"""Convert Aeon Timeline 3 project data to odt. 

Version 0.2.3

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from configparser import ConfigParser

import re

import zipfile
import locale
import tempfile
from shutil import rmtree
from datetime import datetime
from string import Template

from string import Template




class WorldElement():
    """Story world element representation.
    # xml: <LOCATIONS><LOCATION> or # xml: <ITEMS><ITEM>
    """

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>


class Character(WorldElement):
    """yWriter character representation.
    # xml: <CHARACTERS><CHARACTER>
    """

    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        WorldElement.__init__(self)

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None
        # bool
        # xml: <Major>


class Scene():
    """yWriter scene representation.
    # xml: <SCENES><SCENE>
    """

    # Emulate an enumeration for the scene status

    STATUS = [None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']
    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int # xml: <Status>

        self.sceneNotes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

        self.image = None
        # str
        # xml: <ImageFile>

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('\[.+?\]|\.|\,| -', '', self._sceneContent)
        # Remove yWriter raw markup for word count

        wordList = text.split()
        self.wordCount = len(wordList)

        text = re.sub('\[.+?\]', '', self._sceneContent)
        # Remove yWriter raw markup for letter count

        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)
from urllib.parse import quote
from shutil import copy2


class Novel():
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods: 
        read() -- Parse the file and store selected properties.
        merge(novel) -- Copy required attributes of the novel object.
        write() -- Write selected properties to the file.
        convert_to_yw(text) -- Return text, converted from source format to yw7 markup.
        convert_from_yw(text) -- Return text, converted from yw7 markup to target format.
        file_exists() -- Return True, if the file specified by filePath exists.

    Instance variables:
        title -- str; title
        desc -- str; description
        author -- str; author name
        fieldTitle1 -- str; field title 1
        fieldTitle2 -- str; field title 2
        fieldTitle3 -- str; field title 3
        fieldTitle4 -- str; field title 4
        chapters -- dict; key = chapter ID, value = Chapter instance.
        scenes -- dict; key = scene ID, value = Scene instance.
        srtChapters -- list of str; The novel's sorted chapter IDs. 
        locations -- dict; key = location ID, value = WorldElement instance.
        srtLocations -- list of str; The novel's sorted location IDs. 
        items -- dict; key = item ID, value = WorldElement instance.
        srtItems -- list of str; The novel's sorted item IDs. 
        characters -- dict; key = character ID, value = Character instance.
        srtCharacters -- list of str The novel's sorted character IDs.
        filePath -- str; path to the file represented by the class.   
    """

    DESCRIPTION = 'Novel'
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    def __init__(self, filePath, **kwargs):
        """Define instance variables.

        Positional argument:
            filePath -- string; path to the file represented by the class.
        """
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.author = None
        # str
        # xml: <PROJECT><AuthorName>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's
        # order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's
        # order of the scenes is defined by the order of the chapters
        # and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements
        # corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements
        # corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements
        # corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a
        # supported type as specified by EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.        
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """

        if self.SUFFIX is not None:
            suffix = self.SUFFIX

        else:
            suffix = ''

        if filePath.lower().endswith((suffix + self.EXTENSION).lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(
                suffix + self.EXTENSION, ''))

    def read(self):
        """Parse the file and store selected properties.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: read method is not implemented.'

    def merge(self, source):
        """Copy required attributes of the source object.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: merge method is not implemented.'

    def write(self):
        """Write selected properties to the file.
        Return a message beginning with SUCCESS or ERROR.
        This is a stub to be overridden by subclass methods.
        """
        return 'ERROR: write method is not implemented.'

    def convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        This is a stub to be overridden by subclass methods.
        """
        return text

    def convert_from_yw(self, text):
        """Return text, converted from yw7 markup to target format.
        This is a stub to be overridden by subclass methods.
        """
        return text

    def file_exists(self):
        """Return True, if the file specified by filePath exists. 
        Otherwise, return False.
        """
        if os.path.isfile(self.filePath):
            return True

        else:
            return False

    def back_up(self, single=True):
        """Create a backup file from filePath. Return True, if successful.
        Otherwise, return False.

        Parameter: single
        True - Overwrite existing backup file. Extension = .bak
        False - Create a new, numbered backup file. Extension = .bkxxxx
        """
        if os.path.isfile(self.filePath):

            if single:
                backupFile = self.filePath + '.bak'

            else:
                i = 0
                backupFile = self.filePath + '.bk0000'

                while os.path.isfile(backupFile):
                    i += 1
                    backupFile = self.filePath + '.bk' + str(i).zfill(4)

            try:
                copy2(self.filePath, backupFile)
                return True

            except:
                return False

        else:
            return False


class Filter():
    """Strategy class, implementing filtering criteria 
    for template-based export.
    """

    def accept(self, source, id):
        """Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods
        implementing filters.
        """
        return True


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''

    fileHeader = ''
    partTemplate = ''
    chapterTemplate = ''
    notesChapterTemplate = ''
    todoChapterTemplate = ''
    unusedChapterTemplate = ''
    notExportedChapterTemplate = ''
    sceneTemplate = ''
    firstSceneTemplate = ''
    appendedSceneTemplate = ''
    notesSceneTemplate = ''
    todoSceneTemplate = ''
    unusedSceneTemplate = ''
    notExportedSceneTemplate = ''
    sceneDivider = ''
    chapterEndTemplate = ''
    unusedChapterEndTemplate = ''
    notExportedChapterEndTemplate = ''
    notesChapterEndTemplate = ''
    characterTemplate = ''
    locationTemplate = ''
    itemTemplate = ''
    fileFooter = ''

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        initializing a filter class.
        """
        Novel.__init__(self, filePath, **kwargs)
        self.sceneFilter = Filter()
        self.chapterFilter = Filter()
        self.characterFilter = Filter()
        self.locationFilter = Filter()
        self.itemFilter = Filter()

    def merge(self, source):
        """Copy required attributes of the source object.
        Return a message beginning with SUCCESS or ERROR.
        """

        if source.title is not None:
            self.title = source.title

        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc

        else:
            self.desc = ''

        if source.author is not None:
            self.author = source.author

        else:
            self.author = ''

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1

        else:
            self.fieldTitle1 = 'Field 1'

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2

        else:
            self.fieldTitle2 = 'Field 2'

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3

        else:
            self.fieldTitle3 = 'Field 3'

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4

        else:
            self.fieldTitle4 = 'Field 4'

        if source.srtChapters != []:
            self.srtChapters = source.srtChapters

        if source.scenes is not None:
            self.scenes = source.scenes

        if source.chapters is not None:
            self.chapters = source.chapters

        if source.srtCharacters != []:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters

        if source.srtLocations != []:
            self.srtLocations = source.srtLocations
            self.locations = source.locations

        if source.srtItems != []:
            self.srtItems = source.srtItems
            self.items = source.items

        return 'SUCCESS'

    def get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section. 
        """
        projectTemplateMapping = dict(
            Title=self.title,
            Desc=self.convert_from_yw(self.desc),
            AuthorName=self.author,
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
        )
        return projectTemplateMapping

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self.chapters[chId].get_title(),
            Desc=self.convert_from_yw(self.chapters[chId].desc),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section. 
        """
        # Create a comma separated tag list.

        if sceneNumber == 0:
            sceneNumber = ''

        if self.scenes[scId].tags is not None:
            tags = self.get_string(self.scenes[scId].tags)

        else:
            tags = ''

        # Create a comma separated character list.

        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters

            sChList = []

            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)

            sceneChars = self.get_string(sChList)
            viewpointChar = sChList[0]

        except:
            sceneChars = ''
            viewpointChar = ''

        # Create a comma separated location list.

        if self.scenes[scId].locations is not None:
            sLcList = []

            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)

            sceneLocs = self.get_string(sLcList)

        else:
            sceneLocs = ''

        # Create a comma separated item list.

        if self.scenes[scId].items is not None:
            sItList = []

            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)

            sceneItems = self.get_string(sItList)

        else:
            sceneItems = ''

        # Create A/R marker string.

        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER

        else:
            reactionScene = Scene.ACTION_MARKER

        # Create a combined date information.

        if self.scenes[scId].date is not None:
            day = ''
            date = self.scenes[scId].date
            scDate = self.scenes[scId].date

        else:
            date = ''

            if self.scenes[scId].day is not None:
                day = self.scenes[scId].day
                scDate = 'Day ' + self.scenes[scId].day

            else:
                day = ''
                scDate = ''

        # Create a combined time information.

        if self.scenes[scId].time is not None:
            hour = ''
            minute = ''
            time = self.scenes[scId].time
            scTime = self.scenes[scId].time.rsplit(':', 1)[0]

        else:
            time = ''

            if self.scenes[scId].hour or self.scenes[scId].minute:

                if self.scenes[scId].hour:
                    hour = self.scenes[scId].hour

                else:
                    hour = '00'

                if self.scenes[scId].minute:
                    minute = self.scenes[scId].minute

                else:
                    minute = '00'

                scTime = hour.zfill(2) + ':' + minute.zfill(2)

            else:
                hour = ''
                minute = ''
                scTime = ''

        # Create a combined duration information.

        if self.scenes[scId].lastsDays is not None:
            lastsDays = self.scenes[scId].lastsDays
            days = self.scenes[scId].lastsDays + 'd '

        else:
            lastsDays = ''
            days = ''

        if self.scenes[scId].lastsHours is not None:
            lastsHours = self.scenes[scId].lastsHours
            hours = self.scenes[scId].lastsHours + 'h '

        else:
            lastsHours = ''
            hours = ''

        if self.scenes[scId].lastsMinutes is not None:
            lastsMinutes = self.scenes[scId].lastsMinutes
            minutes = self.scenes[scId].lastsMinutes + 'min'

        else:
            lastsMinutes = ''
            minutes = ''

        duration = days + hours + minutes

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self.scenes[scId].title,
            Desc=self.convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self.convert_from_yw(self.scenes[scId].sceneContent),
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=date,
            Time=time,
            Day=day,
            Hour=hour,
            Minute=minute,
            ScDate=scDate,
            ScTime=scTime,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self.convert_from_yw(self.scenes[scId].goal),
            Conflict=self.convert_from_yw(self.scenes[scId].conflict),
            Outcome=self.convert_from_yw(self.scenes[scId].outcome),
            Tags=tags,
            Image=self.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self.convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )

        return sceneMapping

    def get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        """

        if self.characters[crId].tags is not None:
            tags = self.get_string(self.characters[crId].tags)

        else:
            tags = ''

        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER

        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self.characters[crId].title,
            Desc=self.convert_from_yw(self.characters[crId].desc),
            Tags=tags,
            Image=self.characters[crId].image,
            AKA=FileExport.convert_from_yw(self, self.characters[crId].aka),
            Notes=self.convert_from_yw(self.characters[crId].notes),
            Bio=self.convert_from_yw(self.characters[crId].bio),
            Goals=self.convert_from_yw(self.characters[crId].goals),
            FullName=FileExport.convert_from_yw(
                self, self.characters[crId].fullName),
            Status=characterStatus,
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        """

        if self.locations[lcId].tags is not None:
            tags = self.get_string(self.locations[lcId].tags)

        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self.locations[lcId].title,
            Desc=self.convert_from_yw(self.locations[lcId].desc),
            Tags=tags,
            Image=self.locations[lcId].image,
            AKA=FileExport.convert_from_yw(self, self.locations[lcId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section. 
        """

        if self.items[itId].tags is not None:
            tags = self.get_string(self.items[itId].tags)

        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self.items[itId].title,
            Desc=self.convert_from_yw(self.items[itId].desc),
            Tags=tags,
            Image=self.items[itId].image,
            AKA=FileExport.convert_from_yw(self, self.items[itId].aka),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def get_fileHeader(self):
        """Process the file header.
        Return a list of strings.
        """
        lines = []
        template = Template(self.fileHeader)
        lines.append(template.safe_substitute(
            self.get_fileHeaderMapping()))
        return lines

    def get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        Return a list of strings.
        """
        lines = []
        firstSceneInChapter = True

        for scId in self.chapters[chId].srtScenes:
            dispNumber = 0

            if not self.sceneFilter.accept(self, scId):
                continue

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.

            if self.scenes[scId].isTodoScene:

                if self.todoSceneTemplate != '':
                    template = Template(self.todoSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isNotesScene:
                # Scene is "Notes" type.

                if self.notesSceneTemplate != '':
                    template = Template(self.notesSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].isUnused or self.chapters[chId].isUnused:

                if self.unusedSceneTemplate != '':
                    template = Template(self.unusedSceneTemplate)

                else:
                    continue

            elif self.chapters[chId].oldType == 1:
                # Scene is "Info" type (old file format).

                if self.notesSceneTemplate != '':
                    template = Template(self.notesSceneTemplate)

                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:

                if self.notExportedSceneTemplate != '':
                    template = Template(self.notExportedSceneTemplate)

                else:
                    continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount

                template = Template(self.sceneTemplate)

                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self.appendedSceneTemplate != '':
                    template = Template(self.appendedSceneTemplate)

            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self.sceneDivider)

            if firstSceneInChapter and self.firstSceneTemplate != '':
                template = Template(self.firstSceneTemplate)

            lines.append(template.safe_substitute(self.get_sceneMapping(
                scId, dispNumber, wordsTotal, lettersTotal)))

            firstSceneInChapter = False

        return lines, sceneNumber, wordsTotal, lettersTotal

    def get_chapters(self):
        """Process the chapters and nested scenes.
        Return a list of strings.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0

        for chId in self.srtChapters:
            dispNumber = 0

            if not self.chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.

            # Has the chapter only scenes not to be exported?

            sceneCount = 0
            notExportCount = 0
            doNotExport = False
            template = None

            for scId in self.chapters[chId].srtScenes:
                sceneCount += 1

                if self.scenes[scId].doNotExport:
                    notExportCount += 1

            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True

            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type (implies "unused").

                if self.todoChapterTemplate != '':
                    template = Template(self.todoChapterTemplate)

            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type (implies "unused").

                if self.notesChapterTemplate != '':
                    template = Template(self.notesChapterTemplate)

            elif self.chapters[chId].isUnused:
                # Chapter is "really" unused.

                if self.unusedChapterTemplate != '':
                    template = Template(self.unusedChapterTemplate)

            elif self.chapters[chId].oldType == 1:
                # Chapter is "Info" type (old file format).

                if self.notesChapterTemplate != '':
                    template = Template(self.notesChapterTemplate)

            elif doNotExport:

                if self.notExportedChapterTemplate != '':
                    template = Template(self.notExportedChapterTemplate)

            elif self.chapters[chId].chLevel == 1 and self.partTemplate != '':
                template = Template(self.partTemplate)

            else:
                template = Template(self.chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber

            if template is not None:
                lines.append(template.safe_substitute(
                    self.get_chapterMapping(chId, dispNumber)))

            # Process scenes.

            sceneLines, sceneNumber, wordsTotal, lettersTotal = self.get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            # Process chapter ending.

            template = None

            if self.chapters[chId].chType == 2:

                if self.todoChapterEndTemplate != '':
                    template = Template(self.todoChapterEndTemplate)

            elif self.chapters[chId].chType == 1:

                if self.notesChapterEndTemplate != '':
                    template = Template(self.notesChapterEndTemplate)

            elif self.chapters[chId].isUnused:

                if self.unusedChapterEndTemplate != '':
                    template = Template(self.unusedChapterEndTemplate)

            elif self.chapters[chId].oldType == 1:

                if self.notesChapterEndTemplate != '':
                    template = Template(self.notesChapterEndTemplate)

            elif doNotExport:

                if self.notExportedChapterEndTemplate != '':
                    template = Template(self.notExportedChapterEndTemplate)

            elif self.chapterEndTemplate != '':
                template = Template(self.chapterEndTemplate)

            if template is not None:
                lines.append(template.safe_substitute(
                    self.get_chapterMapping(chId, dispNumber)))

        return lines

    def get_characters(self):
        """Process the characters.
        Return a list of strings.
        """
        lines = []
        template = Template(self.characterTemplate)

        for crId in self.srtCharacters:

            if self.characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(
                    self.get_characterMapping(crId)))

        return lines

    def get_locations(self):
        """Process the locations.
        Return a list of strings.
        """
        lines = []
        template = Template(self.locationTemplate)

        for lcId in self.srtLocations:

            if self.locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(
                    self.get_locationMapping(lcId)))

        return lines

    def get_items(self):
        """Process the items.
        Return a list of strings.
        """
        lines = []
        template = Template(self.itemTemplate)

        for itId in self.srtItems:

            if self.itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(
                    self.get_itemMapping(itId)))

        return lines

    def get_text(self):
        """Assemple the whole text applying the templates.
        Return a string to be written to the output file.
        """
        lines = self.get_fileHeader()
        lines.extend(self.get_chapters())
        lines.extend(self.get_characters())
        lines.extend(self.get_locations())
        lines.extend(self.get_items())
        lines.append(self.fileFooter)
        return ''.join(lines)

    def write(self):
        """Create a template-based output file. 
        Return a message string starting with 'SUCCESS' or 'ERROR'.
        """
        text = self.get_text()

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Cannot write "' + os.path.normpath(self.filePath) + '".'

        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'

    def get_string(self, elements):
        """Return a string which is the concatenation of the 
        members of the list of strings "elements", separated by 
        a comma plus a space. The space allows word wrap in 
        spreadsheet cells.
        """
        text = (', ').join(elements)
        return text

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        This is a stub to be overridden by subclass methods.
        """

        if text is None:
            text = ''

        return(text)


class OdfFile(FileExport):
    """Generic OpenDocument xml file representation.
    """

    ODF_COMPONENTS = []
    _MIMETYPE = ''
    _SETTINGS_XML = ''
    _MANIFEST_XML = ''
    _STYLES_XML = ''
    _META_XML = ''

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor, 
        creating a temporary directory.
        """
        FileExport.__init__(self, filePath, **kwargs)
        self.tempDir = tempfile.mkdtemp(suffix='.tmp', prefix='odf_')
        self.originalPath = self._filePath

    def __del__(self):
        """Make sure to delete the temporary directory,
        in case write() has not been called.
        """
        self.tear_down()

    def tear_down(self):
        """Delete the temporary directory 
        containing the unpacked ODF directory structure.
        """
        try:
            rmtree(self.tempDir)
        except:
            pass

    def set_up(self):
        """Helper method for ZIP file generation.

        Prepare the temporary directory containing the internal 
        structure of an ODF file except 'content.xml'.
        """
        # Create and open a temporary directory for the files to zip.

        try:
            self.tear_down()
            os.mkdir(self.tempDir)
            os.mkdir(self.tempDir + '/META-INF')

        except:
            return 'ERROR: Cannot create "' + os.path.normpath(self.tempDir) + '".'

        # Generate mimetype.

        try:
            with open(self.tempDir + '/mimetype', 'w', encoding='utf-8') as f:
                f.write(self._MIMETYPE)
        except:
            return 'ERROR: Cannot write "mimetype"'

        # Generate settings.xml.

        try:
            with open(self.tempDir + '/settings.xml', 'w', encoding='utf-8') as f:
                f.write(self._SETTINGS_XML)
        except:
            return 'ERROR: Cannot write "settings.xml"'

        # Generate META-INF\manifest.xml.

        try:
            with open(self.tempDir + '/META-INF/manifest.xml', 'w', encoding='utf-8') as f:
                f.write(self._MANIFEST_XML)
        except:
            return 'ERROR: Cannot write "manifest.xml"'

        # Generate styles.xml with system language set as document language.

        localeCodes = locale.getdefaultlocale()[0].split('_')

        localeMapping = dict(
            Language=localeCodes[0],
            Country=localeCodes[1],
        )
        template = Template(self._STYLES_XML)
        text = template.safe_substitute(localeMapping)

        try:
            with open(self.tempDir + '/styles.xml', 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            return 'ERROR: Cannot write "styles.xml"'

        # Generate meta.xml with actual document metadata.

        dt = datetime.today()

        metaMapping = dict(
            Author=self.author,
            Title=self.title,
            Summary='<![CDATA[' + self.desc + ']]>',
            Date=str(dt.year) + '-' + str(dt.month).rjust(2, '0') +
            '-' + str(dt.day).rjust(2, '0'),
            Time=str(dt.hour).rjust(2, '0') +
            ':' + str(dt.minute).rjust(2, '0') +
            ':' + str(dt.second).rjust(2, '0'),
        )
        template = Template(self._META_XML)
        text = template.safe_substitute(metaMapping)

        try:
            with open(self.tempDir + '/meta.xml', 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            return 'ERROR: Cannot write "meta.xml".'

        return 'SUCCESS: ODF structure generated.'

    def write(self):
        """Extend the super class method, adding ZIP file operations."""

        # Create a temporary directory containing the internal
        # structure of an ODS file except "content.xml".

        message = self.set_up()

        if message.startswith('ERROR'):
            return message

        # Add "content.xml" to the temporary directory.

        self.originalPath = self._filePath

        self._filePath = self.tempDir + '/content.xml'

        message = FileExport.write(self)

        self._filePath = self.originalPath

        if message.startswith('ERROR'):
            return message

        # Pack the contents of the temporary directory
        # into the ODF file.

        workdir = os.getcwd()

        try:
            with zipfile.ZipFile(self.filePath, 'w') as odfTarget:
                os.chdir(self.tempDir)

                for file in self.ODF_COMPONENTS:
                    odfTarget.write(file, compress_type=zipfile.ZIP_DEFLATED)
        except:
            os.chdir(workdir)
            return 'ERROR: Cannot generate "' + os.path.normpath(self.filePath) + '".'

        # Remove temporary data.

        os.chdir(workdir)
        self.tear_down()
        return 'SUCCESS: "' + os.path.normpath(self.filePath) + '" written.'


class OdtFile(OdfFile):
    """Generic OpenDocument text document representation."""

    EXTENSION = '.odt'
    # overwrites Novel.EXTENSION

    ODF_COMPONENTS = ['manifest.rdf', 'META-INF', 'content.xml', 'meta.xml', 'mimetype',
                      'settings.xml', 'styles.xml', 'META-INF/manifest.xml']

    CONTENT_XML_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>

<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" office:version="1.2">
 <office:scripts/>
 <office:font-face-decls>
  <style:font-face style:name="StarSymbol" svg:font-family="StarSymbol" style:font-charset="x-symbol"/>
  <style:font-face style:name="Courier New" svg:font-family="&apos;Courier New&apos;" style:font-adornments="Standard" style:font-family-generic="modern" style:font-pitch="fixed"/>
   </office:font-face-decls>
 <office:automatic-styles>
  <style:style style:name="Sect1" style:family="section">
   <style:section-properties style:editable="false">
    <style:columns fo:column-count="1" fo:column-gap="0cm"/>
   </style:section-properties>
  </style:style>
 </office:automatic-styles>
 <office:body>
  <office:text text:use-soft-page-breaks="true">

'''

    CONTENT_XML_FOOTER = '''  </office:text>
 </office:body>
</office:document-content>
'''

    _META_XML = '''<?xml version="1.0" encoding="utf-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:grddl="http://www.w3.org/2003/g/data-view#" office:version="1.2">
  <office:meta>
    <meta:generator>PyWriter</meta:generator>
    <dc:title>$Title</dc:title>
    <dc:description>$Summary</dc:description>
    <dc:subject></dc:subject>
    <meta:keyword></meta:keyword>
    <meta:initial-creator>$Author</meta:initial-creator>
    <dc:creator></dc:creator>
    <meta:creation-date>${Date}T${Time}Z</meta:creation-date>
    <dc:date></dc:date>
  </office:meta>
</office:document-meta>
'''
    _MANIFEST_XML = '''<?xml version="1.0" encoding="utf-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/" />
  <manifest:file-entry manifest:media-type="application/xml" manifest:full-path="content.xml" manifest:version="1.2" />
  <manifest:file-entry manifest:media-type="application/rdf+xml" manifest:full-path="manifest.rdf" manifest:version="1.2" />
  <manifest:file-entry manifest:media-type="application/xml" manifest:full-path="styles.xml" manifest:version="1.2" />
  <manifest:file-entry manifest:media-type="application/xml" manifest:full-path="meta.xml" manifest:version="1.2" />
  <manifest:file-entry manifest:media-type="application/xml" manifest:full-path="settings.xml" manifest:version="1.2" />
</manifest:manifest>    
'''
    _MANIFEST_RDF = '''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="styles.xml">
    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/1.2/meta/odf#StylesFile"/>
  </rdf:Description>
  <rdf:Description rdf:about="">
    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#" rdf:resource="styles.xml"/>
  </rdf:Description>
  <rdf:Description rdf:about="content.xml">
    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/1.2/meta/odf#ContentFile"/>
  </rdf:Description>
  <rdf:Description rdf:about="">
    <ns0:hasPart xmlns:ns0="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#" rdf:resource="content.xml"/>
  </rdf:Description>
  <rdf:Description rdf:about="">
    <rdf:type rdf:resource="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#Document"/>
  </rdf:Description>
</rdf:RDF>
'''
    _SETTINGS_XML = '''<?xml version="1.0" encoding="UTF-8"?>

<office:document-settings xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" xmlns:ooo="http://openoffice.org/2004/office" office:version="1.2">
 <office:settings>
  <config:config-item-set config:name="ooo:view-settings">
   <config:config-item config:name="ViewAreaTop" config:type="int">0</config:config-item>
   <config:config-item config:name="ViewAreaLeft" config:type="int">0</config:config-item>
   <config:config-item config:name="ViewAreaWidth" config:type="int">30508</config:config-item>
   <config:config-item config:name="ViewAreaHeight" config:type="int">27783</config:config-item>
   <config:config-item config:name="ShowRedlineChanges" config:type="boolean">true</config:config-item>
   <config:config-item config:name="InBrowseMode" config:type="boolean">false</config:config-item>
   <config:config-item-map-indexed config:name="Views">
    <config:config-item-map-entry>
     <config:config-item config:name="ViewId" config:type="string">view2</config:config-item>
     <config:config-item config:name="ViewLeft" config:type="int">8079</config:config-item>
     <config:config-item config:name="ViewTop" config:type="int">3501</config:config-item>
     <config:config-item config:name="VisibleLeft" config:type="int">0</config:config-item>
     <config:config-item config:name="VisibleTop" config:type="int">0</config:config-item>
     <config:config-item config:name="VisibleRight" config:type="int">30506</config:config-item>
     <config:config-item config:name="VisibleBottom" config:type="int">27781</config:config-item>
     <config:config-item config:name="ZoomType" config:type="short">0</config:config-item>
     <config:config-item config:name="ViewLayoutColumns" config:type="short">0</config:config-item>
     <config:config-item config:name="ViewLayoutBookMode" config:type="boolean">false</config:config-item>
     <config:config-item config:name="ZoomFactor" config:type="short">100</config:config-item>
     <config:config-item config:name="IsSelectedFrame" config:type="boolean">false</config:config-item>
    </config:config-item-map-entry>
   </config:config-item-map-indexed>
  </config:config-item-set>
  <config:config-item-set config:name="ooo:configuration-settings">
   <config:config-item config:name="AddParaSpacingToTableCells" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrintPaperFromSetup" config:type="boolean">false</config:config-item>
   <config:config-item config:name="IsKernAsianPunctuation" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintReversed" config:type="boolean">false</config:config-item>
   <config:config-item config:name="LinkUpdateMode" config:type="short">1</config:config-item>
   <config:config-item config:name="DoNotCaptureDrawObjsOnPage" config:type="boolean">false</config:config-item>
   <config:config-item config:name="SaveVersionOnClose" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintEmptyPages" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrintSingleJobs" config:type="boolean">false</config:config-item>
   <config:config-item config:name="AllowPrintJobCancel" config:type="boolean">true</config:config-item>
   <config:config-item config:name="AddFrameOffsets" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintLeftPages" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrintTables" config:type="boolean">true</config:config-item>
   <config:config-item config:name="ProtectForm" config:type="boolean">false</config:config-item>
   <config:config-item config:name="ChartAutoUpdate" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrintControls" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrinterSetup" config:type="base64Binary">8gT+/0hQIExhc2VySmV0IFAyMDE0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASFAgTGFzZXJKZXQgUDIwMTQAAAAAAAAAAAAAAAAAAAAWAAEAGAQAAAAAAAAEAAhSAAAEdAAAM1ROVwIACABIAFAAIABMAGEAcwBlAHIASgBlAHQAIABQADIAMAAxADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQQDANwANAMPnwAAAQAJAJoLNAgAAAEABwBYAgEAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU0RETQAGAAAABgAASFAgTGFzZXJKZXQgUDIwMTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAEAAAAJAAAACQAAAAkAAAAJAAAACQAAAAkAAAAJAAAACQAAAAkAAAAJAAAACQAAAAkAAAAJAAAACQAAAAkAAAAJAAAACQAAAAAAAAABAAAAAQAAABoEAAAAAAAAAAAAAAAAAAAPAAAALQAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAgICAAP8AAAD//wAAAP8AAAD//wAAAP8A/wD/AAAAAAAAAAAAAAAAAAAAAAAoAAAAZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeAwAA3gMAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABrjvBgNAMAAAAAAAAAAAAABIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAQ09NUEFUX0RVUExFWF9NT0RFCgBEVVBMRVhfT0ZG</config:config-item>
   <config:config-item config:name="CurrentDatabaseDataSource" config:type="string"/>
   <config:config-item config:name="LoadReadonly" config:type="boolean">false</config:config-item>
   <config:config-item config:name="CurrentDatabaseCommand" config:type="string"/>
   <config:config-item config:name="ConsiderTextWrapOnObjPos" config:type="boolean">false</config:config-item>
   <config:config-item config:name="ApplyUserData" config:type="boolean">true</config:config-item>
   <config:config-item config:name="AddParaTableSpacing" config:type="boolean">true</config:config-item>
   <config:config-item config:name="FieldAutoUpdate" config:type="boolean">true</config:config-item>
   <config:config-item config:name="IgnoreFirstLineIndentInNumbering" config:type="boolean">false</config:config-item>
   <config:config-item config:name="TabsRelativeToIndent" config:type="boolean">true</config:config-item>
   <config:config-item config:name="IgnoreTabsAndBlanksForLineCalculation" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintAnnotationMode" config:type="short">0</config:config-item>
   <config:config-item config:name="AddParaTableSpacingAtStart" config:type="boolean">true</config:config-item>
   <config:config-item config:name="UseOldPrinterMetrics" config:type="boolean">false</config:config-item>
   <config:config-item config:name="TableRowKeep" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrinterName" config:type="string">HP LaserJet P2014</config:config-item>
   <config:config-item config:name="PrintFaxName" config:type="string"/>
   <config:config-item config:name="UnxForceZeroExtLeading" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintTextPlaceholder" config:type="boolean">false</config:config-item>
   <config:config-item config:name="DoNotJustifyLinesWithManualBreak" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintRightPages" config:type="boolean">true</config:config-item>
   <config:config-item config:name="CharacterCompressionType" config:type="short">0</config:config-item>
   <config:config-item config:name="UseFormerTextWrapping" config:type="boolean">false</config:config-item>
   <config:config-item config:name="IsLabelDocument" config:type="boolean">false</config:config-item>
   <config:config-item config:name="AlignTabStopPosition" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrintHiddenText" config:type="boolean">false</config:config-item>
   <config:config-item config:name="DoNotResetParaAttrsForNumFont" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintPageBackground" config:type="boolean">true</config:config-item>
   <config:config-item config:name="CurrentDatabaseCommandType" config:type="int">0</config:config-item>
   <config:config-item config:name="OutlineLevelYieldsNumbering" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintProspect" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintGraphics" config:type="boolean">true</config:config-item>
   <config:config-item config:name="SaveGlobalDocumentLinks" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintProspectRTL" config:type="boolean">false</config:config-item>
   <config:config-item config:name="UseFormerLineSpacing" config:type="boolean">false</config:config-item>
   <config:config-item config:name="AddExternalLeading" config:type="boolean">true</config:config-item>
   <config:config-item config:name="UseFormerObjectPositioning" config:type="boolean">false</config:config-item>
   <config:config-item config:name="RedlineProtectionKey" config:type="base64Binary"/>
   <config:config-item config:name="MathBaselineAlignment" config:type="boolean">false</config:config-item>
   <config:config-item config:name="ClipAsCharacterAnchoredWriterFlyFrames" config:type="boolean">false</config:config-item>
   <config:config-item config:name="UseOldNumbering" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintDrawings" config:type="boolean">true</config:config-item>
   <config:config-item config:name="PrinterIndependentLayout" config:type="string">disabled</config:config-item>
   <config:config-item config:name="TabAtLeftIndentForParagraphsInList" config:type="boolean">false</config:config-item>
   <config:config-item config:name="PrintBlackFonts" config:type="boolean">false</config:config-item>
   <config:config-item config:name="UpdateFromTemplate" config:type="boolean">true</config:config-item>
  </config:config-item-set>
 </office:settings>
</office:document-settings>
'''
    _STYLES_XML = '''<?xml version="1.0" encoding="UTF-8"?>

<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0">
 <office:font-face-decls>
  <style:font-face style:name="StarSymbol" svg:font-family="StarSymbol" style:font-charset="x-symbol"/>
  <style:font-face style:name="Segoe UI" svg:font-family="&apos;Segoe UI&apos;"/>
  <style:font-face style:name="Courier New" svg:font-family="&apos;Courier New&apos;" style:font-adornments="Standard" style:font-family-generic="modern" style:font-pitch="fixed"/>
  <style:font-face style:name="Cumberland" svg:font-family="Cumberland" style:font-family-generic="modern" style:font-pitch="fixed"/>
  <style:font-face style:name="Courier New1" svg:font-family="&apos;Courier New&apos;" style:font-family-generic="roman" style:font-pitch="fixed"/>
  <style:font-face style:name="ITC Officina Sans Book" svg:font-family="&apos;ITC Officina Sans Book&apos;" style:font-family-generic="swiss" style:font-pitch="variable"/>
 </office:font-face-decls>
 <office:styles>
  <style:default-style style:family="graphic">
   <style:graphic-properties svg:stroke-color="#3465a4" draw:fill-color="#729fcf" fo:wrap-option="no-wrap" draw:shadow-offset-x="0.3cm" draw:shadow-offset-y="0.3cm" draw:start-line-spacing-horizontal="0.283cm" draw:start-line-spacing-vertical="0.283cm" draw:end-line-spacing-horizontal="0.283cm" draw:end-line-spacing-vertical="0.283cm" style:flow-with-text="true"/>
   <style:paragraph-properties style:text-autospace="ideograph-alpha" style:line-break="strict" style:writing-mode="lr-tb" style:font-independent-line-spacing="false">
    <style:tab-stops/>
   </style:paragraph-properties>
   <style:text-properties fo:color="#000000" fo:font-size="10pt" fo:language="${Language}" fo:country="${Country}" style:font-size-asian="10pt" style:language-asian="zxx" style:country-asian="none" style:font-size-complex="1pt" style:language-complex="zxx" style:country-complex="none"/>
  </style:default-style>
  <style:default-style style:family="paragraph">
   <style:paragraph-properties fo:hyphenation-ladder-count="no-limit" style:text-autospace="ideograph-alpha" style:punctuation-wrap="hanging" style:line-break="strict" style:tab-stop-distance="1.251cm" style:writing-mode="lr-tb"/>
   <style:text-properties fo:color="#000000" style:font-name="Segoe UI" fo:font-size="10pt" fo:language="${Language}" fo:country="${Country}" style:font-name-asian="Segoe UI" style:font-size-asian="10pt" style:language-asian="zxx" style:country-asian="none" style:font-name-complex="Segoe UI" style:font-size-complex="1pt" style:language-complex="zxx" style:country-complex="none" fo:hyphenate="false" fo:hyphenation-remain-char-count="2" fo:hyphenation-push-char-count="2"/>
  </style:default-style>
  <style:default-style style:family="table">
   <style:table-properties table:border-model="separating"/>
  </style:default-style>
  <style:default-style style:family="table-row">
   <style:table-row-properties fo:keep-together="always"/>
  </style:default-style>
  <style:style style:name="Standard" style:family="paragraph" style:class="text" style:master-page-name="">
   <style:paragraph-properties fo:line-height="0.73cm" style:page-number="auto"/>
   <style:text-properties style:font-name="Courier New" fo:font-size="12pt" fo:font-weight="normal"/>
  </style:style>
  <style:style style:name="Text_20_body" style:display-name="Text body" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="First_20_line_20_indent" style:class="text" style:master-page-name="">
   <style:paragraph-properties style:page-number="auto">
    <style:tab-stops/>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="First_20_line_20_indent" style:display-name="First line indent" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="text" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0.499cm" style:auto-text-indent="false" style:page-number="auto"/>
  </style:style>
  <style:style style:name="Hanging_20_indent" style:display-name="Hanging indent" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="text">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="-0.499cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="0cm"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Text_20_body_20_indent" style:display-name="Text body indent" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="text">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Salutation" style:family="paragraph" style:parent-style-name="Standard" style:class="text"/>
  <style:style style:name="Signature" style:family="paragraph" style:parent-style-name="Standard" style:class="text"/>
  <style:style style:name="List_20_Indent" style:display-name="List Indent" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="text">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="5.001cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="-4.5cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="0cm"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Marginalia" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="text">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="4.001cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Heading" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Text_20_body" style:class="text" style:master-page-name="">
   <style:paragraph-properties fo:line-height="0.73cm" fo:text-align="center" style:justify-single-word="false" style:page-number="auto" fo:keep-with-next="always">
    <style:tab-stops/>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Heading_20_1" style:display-name="Heading 1" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="1" style:list-style-name="" style:class="text" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="1.461cm" fo:margin-bottom="0.73cm" style:page-number="auto">
    <style:tab-stops/>
   </style:paragraph-properties>
   <style:text-properties fo:text-transform="uppercase" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Heading_20_2" style:display-name="Heading 2" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="2" style:list-style-name="" style:class="text" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="1.461cm" fo:margin-bottom="0.73cm" style:page-number="auto"/>
   <style:text-properties fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Heading_20_3" style:display-name="Heading 3" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="3" style:list-style-name="" style:class="text" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0.73cm" fo:margin-bottom="0.73cm" style:page-number="auto"/>
   <style:text-properties fo:font-style="italic"/>
  </style:style>
  <style:style style:name="Heading_20_4" style:display-name="Heading 4" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text" style:master-page-name="">
   <style:paragraph-properties fo:margin-top="0.73cm" fo:margin-bottom="0.73cm" style:page-number="auto"/>
  </style:style>
  <style:style style:name="Heading_20_5" style:display-name="Heading 5" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text" style:master-page-name="">
   <style:paragraph-properties style:page-number="auto"/>
  </style:style>
  <style:style style:name="Heading_20_6" style:display-name="Heading 6" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text"/>
  <style:style style:name="Heading_20_7" style:display-name="Heading 7" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text"/>
  <style:style style:name="Heading_20_8" style:display-name="Heading 8" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text"/>
  <style:style style:name="Heading_20_9" style:display-name="Heading 9" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="" style:list-style-name="" style:class="text"/>
  <style:style style:name="Heading_20_10" style:display-name="Heading 10" style:family="paragraph" style:parent-style-name="Heading" style:next-style-name="Text_20_body" style:default-outline-level="10" style:list-style-name="" style:class="text">
   <style:text-properties fo:font-size="75%" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="List" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="list"/>
  <style:style style:name="Numbering_20_1_20_Start" style:display-name="Numbering 1 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_1" style:display-name="Numbering 1" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_1_20_End" style:display-name="Numbering 1 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_1_20_Cont." style:display-name="Numbering 1 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_2_20_Start" style:display-name="Numbering 2 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_2" style:display-name="Numbering 2" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_2_20_End" style:display-name="Numbering 2 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_2_20_Cont." style:display-name="Numbering 2 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_3_20_Start" style:display-name="Numbering 3 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_3" style:display-name="Numbering 3" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_3_20_End" style:display-name="Numbering 3 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_3_20_Cont." style:display-name="Numbering 3 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_4_20_Start" style:display-name="Numbering 4 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_4" style:display-name="Numbering 4" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_4_20_End" style:display-name="Numbering 4 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_4_20_Cont." style:display-name="Numbering 4 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_5_20_Start" style:display-name="Numbering 5 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_5" style:display-name="Numbering 5" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_5_20_End" style:display-name="Numbering 5 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Numbering_20_5_20_Cont." style:display-name="Numbering 5 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_1_20_Start" style:display-name="List 1 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_1" style:display-name="List 1" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_1_20_End" style:display-name="List 1 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_1_20_Cont." style:display-name="List 1 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_2_20_Start" style:display-name="List 2 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_2" style:display-name="List 2" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_2_20_End" style:display-name="List 2 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_2_20_Cont." style:display-name="List 2 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_3_20_Start" style:display-name="List 3 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_3" style:display-name="List 3" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_3_20_End" style:display-name="List 3 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_3_20_Cont." style:display-name="List 3 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_4_20_Start" style:display-name="List 4 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_4" style:display-name="List 4" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_4_20_End" style:display-name="List 4 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_4_20_Cont." style:display-name="List 4 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_5_20_Start" style:display-name="List 5 Start" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_5" style:display-name="List 5" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_5_20_End" style:display-name="List 5 End" style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.423cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_5_20_Cont." style:display-name="List 5 Cont." style:family="paragraph" style:parent-style-name="List" style:class="list">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0.212cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Header_20_and_20_Footer" style:display-name="Header and Footer" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties text:number-lines="false" text:line-number="0">
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Header" style:family="paragraph" style:parent-style-name="Standard" style:class="extra" style:master-page-name="">
   <style:paragraph-properties fo:text-align="end" style:justify-single-word="false" style:page-number="auto" fo:padding="0.049cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000" style:shadow="none">
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
   <style:text-properties fo:font-variant="normal" fo:text-transform="none" fo:font-style="italic"/>
  </style:style>
  <style:style style:name="Header_20_left" style:display-name="Header left" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties>
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Header_20_right" style:display-name="Header right" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties>
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Footer" style:family="paragraph" style:parent-style-name="Standard" style:class="extra" style:master-page-name="">
   <style:paragraph-properties fo:text-align="center" style:justify-single-word="false" style:page-number="auto" text:number-lines="false" text:line-number="0">
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
   <style:text-properties fo:font-size="11pt"/>
  </style:style>
  <style:style style:name="Footer_20_left" style:display-name="Footer left" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties>
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Footer_20_right" style:display-name="Footer right" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties>
    <style:tab-stops>
     <style:tab-stop style:position="8.5cm" style:type="center"/>
     <style:tab-stop style:position="17.002cm" style:type="right"/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Table_20_Contents" style:display-name="Table Contents" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="extra"/>
  <style:style style:name="Table_20_Heading" style:display-name="Table Heading" style:family="paragraph" style:parent-style-name="Table_20_Contents" style:class="extra">
   <style:paragraph-properties fo:text-align="center" style:justify-single-word="false"/>
   <style:text-properties fo:font-style="italic" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Caption" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0.212cm" fo:margin-bottom="0.212cm"/>
  </style:style>
  <style:style style:name="Illustration" style:family="paragraph" style:parent-style-name="Caption" style:class="extra"/>
  <style:style style:name="Table" style:family="paragraph" style:parent-style-name="Caption" style:class="extra"/>
  <style:style style:name="Text" style:family="paragraph" style:parent-style-name="Caption" style:class="extra" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0.21cm" fo:margin-bottom="0.21cm" style:page-number="auto"/>
  </style:style>
  <style:style style:name="Frame_20_contents" style:display-name="Frame contents" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="extra"/>
  <style:style style:name="Footnote" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="-0.499cm" style:auto-text-indent="false"/>
   <style:text-properties fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="Addressee" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0cm" fo:margin-bottom="0.106cm"/>
  </style:style>
  <style:style style:name="Sender" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0cm" fo:margin-bottom="0.106cm" fo:line-height="100%" text:number-lines="false" text:line-number="0"/>
  </style:style>
  <style:style style:name="Endnote" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="-0.499cm" style:auto-text-indent="false" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="Drawing" style:family="paragraph" style:parent-style-name="Caption" style:class="extra"/>
  <style:style style:name="Index" style:family="paragraph" style:parent-style-name="Standard" style:class="index"/>
  <style:style style:name="Index_20_Heading" style:display-name="Index Heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Index_20_1" style:display-name="Index 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Index_20_2" style:display-name="Index 2" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Index_20_3" style:display-name="Index 3" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Index_20_Separator" style:display-name="Index Separator" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="Contents_20_Heading" style:display-name="Contents Heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Contents_20_1" style:display-name="Contents 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="17.002cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_2" style:display-name="Contents 2" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="16.503cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_3" style:display-name="Contents 3" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="16.004cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_4" style:display-name="Contents 4" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="15.505cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_5" style:display-name="Contents 5" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="15.005cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_Heading" style:display-name="User Index Heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="User_20_Index_20_1" style:display-name="User Index 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="17.002cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_2" style:display-name="User Index 2" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="16.503cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_3" style:display-name="User Index 3" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.998cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="16.004cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_4" style:display-name="User Index 4" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.498cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="15.505cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_5" style:display-name="User Index 5" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1.997cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="15.005cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_6" style:display-name="Contents 6" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="11.105cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_7" style:display-name="Contents 7" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.995cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="10.606cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_8" style:display-name="Contents 8" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="3.494cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="10.107cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_9" style:display-name="Contents 9" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="3.993cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="9.608cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Contents_20_10" style:display-name="Contents 10" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="4.493cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="9.109cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Illustration_20_Index_20_Heading" style:display-name="Illustration Index Heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Illustration_20_Index_20_1" style:display-name="Illustration Index 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="13.601cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Object_20_index_20_heading" style:display-name="Object index heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Object_20_index_20_1" style:display-name="Object index 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="13.601cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Table_20_index_20_heading" style:display-name="Table index heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Table_20_index_20_1" style:display-name="Table index 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="13.601cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Bibliography_20_Heading" style:display-name="Bibliography Heading" style:family="paragraph" style:parent-style-name="Heading" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="16pt" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Bibliography_20_1" style:display-name="Bibliography 1" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="13.601cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_6" style:display-name="User Index 6" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.496cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="11.105cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_7" style:display-name="User Index 7" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="2.995cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="10.606cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_8" style:display-name="User Index 8" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="3.494cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="10.107cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_9" style:display-name="User Index 9" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="3.993cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="9.608cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="User_20_Index_20_10" style:display-name="User Index 10" style:family="paragraph" style:parent-style-name="Index" style:class="index">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="4.493cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false">
    <style:tab-stops>
     <style:tab-stop style:position="9.109cm" style:type="right" style:leader-style="dotted" style:leader-text="."/>
    </style:tab-stops>
   </style:paragraph-properties>
  </style:style>
  <style:style style:name="Title" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Subtitle" style:class="chapter" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0.000cm" fo:margin-bottom="0cm" fo:line-height="200%" fo:text-align="center" style:justify-single-word="false" fo:text-indent="0cm" style:auto-text-indent="false" style:page-number="auto" fo:background-color="transparent" fo:padding="0cm" fo:border="none" text:number-lines="false" text:line-number="0">
    <style:tab-stops/>
    <style:background-image/>
   </style:paragraph-properties>
   <style:text-properties fo:text-transform="uppercase" fo:font-weight="normal" style:letter-kerning="false"/>
  </style:style>
  <style:style style:name="Subtitle" style:family="paragraph" style:parent-style-name="Title" style:class="chapter" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0cm" fo:margin-bottom="0cm" style:page-number="auto"/>
   <style:text-properties fo:font-variant="normal" fo:text-transform="none" fo:letter-spacing="normal" fo:font-style="italic" fo:font-weight="normal"/>
  </style:style>
  <style:style style:name="Quotations" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="html" style:master-page-name="">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0.499cm" fo:margin-right="0.499cm" fo:margin-top="0cm" fo:margin-bottom="0.499cm" fo:text-indent="0cm" style:auto-text-indent="false" style:page-number="auto"/>
  </style:style>
  <style:style style:name="Preformatted_20_Text" style:display-name="Preformatted Text" style:family="paragraph" style:parent-style-name="Standard" style:class="html">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0cm" fo:margin-bottom="0cm"/>
  </style:style>
  <style:style style:name="Horizontal_20_Line" style:display-name="Horizontal Line" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Text_20_body" style:class="html">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin-top="0cm" fo:margin-bottom="0.499cm" style:border-line-width-bottom="0.002cm 0.035cm 0.002cm" fo:padding="0cm" fo:border-left="none" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.039cm double #808080" text:number-lines="false" text:line-number="0"/>
   <style:text-properties fo:font-size="6pt"/>
  </style:style>
  <style:style style:name="List_20_Contents" style:display-name="List Contents" style:family="paragraph" style:parent-style-name="Standard" style:class="html">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="1cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="List_20_Heading" style:display-name="List Heading" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="List_20_Contents" style:class="html">
   <style:paragraph-properties loext:contextual-spacing="false" fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:text-indent="0cm" style:auto-text-indent="false"/>
  </style:style>
  <style:style style:name="yWriter_20_mark" style:display-name="yWriter mark" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text">
   <style:text-properties fo:color="#008000" fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="yWriter_20_mark_20_unused" style:display-name="yWriter mark unused" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text">
   <style:text-properties fo:color="#808080" fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="yWriter_20_mark_20_notes" style:display-name="yWriter mark notes" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text">
   <style:text-properties fo:color="#0000FF" fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="yWriter_20_mark_20_todo" style:display-name="yWriter mark todo" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Standard" style:class="text">
   <style:text-properties fo:color="#B22222" fo:font-size="10pt"/>
  </style:style>
  <style:style style:name="Footnote_20_Symbol" style:display-name="Footnote Symbol" style:family="text"/>
  <style:style style:name="Page_20_Number" style:display-name="Page Number" style:family="text">
   <style:text-properties style:font-name="ITC Officina Sans Book" fo:font-size="7pt" fo:letter-spacing="0.071cm" fo:font-weight="bold"/>
  </style:style>
  <style:style style:name="Caption_20_characters" style:display-name="Caption characters" style:family="text"/>
  <style:style style:name="Drop_20_Caps" style:display-name="Drop Caps" style:family="text"/>
  <style:style style:name="Numbering_20_Symbols" style:display-name="Numbering Symbols" style:family="text"/>
  <style:style style:name="Bullet_20_Symbols" style:display-name="Bullet Symbols" style:family="text">
   <style:text-properties style:font-name="StarSymbol" fo:font-size="9pt"/>
  </style:style>
  <style:style style:name="Internet_20_link" style:display-name="Internet link" style:family="text">
   <style:text-properties fo:color="#000080" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
  </style:style>
  <style:style style:name="Visited_20_Internet_20_Link" style:display-name="Visited Internet Link" style:family="text">
   <style:text-properties fo:color="#800000" style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
  </style:style>
  <style:style style:name="Placeholder" style:family="text">
   <style:text-properties fo:font-variant="small-caps" fo:color="#008080" style:text-underline-style="dotted" style:text-underline-width="auto" style:text-underline-color="font-color"/>
  </style:style>
  <style:style style:name="Index_20_Link" style:display-name="Index Link" style:family="text"/>
  <style:style style:name="Endnote_20_Symbol" style:display-name="Endnote Symbol" style:family="text"/>
  <style:style style:name="Line_20_numbering" style:display-name="Line numbering" style:family="text">
   <style:text-properties style:font-name="Courier New" fo:font-size="8pt"/>
  </style:style>
  <style:style style:name="Main_20_index_20_entry" style:display-name="Main index entry" style:family="text">
   <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
  </style:style>
  <style:style style:name="Footnote_20_anchor" style:display-name="Footnote anchor" style:family="text">
   <style:text-properties style:text-position="super 58%"/>
  </style:style>
  <style:style style:name="Endnote_20_anchor" style:display-name="Endnote anchor" style:family="text">
   <style:text-properties style:text-position="super 58%"/>
  </style:style>
  <style:style style:name="Rubies" style:family="text">
   <style:text-properties fo:font-size="6pt" style:font-size-asian="6pt" style:font-size-complex="6pt"/>
  </style:style>
  <style:style style:name="Emphasis" style:family="text">
   <style:text-properties fo:font-style="italic" fo:background-color="transparent"/>
  </style:style>
  <style:style style:name="Citation" style:family="text">
   <style:text-properties fo:font-style="italic"/>
  </style:style>
  <style:style style:name="Strong_20_Emphasis" style:display-name="Strong Emphasis" style:family="text">
   <style:text-properties fo:text-transform="uppercase"/>
  </style:style>
  <style:style style:name="Source_20_Text" style:display-name="Source Text" style:family="text">
   <style:text-properties style:font-name="Cumberland" style:font-name-asian="Cumberland" style:font-name-complex="Cumberland"/>
  </style:style>
  <style:style style:name="Example" style:family="text">
   <style:text-properties style:font-name="Courier New1"/>
  </style:style>
  <style:style style:name="User_20_Entry" style:display-name="User Entry" style:family="text">
   <style:text-properties style:font-name="Cumberland" style:font-name-asian="Cumberland" style:font-name-complex="Cumberland"/>
  </style:style>
  <style:style style:name="Variable" style:family="text">
   <style:text-properties fo:font-style="italic" style:font-style-asian="italic" style:font-style-complex="italic"/>
  </style:style>
  <style:style style:name="Definition" style:family="text"/>
  <style:style style:name="Teletype" style:family="text">
   <style:text-properties style:font-name="Cumberland" style:font-name-asian="Cumberland" style:font-name-complex="Cumberland"/>
  </style:style>
  <style:style style:name="Frame" style:family="graphic">
   <style:graphic-properties text:anchor-type="paragraph" svg:x="0cm" svg:y="0cm" style:wrap="parallel" style:number-wrapped-paragraphs="no-limit" style:wrap-contour="false" style:vertical-pos="top" style:vertical-rel="paragraph-content" style:horizontal-pos="center" style:horizontal-rel="paragraph-content"/>
  </style:style>
  <style:style style:name="Graphics" style:family="graphic">
   <style:graphic-properties text:anchor-type="paragraph" svg:x="0cm" svg:y="0cm" style:wrap="none" style:vertical-pos="top" style:vertical-rel="paragraph" style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
  </style:style>
  <style:style style:name="OLE" style:family="graphic">
   <style:graphic-properties text:anchor-type="paragraph" svg:x="0cm" svg:y="0cm" style:wrap="none" style:vertical-pos="top" style:vertical-rel="paragraph" style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
  </style:style>
  <style:style style:name="Formula" style:family="graphic">
   <style:graphic-properties text:anchor-type="as-char" svg:y="0cm" style:vertical-pos="top" style:vertical-rel="baseline"/>
  </style:style>
  <style:style style:name="Labels" style:family="graphic" style:auto-update="true">
   <style:graphic-properties text:anchor-type="as-char" svg:y="0cm" fo:margin-left="0.201cm" fo:margin-right="0.201cm" style:protect="size position" style:vertical-pos="top" style:vertical-rel="baseline"/>
  </style:style>
  <text:outline-style style:name="Outline">
   <text:outline-level-style text:level="1" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="2" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="3" text:style-name="Zeichenformat" style:num-format="">
    <style:list-level-properties/>
   </text:outline-level-style>
   <text:outline-level-style text:level="4" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="5" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="6" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="7" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="8" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="9" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
   <text:outline-level-style text:level="10" style:num-format="">
    <style:list-level-properties text:min-label-distance="0.381cm"/>
   </text:outline-level-style>
  </text:outline-style>
  <text:list-style style:name="Numbering_20_1" style:display-name="Numbering 1">
   <text:list-level-style-number text:level="1" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="2" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="0.499cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="3" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="0.999cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="4" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="1.498cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="5" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="1.997cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="6" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="2.496cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="7" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="2.995cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="8" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="3.494cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="9" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="3.994cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
   <text:list-level-style-number text:level="10" text:style-name="Numbering_20_Symbols" style:num-suffix="." style:num-format="1">
    <style:list-level-properties text:space-before="4.493cm" text:min-label-width="0.499cm"/>
   </text:list-level-style-number>
  </text:list-style>
  <text:list-style style:name="List_20_1" style:display-name="List 1">
   <text:list-level-style-bullet text:level="1" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="2" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="0.395cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="3" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="0.79cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="4" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="1.185cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="5" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="1.581cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="6" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="1.976cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="7" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="2.371cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="8" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="2.766cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="9" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="3.161cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="10" text:style-name="Numbering_20_Symbols" text:bullet-char="•">
    <style:list-level-properties text:space-before="3.556cm" text:min-label-width="0.395cm"/>
    <style:text-properties style:font-name="StarSymbol"/>
   </text:list-level-style-bullet>
  </text:list-style>
  <text:list-style style:name="List_20_2" style:display-name="List 2">
   <text:list-level-style-bullet text:level="1" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.3cm" fo:text-indent="-0.3cm" fo:margin-left="0.3cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="2" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.6cm" fo:text-indent="-0.3cm" fo:margin-left="0.6cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="3" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.9cm" fo:text-indent="-0.3cm" fo:margin-left="0.9cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="4" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.199cm" fo:text-indent="-0.3cm" fo:margin-left="1.199cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="5" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.499cm" fo:text-indent="-0.3cm" fo:margin-left="1.499cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="6" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.799cm" fo:text-indent="-0.3cm" fo:margin-left="1.799cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="7" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.101cm" fo:text-indent="-0.3cm" fo:margin-left="2.101cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="8" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.401cm" fo:text-indent="-0.3cm" fo:margin-left="2.401cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="9" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.701cm" fo:text-indent="-0.3cm" fo:margin-left="2.701cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="10" text:style-name="Numbering_20_Symbols" text:bullet-char="–">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3cm" fo:text-indent="-0.3cm" fo:margin-left="3cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
  </text:list-style>
  <text:list-style style:name="List_20_3" style:display-name="List 3">
   <text:list-level-style-bullet text:level="1" text:style-name="Numbering_20_Symbols" text:bullet-char="☑">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.395cm" fo:text-indent="-0.395cm" fo:margin-left="0.395cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="2" text:style-name="Numbering_20_Symbols" text:bullet-char="□">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.79cm" fo:text-indent="-0.395cm" fo:margin-left="0.79cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="3" text:style-name="Numbering_20_Symbols" text:bullet-char="☑">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.395cm" fo:text-indent="-0.395cm" fo:margin-left="0.395cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="4" text:style-name="Numbering_20_Symbols" text:bullet-char="□">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.79cm" fo:text-indent="-0.395cm" fo:margin-left="0.79cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="5" text:style-name="Numbering_20_Symbols" text:bullet-char="☑">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.395cm" fo:text-indent="-0.395cm" fo:margin-left="0.395cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="6" text:style-name="Numbering_20_Symbols" text:bullet-char="□">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.79cm" fo:text-indent="-0.395cm" fo:margin-left="0.79cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="7" text:style-name="Numbering_20_Symbols" text:bullet-char="☑">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.395cm" fo:text-indent="-0.395cm" fo:margin-left="0.395cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="8" text:style-name="Numbering_20_Symbols" text:bullet-char="□">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.79cm" fo:text-indent="-0.395cm" fo:margin-left="0.79cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="9" text:style-name="Numbering_20_Symbols" text:bullet-char="☑">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.395cm" fo:text-indent="-0.395cm" fo:margin-left="0.395cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
   <text:list-level-style-bullet text:level="10" text:style-name="Numbering_20_Symbols" text:bullet-char="□">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
     <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.79cm" fo:text-indent="-0.395cm" fo:margin-left="0.79cm"/>
    </style:list-level-properties>
    <style:text-properties fo:font-family="OpenSymbol"/>
   </text:list-level-style-bullet>
  </text:list-style>
  <text:notes-configuration text:note-class="footnote" text:citation-style-name="Footnote_20_Symbol" text:citation-body-style-name="Footnote_20_anchor" style:num-format="1" text:start-value="0" text:footnotes-position="page" text:start-numbering-at="page"/>
  <text:notes-configuration text:note-class="endnote" text:citation-style-name="Endnote_20_Symbol" text:citation-body-style-name="Endnote_20_anchor" text:master-page-name="Endnote" style:num-format="1" text:start-value="0"/>
  <text:linenumbering-configuration text:style-name="Line_20_numbering" text:number-lines="false" text:offset="0.499cm" style:num-format="1" text:number-position="left" text:increment="5"/>
 </office:styles>
 <office:automatic-styles>
  <style:page-layout style:name="Mpm1">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:num-format="1" style:paper-tray-name="[From printer settings]" style:print-orientation="portrait" fo:margin-top="3.2cm" fo:margin-bottom="2.499cm" fo:margin-left="2.701cm" fo:margin-right="3cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:columns fo:column-count="1" fo:column-gap="0cm"/>
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style>
    <style:header-footer-properties fo:min-height="1.699cm" fo:margin-left="0cm" fo:margin-right="0cm" fo:margin-top="1.199cm" style:shadow="none" style:dynamic-spacing="false"/>
   </style:footer-style>
  </style:page-layout>
  <style:page-layout style:name="Mpm2">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2.499cm" fo:margin-right="2.499cm" style:shadow="none" fo:background-color="transparent" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:background-image/>
    <style:columns fo:column-count="1" fo:column-gap="0cm"/>
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
  <style:page-layout style:name="Mpm3" style:page-usage="left">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="1cm" fo:margin-left="2.499cm" fo:margin-right="4.5cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
  <style:page-layout style:name="Mpm4" style:page-usage="right">
   <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="1cm" fo:margin-left="2.499cm" fo:margin-right="4.5cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
  <style:page-layout style:name="Mpm5">
   <style:page-layout-properties fo:page-width="22.721cm" fo:page-height="11.4cm" style:num-format="1" style:print-orientation="landscape" fo:margin-top="0cm" fo:margin-bottom="0cm" fo:margin-left="0cm" fo:margin-right="0cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
  <style:page-layout style:name="Mpm6">
   <style:page-layout-properties fo:page-width="14.801cm" fo:page-height="21.001cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
  <style:page-layout style:name="Mpm7">
   <style:page-layout-properties fo:page-width="20.999cm" fo:page-height="29.699cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm" style:writing-mode="lr-tb" style:layout-grid-color="#c0c0c0" style:layout-grid-lines="20" style:layout-grid-base-height="0.706cm" style:layout-grid-ruby-height="0.353cm" style:layout-grid-mode="none" style:layout-grid-ruby-below="false" style:layout-grid-print="false" style:layout-grid-display="false" style:footnote-max-height="0cm">
    <style:footnote-sep style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
   </style:page-layout-properties>
   <style:header-style/>
   <style:footer-style/>
  </style:page-layout>
 </office:automatic-styles>
 <office:master-styles>
  <style:master-page style:name="Standard" style:page-layout-name="Mpm1">
   <style:footer>
    <text:p text:style-name="Footer"><text:page-number text:select-page="current"/></text:p>
   </style:footer>
  </style:master-page>
  <style:master-page style:name="First_20_Page" style:display-name="First Page" style:page-layout-name="Mpm2" style:next-style-name="Standard"/>
  <style:master-page style:name="Left_20_Page" style:display-name="Left Page" style:page-layout-name="Mpm3"/>
  <style:master-page style:name="Right_20_Page" style:display-name="Right Page" style:page-layout-name="Mpm4"/>
  <style:master-page style:name="Envelope" style:page-layout-name="Mpm5"/>
  <style:master-page style:name="Index" style:page-layout-name="Mpm6" style:next-style-name="Standard"/>
  <style:master-page style:name="Endnote" style:page-layout-name="Mpm7"/>
 </office:master-styles>
</office:document-styles>
'''
    _MIMETYPE = 'application/vnd.oasis.opendocument.text'

    def set_up(self):
        """Create a temporary directory containing the internal 
        structure of an ODT file except 'content.xml'.
        """

        # Generate the common ODF components.

        message = OdfFile.set_up(self)

        if message.startswith('ERROR'):
            return message

        # Generate manifest.rdf

        try:
            with open(self.tempDir + '/manifest.rdf', 'w', encoding='utf-8') as f:
                f.write(self._MANIFEST_RDF)
        except:
            return 'ERROR: Cannot write "manifest.rdf"'

        return 'SUCCESS: ODT structure generated.'

    def convert_from_yw(self, text):
        """Convert yw7 raw markup to odt. Return an xml string.
        """

        ODT_REPLACEMENTS = [
            ['&', '&amp;'],
            ['>', '&gt;'],
            ['<', '&lt;'],
            ['\n', '</text:p>\n<text:p text:style-name="First_20_line_20_indent">'],
            ['[i]', '<text:span text:style-name="Emphasis">'],
            ['[/i]', '</text:span>'],
            ['[b]', '<text:span text:style-name="Strong_20_Emphasis">'],
            ['[/b]', '</text:span>'],
            ['/*', '<office:annotation><dc:creator>' +
                self.author + '</dc:creator><text:p>'],
            ['*/', '</text:p></office:annotation>'],
        ]

        try:

            # process italics and bold markup reaching across linebreaks

            italics = False
            bold = False
            newlines = []
            lines = text.split('\n')
            for line in lines:
                if italics:
                    line = '[i]' + line
                    italics = False

                while line.count('[i]') > line.count('[/i]'):
                    line += '[/i]'
                    italics = True

                while line.count('[/i]') > line.count('[i]'):
                    line = '[i]' + line

                line = line.replace('[i][/i]', '')

                if bold:
                    line = '[b]' + line
                    bold = False

                while line.count('[b]') > line.count('[/b]'):
                    line += '[/b]'
                    bold = True

                while line.count('[/b]') > line.count('[b]'):
                    line = '[b]' + line

                line = line.replace('[b][/b]', '')

                newlines.append(line)

            text = '\n'.join(newlines).rstrip()

            for r in ODT_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return text


class OdtFullSynopsis(OdtFile):
    """ODT scene summaries file representation.

    Export a full synopsis.
    """

    DESCRIPTION = 'Full synopsis'
    SUFFIX = '_full_synopsis'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title</text:h>
'''

    sceneTemplate = '''<text:p text:style-name="Text_20_body"><office:annotation>
<dc:creator>scene title</dc:creator>
<text:p>~ ${Title} ~</text:p>
<text:p/>
</office:annotation>$Desc</text:p>
'''

    sceneDivider = '''<text:p text:style-name="Heading_20_4">* * *</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER


class OdtBriefSynopsis(OdtFile):
    """ODT chapter summaries snf scene titles file representation.

    Export a brief synopsis.
    """

    DESCRIPTION = 'Brief synopsis'
    SUFFIX = '_brief_synopsis'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Desc</text:h>
'''

    chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Desc</text:h>
'''

    sceneTemplate = '''<text:p text:style-name="Text_20_body">$Title</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER


class OdtChapterOverview(OdtFile):
    """ODT part and chapter summaries file representation.

    Export a very brief synopsis.
    """

    DESCRIPTION = 'Chapter overview'
    SUFFIX = '_chapter_overview'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Desc</text:h>
'''

    chapterTemplate = '''<text:p text:style-name="Text_20_body">$Desc</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER


class OdtCharacterSheets(OdtFile):
    """ODT character descriptions file representation.

    Export a character sheet.
    """

    DESCRIPTION = 'Character sheets'
    SUFFIX = '_character_sheets'

    fileHeader = OdtFile.CONTENT_XML_HEADER + '''<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    characterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$FullName$AKA</text:h>
<text:section text:style-name="Sect1" text:name="CrID:$ID">
<text:h text:style-name="Heading_20_3" text:outline-level="3">Description</text:h>
<text:section text:style-name="Sect1" text:name="CrID_desc:$ID">
<text:p text:style-name="Text_20_body">$Desc</text:p>
</text:section>
<text:h text:style-name="Heading_20_3" text:outline-level="3">Bio</text:h>
<text:section text:style-name="Sect1" text:name="CrID_bio:$ID">
<text:p text:style-name="Text_20_body">$Bio</text:p>
</text:section>
<text:h text:style-name="Heading_20_3" text:outline-level="3">Goals</text:h>
<text:section text:style-name="Sect1" text:name="CrID_goals:$ID">
<text:p text:style-name="Text_20_body">$Goals</text:p>
</text:section>
<text:h text:style-name="Heading_20_3" text:outline-level="3">Notes</text:h>
<text:section text:style-name="Sect1" text:name="CrID_notes:$ID">
<text:p text:style-name="Text_20_body">$Notes</text:p>
</text:section>
</text:section>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER

    def get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        """
        characterMapping = OdtFile.get_characterMapping(self, crId)

        if self.characters[crId].aka:
            characterMapping['AKA'] = ' ("' + self.characters[crId].aka + '")'

        if self.characters[crId].fullName:
            characterMapping['FullName'] = '/' + self.characters[crId].fullName

        return characterMapping


class OdtLocationSheets(OdtFile):
    """ODT location descriptions file representation.

    Export a location sheet.
    """

    DESCRIPTION = 'Location sheets'
    SUFFIX = '_location_sheets'

    fileHeader = OdtFile.CONTENT_XML_HEADER + '''<text:p text:style-name="Title">$Title</text:p>
<text:p text:style-name="Subtitle">$AuthorName</text:p>
'''

    locationTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$AKA</text:h>
<text:section text:style-name="Sect1" text:name="LcID:$ID">
<text:p text:style-name="Text_20_body">$Desc</text:p>
</text:section>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER

    def get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        """
        locationMapping = OdtFile.get_locationMapping(self, lcId)

        if self.locations[lcId].aka:
            locationMapping['AKA'] = ' ("' + self.locations[lcId].aka + '")'

        return locationMapping


class OdtReport(OdtFile):
    """ODT scene summaries file representation.

    Export a full synopsis.
    """

    DESCRIPTION = 'Project report'
    SUFFIX = '_report'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title</text:h>
'''

    chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title</text:h>
<text:p text:style-name="Text_20_body">$Desc</text:p>
'''

    sceneTemplate = '''<text:h text:style-name="Heading_20_3" text:outline-level="3"> ${Title}</text:h>
<text:p>$Desc</text:p>
'''

    appendedSceneTemplate = '''<text:h text:style-name="Heading_20_3" text:outline-level="3"> ${Title}</text:h>
<text:p>$Desc</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER

import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.beans import PropertyValue

from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY

CTX = uno.getComponentContext()
SM = CTX.getServiceManager()


def create_instance(name, with_context=False):
    if with_context:
        instance = SM.createInstanceWithContext(name, CTX)
    else:
        instance = SM.createInstance(name)
    return instance


def msgbox(message, title='yWriter import/export', buttons=BUTTONS_OK, type_msg=INFOBOX):
    """ Create message box
        type_msg: MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX

        MSG_BUTTONS: BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, 
        BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY

        MSG_RESULTS: OK, YES, NO, CANCEL

        http://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1awt_1_1XMessageBoxFactory.html
    """
    toolkit = create_instance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    mb = toolkit.createMessageBox(
        parent, type_msg, buttons, title, str(message))
    return mb.execute()


class Stub():

    def dummy(self):
        pass


def FilePicker(path=None, mode=0):
    """
    Read file:  `mode in (0, 6, 7, 8, 9)`
    Write file: `mode in (1, 2, 3, 4, 5, 10)`
    see: (http://api.libreoffice.org/docs/idl/ref/
            namespacecom_1_1sun_1_1star_1_1ui_1_1
            dialogs_1_1TemplateDescription.html)

    See: https://stackoverflow.com/questions/30840736/libreoffice-how-to-create-a-file-dialog-via-python-macro
    """
    # shortcut:
    createUnoService = (
        XSCRIPTCONTEXT
        .getComponentContext()
        .getServiceManager()
        .createInstance
    )

    filepicker = createUnoService("com.sun.star.ui.dialogs.OfficeFilePicker")

    if path:
        filepicker.setDisplayDirectory(path)

    filepicker.initialize((mode,))
    filepicker.appendFilter("CSV Files", "*.csv")

    if filepicker.execute():
        return filepicker.getFiles()[0]


import sys
import webbrowser



class Ui():
    """Base class for UI facades, implementing a 'silent mode'.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """The application may use a subclass  
        for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """What's the converter going to do?"""
        self.infoWhatText = message

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message

    def start(self):
        """To be overridden by subclasses requiring
        special action to launch the user interaction.
        """


class YwCnv():
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, sourceFile, targetFile):
        """Convert sourceFile into targetFile and return a message.

        Positional arguments:
            sourceFile, targetFile -- Novel subclass instances.

        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with SUCCESS or ERROR.

        Error handling:
        - Check if sourceFile and targetFile are correctly initialized.
        - Ask for permission to overwrite targetFile.
        - Pass the error messages of the called methods of sourceFile and targetFile.
        - The success message comes from targetFile.write(), if called.       
        """

        # Initial error handling.

        if sourceFile.filePath is None:
            return 'ERROR: Source "' + os.path.normpath(sourceFile.filePath) + '" is not of the supported type.'

        if not sourceFile.file_exists():
            return 'ERROR: "' + os.path.normpath(sourceFile.filePath) + '" not found.'

        if targetFile.filePath is None:
            return 'ERROR: Target "' + os.path.normpath(targetFile.filePath) + '" is not of the supported type.'

        if targetFile.file_exists() and not self.confirm_overwrite(targetFile.filePath):
            return 'ERROR: Action canceled by user.'

        # Make the source object read the source file.

        message = sourceFile.read()

        if message.startswith('ERROR'):
            return message

        # Make the target object merge the source object's instance variables.

        message = targetFile.merge(sourceFile)

        if message.startswith('ERROR'):
            return message

        # Make the source object write the target file.

        return targetFile.write()

    def confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        This is a stub to be overridden by subclass methods.
        """
        return True



class FileFactory:
    """Base class for conversion object factory classes.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.

    This class emulates a "FileFactory" Interface.
    Instances can be used as stubs for factories instantiated at runtime.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a private instance variable.

        Positional arguments:
            fileClasses -- list of classes from which an instance can be returned.
        """
        self.fileClasses = fileClasses

    def make_file_objects(self, sourcePath, **kwargs):
        """A factory method stub.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the target file type.

        Return a tuple with three elements:
        - A message string starting with 'ERROR'
        - sourceFile: None
        - targetFile: None

        Factory method to be overridden by subclasses.
        Subclasses return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance
        - targetFile: a Novel subclass instance
        """
        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None



class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a YwFile subclass instance, or None in case of error
        - targetFile: None
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        for fileClass in self.fileClasses:

            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return 'SUCCESS', sourceFile, None

        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None



class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the target file type.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']

        for fileClass in self.fileClasses:

            if fileClass.SUFFIX == suffix:

                if suffix is None:
                    suffix = ''

                targetFile = fileClass(
                    fileName + suffix + fileClass.EXTENSION, **kwargs)
                return 'SUCCESS', None, targetFile

        return 'ERROR: File type of "' + os.path.normpath(sourcePath) + '" not supported.', None, None


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None
        """

        for fileClass in self.fileClasses:

            if fileClass.SUFFIX is not None:

                if sourcePath.endswith(fileClass.SUFFIX + fileClass.EXTENSION):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return 'SUCCESS', sourceFile, None

        return 'ERROR: This document is not meant to be written back.', None, None



class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.
        Override the superclass method.

        Positional arguments:
            sourcePath -- string; path to the source file to convert.

        Optional arguments:
            suffix -- string; an indicator for the source file type.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: None
        - targetFile: a YwFile subclass instance, or None in case of error

        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']

        if sourceSuffix:
            ywPathBasis = fileName.split(sourceSuffix)[0]

        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.

        for fileClass in self.fileClasses:

            if os.path.isfile(ywPathBasis + fileClass.EXTENSION):
                targetFile = fileClass(
                    ywPathBasis + fileClass.EXTENSION, **kwargs)
                return 'SUCCESS', None, targetFile

        return 'ERROR: No yWriter project to write.', None, None


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        run(sourcePath, suffix) -- Create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- List of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- List of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- List of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- List of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
        newFile -- string; path to the target file in case of success.   
    """

    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.

        self.exportSourceFactory = ExportSourceFactory(
            self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(
            self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(
            self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(
            self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

        self.newFile = None
        # Also indicates successful conversion.

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        sourcePath -- str; the source file path.
        suffix -- str; target file name suffix. 

        This is a template method that calls primitive operations by case.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(
                'ERROR: File "' + os.path.normpath(sourcePath) + '" not found.')
            return

        message, sourceFile, dummy = self.exportSourceFactory.make_file_objects(
            sourcePath, **kwargs)

        if message.startswith('SUCCESS'):
            # The source file is a yWriter project.

            message, dummy, targetFile = self.exportTargetFactory.make_file_objects(
                sourcePath, **kwargs)

            if message.startswith('SUCCESS'):
                self.export_from_yw(sourceFile, targetFile)

            else:
                self.ui.set_info_how(message)

        else:
            # The source file is not a yWriter project.

            message, sourceFile, dummy = self.importSourceFactory.make_file_objects(
                sourcePath, **kwargs)

            if message.startswith('SUCCESS'):
                kwargs['suffix'] = sourceFile.SUFFIX
                message, dummy, targetFile = self.importTargetFactory.make_file_objects(
                    sourcePath, **kwargs)

                if message.startswith('SUCCESS'):
                    self.import_to_yw(sourceFile, targetFile)

                else:
                    self.ui.set_info_how(message)

            else:
                # A new yWriter project might be required.

                message, sourceFile, targetFile = self.newProjectFactory.make_file_objects(
                    sourcePath, **kwargs)

                if message.startswith('SUCCESS'):
                    self.create_yw7(sourceFile, targetFile)

                else:
                    self.ui.set_info_how(message)

    def export_from_yw(self, sourceFile, targetFile):
        """Convert from yWriter project to other file format.

        sourceFile -- YwFile subclass instance.
        targetFile -- Any Novel subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')

        # Convert sourceFile into targetFile.

        message = self.convert(sourceFile, targetFile)

        # Pass the message to the UI.

        self.ui.set_info_how(message)

        # Save the new file pathname.

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.newFile = None

    def create_yw7(self, sourceFile, targetFile):
        """Create targetFile from sourceFile.

        sourceFile -- Any Novel subclass instance.
        targetFile -- YwFile subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf targetFile already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what(
            'Create a yWriter project file from ' + sourceFile.DESCRIPTION + '\nNew project: "' + os.path.normpath(targetFile.filePath) + '"')

        if targetFile.file_exists():
            self.ui.set_info_how(
                'ERROR: "' + os.path.normpath(targetFile.filePath) + '" already exists.')

        else:
            # Convert sourceFile into targetFile.

            message = self.convert(sourceFile, targetFile)

            # Pass the message to the UI.

            self.ui.set_info_how(message)

            # Save the new file pathname.

            if message.startswith('SUCCESS'):
                self.newFile = targetFile.filePath

            else:
                self.newFile = None

    def import_to_yw(self, sourceFile, targetFile):
        """Convert from any file format to yWriter project.

        sourceFile -- Any Novel subclass instance.
        targetFile -- YwFile subclass instance.

        This is a primitive operation of the run() template method.

        1. Send specific information about the conversion to the UI.
        2. Convert sourceFile into targetFile.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """

        # Send specific information about the conversion to the UI.

        self.ui.set_info_what('Input: ' + sourceFile.DESCRIPTION + ' "' + os.path.normpath(
            sourceFile.filePath) + '"\nOutput: ' + targetFile.DESCRIPTION + ' "' + os.path.normpath(targetFile.filePath) + '"')

        # Convert sourceFile into targetFile.

        message = self.convert(sourceFile, targetFile)

        # Pass the message to the UI.

        self.ui.set_info_how(message)

        # Delete the temporay file, if exists.

        self.delete_tempfile(sourceFile.filePath)

        # Save the new file pathname.

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.newFile = None

    def confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file, overriding the superclass method."""
        return self.ui.ask_yes_no('Overwrite existing file "' + os.path.normpath(filePath) + '"?')

    def delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""

        if filePath.endswith('.html'):
            # Might it be a temporary text document?

            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?

                try:
                    os.remove(filePath)

                except:
                    pass

        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?

            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?

                try:
                    os.remove(filePath)

                except:
                    pass

    def open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        webbrowser.open(self.newFile)
        sys.exit(0)
import csv

from datetime import datetime



class Chapter():
    """yWriter chapter representation.
    # xml: <CHAPTERS><CHAPTER>
    """

    chapterTitlePrefix = "Chapter "
    # str
    # Can be changed at runtime for non-English projects.

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.oldType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

    def get_title(self):
        """Fix auto-chapter titles if necessary 
        """
        text = self.title

        if text:
            text = text.replace('Chapter ', self.chapterTitlePrefix)

        return text



def fix_iso_dt(dateTimeStr):
    """Return a date/time string with a four-number year.
    This is required for comparing date/time strings, 
    and by the datetime.fromisoformat() method.

    Substitute missing time by "00:00:00".
    Substitute missing month by '01'.
    Substitute missing day by '01'.
    If the date is empty or out of yWriter's range, return None. 
    """
    if not dateTimeStr:
        return None

    if dateTimeStr.startswith('BC'):
        return None

    dt = dateTimeStr.split(' ')

    if len(dt) == 1:
        dt.append('00:00:00')

    date = dt[0].split('-')

    while len(date) < 3:
        date.append('01')

    if int(date[0]) < 100:
        return None

    if int(date[0]) > 9999:
        return None

    date[0] = date[0].zfill(4)
    dt[0] = ('-').join(date)
    dateTimeStr = (' ').join(dt)
    return dateTimeStr


class AeonTimeline(FileExport):
    """File representation of a csv file exported by Aeon Timeline 3. 

    Represents a csv file with a record per scene.
    - Records are separated by line breaks.
    - Data fields are delimited by the _SEPARATOR character.
    """

    # Aeon 3 csv export structure (fix part)

    _SCENE_MARKER = 'Scene'
    _CHAPTER_MARKER = 'Chapter'
    _PART_MARKER = 'Part'
    _SCENE_LABEL = 'Narrative Position'
    _TYPE_LABEL = 'Type'
    _EVENT_MARKER = 'Event'
    _STRUCT_MARKER = 'Narrative Folder'
    _START_DATE_TIME_LABEL = 'Start Date'
    _END_DATE_TIME_LABEL = 'End Date'

    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    # Events assigned to the "varrative" become
    # regular scenes, the others become Notes scenes.

    def __init__(self, filePath, **kwargs):
        """Extend the superclass constructor,
        defining instance variables.
        """
        FileExport.__init__(self, filePath, **kwargs)
        self.labels = []
        self.entities = []
        self.partNrPrefix = kwargs['part_number_prefix']

        if self.partNrPrefix:
            self.partNrPrefix += ' '

        self.chapterNrPrefix = kwargs['chapter_number_prefix']

        if self.chapterNrPrefix:
            self.chapterNrPrefix += ' '

        self.partDescLabel = kwargs['part_desc_label']
        self.chapterDescLabel = kwargs['chapter_desc_label']
        self.sceneDescLabel = kwargs['scene_desc_label']
        self.sceneTitleLabel = kwargs['scene_title_label']
        self.notesLabel = kwargs['notes_label']
        self.tagLabel = kwargs['tag_label']
        self.locationLabel = kwargs['location_label']
        self.itemLabel = kwargs['item_label']
        self.characterLabel = kwargs['character_label']
        self.viewpointLabel = kwargs['viewpoint_label']

    def read(self):
        """Parse the timeline structure.

        Return a message beginning with SUCCESS or ERROR.
        """

        def get_lcIds(lcTitles):
            """Return a list of location IDs; Add new location to the project.
            """
            lcIds = []

            for lcTitle in lcTitles:

                if lcTitle in self.locIdsByTitle:
                    lcIds.append(self.locIdsByTitle[lcTitle])

                elif lcTitle:
                    # Add a new location to the project.

                    self.locationCount += 1
                    lcId = str(self.locationCount)
                    self.locIdsByTitle[lcTitle] = lcId
                    self.locations[lcId] = WorldElement()
                    self.locations[lcId].title = lcTitle
                    self.srtLocations.append(lcId)
                    lcIds.append(lcId)

                else:
                    return None

            return lcIds

        def get_itIds(itTitles):
            """Return a list of item IDs; Add new item to the project.
            """
            itIds = []

            for itTitle in itTitles:

                if itTitle in self.itmIdsByTitle:
                    itIds.append(self.itmIdsByTitle[itTitle])

                elif itTitle:
                    # Add a new item to the project.

                    self.itemCount += 1
                    itId = str(self.itemCount)
                    self.itmIdsByTitle[itTitle] = itId
                    self.items[itId] = WorldElement()
                    self.items[itId].title = itTitle
                    self.srtItems.append(itId)
                    itIds.append(itId)

                else:
                    return None

            return itIds

        self.characterCount = 0
        self.chrIdsByTitle = {}
        # key = character title
        # value = character ID

        def get_crIds(crTitles):
            """Return a list of character IDs; Add new characters to the project.
            """
            crIds = []

            for crTitle in crTitles:

                if crTitle in self.chrIdsByTitle:
                    crIds.append(self.chrIdsByTitle[crTitle])

                elif crTitle:
                    # Add a new character to the project.

                    self.characterCount += 1
                    crId = str(self.characterCount)
                    self.chrIdsByTitle[crTitle] = crId
                    self.characters[crId] = Character()
                    self.characters[crId].title = crTitle
                    self.srtCharacters.append(crId)
                    crIds.append(crId)

                else:
                    return None

            return crIds

        self.locationCount = 0
        self.locIdsByTitle = {}
        # key = location title
        # value = location ID

        self.itemCount = 0
        self.itmIdsByTitle = {}
        # key = item title
        # value = item ID

        internalDelimiter = ','
        try:

            for label in [self._SCENE_LABEL, self.sceneTitleLabel, self._START_DATE_TIME_LABEL, self._END_DATE_TIME_LABEL]:

                if not label in self.labels:
                    return 'ERROR: Property "' + label + '" is missing.'

            scIdsByStruc = {}
            chIdsByStruc = {}
            otherEvents = []
            eventCount = 0
            chapterCount = 0

            for aeonEntity in self.entities:

                if aeonEntity[self._SCENE_LABEL]:
                    narrativeType, narrativePosition = aeonEntity[self._SCENE_LABEL].split(' ')

                    # Make the narrative position a sortable string.

                    numbers = narrativePosition.split('.')

                    for i in range(len(numbers)):
                        numbers[i] = numbers[i].zfill(4)
                        narrativePosition = ('.').join(numbers)

                else:
                    narrativeType = ''
                    narrativePosition = ''

                if aeonEntity[self._TYPE_LABEL] == self._STRUCT_MARKER:

                    if narrativeType == self._CHAPTER_MARKER:
                        chapterCount += 1
                        chId = str(chapterCount)
                        chIdsByStruc[narrativePosition] = chId
                        self.chapters[chId] = Chapter()
                        self.chapters[chId].chLevel = 0

                        if self.chapterDescLabel:
                            self.chapters[chId].desc = aeonEntity[self.chapterDescLabel]

                    elif narrativeType == self._PART_MARKER:
                        chapterCount += 1
                        chId = str(chapterCount)
                        chIdsByStruc[narrativePosition] = chId
                        self.chapters[chId] = Chapter()
                        self.chapters[chId].chLevel = 1
                        narrativePosition += '.0000'

                        if self.partDescLabel:
                            self.chapters[chId].desc = aeonEntity[self.partDescLabel]

                    continue

                elif aeonEntity[self._TYPE_LABEL] != self._EVENT_MARKER:
                    continue

                eventCount += 1
                scId = str(eventCount)
                self.scenes[scId] = Scene()

                if narrativeType == self._SCENE_MARKER:
                    self.scenes[scId].isNotesScene = False
                    scIdsByStruc[narrativePosition] = scId

                else:
                    self.scenes[scId].isNotesScene = True
                    otherEvents.append(scId)

                self.scenes[scId].title = aeonEntity[self.sceneTitleLabel]

                startDateTimeStr = fix_iso_dt(aeonEntity[self._START_DATE_TIME_LABEL])

                if startDateTimeStr is not None:
                    startDateTime = startDateTimeStr.split(' ')
                    self.scenes[scId].date = startDateTime[0]
                    self.scenes[scId].time = startDateTime[1]
                    endDateTimeStr = fix_iso_dt(aeonEntity[self._END_DATE_TIME_LABEL])

                    if endDateTimeStr is not None:

                        # Calculate duration of scenes that begin after 99-12-31.

                        sceneStart = datetime.fromisoformat(startDateTimeStr)
                        sceneEnd = datetime.fromisoformat(endDateTimeStr)
                        sceneDuration = sceneEnd - sceneStart
                        lastsHours = sceneDuration.seconds // 3600
                        lastsMinutes = (sceneDuration.seconds % 3600) // 60

                        self.scenes[scId].lastsDays = str(sceneDuration.days)
                        self.scenes[scId].lastsHours = str(lastsHours)
                        self.scenes[scId].lastsMinutes = str(lastsMinutes)

                else:
                    self.scenes[scId].date = self.NULL_DATE
                    self.scenes[scId].time = self.NULL_TIME

                if self.sceneDescLabel in aeonEntity:
                    self.scenes[scId].desc = aeonEntity[self.sceneDescLabel]

                if self.notesLabel in aeonEntity:
                    self.scenes[scId].sceneNotes = aeonEntity[self.notesLabel]

                if self.tagLabel in aeonEntity and aeonEntity[self.tagLabel] != '':
                    self.scenes[scId].tags = aeonEntity[self.tagLabel].split(internalDelimiter)

                if self.locationLabel in aeonEntity:
                    self.scenes[scId].locations = get_lcIds(aeonEntity[self.locationLabel].split(internalDelimiter))

                if self.characterLabel in aeonEntity:
                    self.scenes[scId].characters = get_crIds(aeonEntity[self.characterLabel].split(internalDelimiter))

                if self.viewpointLabel in aeonEntity:
                    vpIds = get_crIds([aeonEntity[self.viewpointLabel]])

                    if vpIds is not None:
                        vpId = vpIds[0]

                        if self.scenes[scId].characters is None:
                            self.scenes[scId].characters = []

                        elif vpId in self.scenes[scId].characters:
                            self.scenes[scId].characters.remove[vpId]

                        self.scenes[scId].characters.insert(0, vpId)

                if self.itemLabel in aeonEntity:
                    self.scenes[scId].items = get_itIds(aeonEntity[self.itemLabel].split(internalDelimiter))

                # Set scene status = "Outline".

                self.scenes[scId].status = 1

        except(FileNotFoundError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" not found.'

        except(KeyError):
            return 'ERROR: Wrong csv structure.'

        except(ValueError):
            return 'ERROR: Wrong date/time format.'

        except:
            return 'ERROR: Can not parse "' + os.path.normpath(self.filePath) + '".'

        # Build the chapter structure as defined with Aeon v3.

        srtChpDict = sorted(chIdsByStruc.items())
        srtScnDict = sorted(scIdsByStruc.items())

        partNr = 0
        chapterNr = 0

        for ch in srtChpDict:
            self.srtChapters.append(ch[1])

            if self.chapters[ch[1]].chLevel == 0:
                chapterNr += 1
                self.chapters[ch[1]].title = self.chapterNrPrefix + str(chapterNr)

                for sc in srtScnDict:

                    if sc[0].startswith(ch[0]):
                        self.chapters[ch[1]].srtScenes.append(sc[1])

            else:
                partNr += 1
                self.chapters[ch[1]].title = self.partNrPrefix + str(partNr)

        # Create a chapter for the non-narrative events.

        chapterNr += 1
        chId = str(chapterCount + 1)
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Other events'
        self.chapters[chId].desc = 'Scenes generated from events that ar not assigned to the narrative structure.'
        self.chapters[chId].chType = 1
        self.chapters[chId].srtScenes = otherEvents
        self.srtChapters.append(chId)

        return 'SUCCESS: Data read from "' + os.path.normpath(self.filePath) + '".'


class CsvTimeline(AeonTimeline):
    """File representation of a csv file exported by Aeon Timeline 3. 

    Represents a csv file with a record per scene.
    - Records are separated by line breaks.
    - Data fields are delimited by commas.
    """

    EXTENSION = '.csv'
    DESCRIPTION = 'Aeon Timeline CSV export'
    SUFFIX = ''

    _SEPARATOR = ','

    def read(self):
        """Parse the csv file located at filePath, fetching the relevant data.
        Extend the superclass.

        Return a message beginning with SUCCESS or ERROR.
        """

        #--- Read the csv file.

        try:
            with open(self.filePath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=self._SEPARATOR)

                for label in reader.fieldnames:
                    self.labels.append(label)

                for row in reader:
                    aeonEntity = {}

                    for label in row:
                        aeonEntity[label] = row[label]

                    self.entities.append(aeonEntity)

        except(FileNotFoundError):
            return 'ERROR: "' + os.path.normpath(self.filePath) + '" not found.'

        except:
            return 'ERROR: Can not parse csv file "' + os.path.normpath(self.filePath) + '".'

        return AeonTimeline.read(self)



class CsvConverter(YwCnvUi):
    EXPORT_SOURCE_CLASSES = [CsvTimeline]
    EXPORT_TARGET_CLASSES = [OdtFullSynopsis,
                             OdtBriefSynopsis,
                             OdtChapterOverview,
                             OdtCharacterSheets,
                             OdtLocationSheets,
                             OdtReport,
                             ]

    def __init__(self):
        """Initialize instance variables.
        Extend the superclass constructor by
        changing the newProjectFactory strategy.
        """
        YwCnvUi.__init__(self)


class CsvCnvUno(CsvConverter):
    """Converter for yWriter project files.
    Variant with UNO UI.
    """

    def export_from_yw(self, sourceFile, targetFile):
        """Method for conversion from yw to other.
        Show only error messages.
        """
        message = self.convert(sourceFile, targetFile)

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.ui.set_info_how(message)
from com.sun.star.awt.MessageBoxResults import OK, YES, NO, CANCEL
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK, BUTTONS_OK_CANCEL, BUTTONS_YES_NO, BUTTONS_YES_NO_CANCEL, BUTTONS_RETRY_CANCEL, BUTTONS_ABORT_IGNORE_RETRY
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX



class UiUno(Ui):
    """UI subclass implementing a LibreOffice UNO facade."""

    def ask_yes_no(self, text):
        result = msgbox(text, buttons=BUTTONS_YES_NO,
                        type_msg=WARNINGBOX)

        if result == YES:
            return True

        else:
            return False

    def set_info_how(self, message):
        """How's the converter doing?"""
        self.infoHowText = message

        if message.startswith('SUCCESS'):
            msgbox(message, type_msg=INFOBOX)

        else:
            msgbox(message, type_msg=ERRORBOX)

INI_FILE = 'openyw.ini'

SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
    part_desc_label='Label',
    chapter_desc_label='Label',
    scene_desc_label='Summary',
    scene_title_label='Label',
    notes_label='Notes',
    tag_label='Tags',
    location_label='Location',
    item_label='Item',
    character_label='Participant',
    viewpoint_label='Viewpoint',
)


def open_csv(suffix, newExt):

    # Set last opened yWriter project as default (if existing).

    scriptLocation = os.path.dirname(__file__)
    inifile = uno.fileUrlToSystemPath(scriptLocation + '/' + INI_FILE)
    defaultFile = None
    config = ConfigParser()

    try:
        config.read(inifile)
        csvLastOpen = config.get('FILES', 'csv_last_open')

        if os.path.isfile(csvLastOpen):
            defaultFile = uno.systemPathToFileUrl(csvLastOpen)

    except:
        pass

    # Ask for csv file to open:

    csvFile = FilePicker(path=defaultFile)

    if csvFile is None:
        return

    sourcePath = uno.fileUrlToSystemPath(csvFile)
    aeonExt = os.path.splitext(sourcePath)[1]

    if not aeonExt in ['.csv']:
        msgbox('Please choose a csv file exported by Aeon Timeline 3.',
               'Import from yWriter', type_msg=ERRORBOX)
        return

    # Store selected yWriter project as "last opened".

    newFile = csvFile.replace(aeonExt, suffix + newExt)
    dirName, filename = os.path.split(newFile)
    lockFile = uno.fileUrlToSystemPath(
        dirName + '/') + '.~lock.' + filename + '#'

    if not config.has_section('FILES'):
        config.add_section('FILES')

    config.set('FILES', 'csv_last_open', uno.fileUrlToSystemPath(csvFile))

    with open(inifile, 'w') as f:
        config.write(f)

    # Check if import file is already open in LibreOffice:

    if os.path.isfile(lockFile):
        msgbox('Please close "' + filename + '" first.',
               'Import from Aeon Timeline 3', type_msg=ERRORBOX)
        return

    # Open yWriter project and convert data.

    workdir = os.path.dirname(sourcePath)
    os.chdir(workdir)
    converter = CsvCnvUno()
    converter.ui = UiUno('Import from Aeon Timeline 3')
    kwargs = {'suffix': suffix}
    kwargs.update(SETTINGS)
    converter.run(sourcePath, **kwargs)

    if converter.newFile:
        desktop = XSCRIPTCONTEXT.getDesktop()
        doc = desktop.loadComponentFromURL(newFile, "_blank", 0, ())


def get_chapteroverview():
    '''Import a chapter overview from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtChapterOverview.SUFFIX, OdtChapterOverview.EXTENSION)


def get_briefsynopsis():
    '''Import a brief synopsis from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtBriefSynopsis.SUFFIX, OdtBriefSynopsis.EXTENSION)


def get_fullsynopsis():
    '''Import a full synopsis from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtFullSynopsis.SUFFIX, OdtFullSynopsis.EXTENSION)


def get_charactersheets():
    '''Import character sheets from Aeon 3 to a Writer document.
    '''
    open_csv(OdtCharacterSheets.SUFFIX, OdtCharacterSheets.EXTENSION)


def get_locationsheets():
    '''Import location sheets from Aeon 3 to a Writer document.
    '''
    open_csv(OdtLocationSheets.SUFFIX, OdtLocationSheets.EXTENSION)


def get_report():
    '''Import a full report of the narrative from Aeon 3 to a Writer document.
    '''
    open_csv(OdtReport.SUFFIX, OdtReport.EXTENSION)
