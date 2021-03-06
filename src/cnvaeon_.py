"""Convert Aeon Timeline project data to odt. 

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.beans import PropertyValue
import os
from configparser import ConfigParser
from pathlib import Path
from pywriter.config.configuration import Configuration
from aeon3odtlib.uno_tools import *
from aeon3odtlib.aeon3odt_cnv_uno import Aeon3odtCnvUno
from aeon3odtlib.ui_uno import UiUno
from aeon3odtlib.odt_full_synopsis import OdtFullSynopsis
from aeon3odtlib.odt_brief_synopsis import OdtBriefSynopsis
from aeon3odtlib.odt_chapter_overview import OdtChapterOverview
from aeon3odtlib.odt_character_sheets import OdtCharacterSheets
from aeon3odtlib.odt_location_sheets import OdtLocationSheets
from aeon3odtlib.odt_report import OdtReport

INI_FILE = 'openyw.ini'
CONFIG_PROJECT = 'aeon3yw'
# cnvaeon uses the aeon3yw configuration file, if any.
SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
    type_event='Event',
    type_character='Character',
    type_location='Location',
    type_item='Item',
    character_label='Participant',
    location_label='Location',
    item_label='Item',
    part_desc_label='Label',
    chapter_desc_label='Label',
    scene_desc_label='Summary',
    scene_title_label='Label',
    notes_label='Notes',
    tag_label='Tags',
    viewpoint_label='Viewpoint',
    character_bio_label='Summary',
    character_aka_label='Nickname',
    character_desc_label1='Characteristics',
    character_desc_label2='Traits',
    character_desc_label3='',
    location_desc_label='Summary',
)


def open_src(suffix, newExt):
    """Open a yWriter project, create a new document and load it.
    
    Positional arguments:
        suffix -- str: filename suffix of the document to create.
        newExt -- str: file extension of the document to create.   
    """

    # Set last opened Aeon project as default (if existing).
    scriptLocation = os.path.dirname(__file__)
    inifile = uno.fileUrlToSystemPath(f'{scriptLocation}/{INI_FILE}')
    defaultFile = None
    config = ConfigParser()
    try:
        config.read(inifile)
        srcLastOpen = config.get('FILES', 'src_last_open')
        if os.path.isfile(srcLastOpen):
            defaultFile = uno.systemPathToFileUrl(srcLastOpen)
    except:
        pass

    # Ask for source file to open:
    srcFile = FilePicker(path=defaultFile)
    if srcFile is None:
        return

    sourcePath = uno.fileUrlToSystemPath(srcFile)
    __, aeonExt = os.path.splitext(sourcePath)
    converter = Aeon3odtCnvUno()
    extensions = []
    for srcClass in converter.EXPORT_SOURCE_CLASSES:
        extensions.append(srcClass.EXTENSION)
    if not aeonExt in extensions:
        msgbox('Please choose a csv file exported by Aeon Timeline 3, or an .aeon file.',
               'Import from Aeon timeline', type_msg=ERRORBOX)
        return

    # Store selected yWriter project as "last opened".
    newFile = srcFile.replace(aeonExt, f'{suffix}{newExt}')
    dirName, fileName = os.path.split(newFile)
    thisDir = uno.fileUrlToSystemPath(f'{dirName}/')
    lockFile = f'{thisDir}.~lock.{fileName}#'
    if not config.has_section('FILES'):
        config.add_section('FILES')
    config.set('FILES', 'src_last_open', uno.fileUrlToSystemPath(srcFile))
    with open(inifile, 'w') as f:
        config.write(f)

    # Check whether the import file is already open in LibreOffice:
    if os.path.isfile(lockFile):
        msgbox(f'Please close "{fileName}" first.',
               'Import from Aeon Timeline', type_msg=ERRORBOX)
        return

    workdir = os.path.dirname(sourcePath)

    # Read the aeon3yw configuration.
    iniFileName = f'{CONFIG_PROJECT}.ini'
    iniFiles = []
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        globalConfiguration = f'{homeDir}/.pyWriter/{CONFIG_PROJECT}/config/{iniFileName}'
        iniFiles.append(globalConfiguration)
    except:
        pass
    if not workdir:
        localConfiguration = f'./{iniFileName}'
    else:
        localConfiguration = f'{workdir}/{iniFileName}'
    iniFiles.append(localConfiguration)
    configuration = Configuration(SETTINGS)
    for iniFile in iniFiles:
        configuration.read(iniFile)

    # Open yWriter project and convert data.
    os.chdir(workdir)
    converter.ui = UiUno('Import from Aeon Timeline')
    kwargs = {'suffix': suffix}
    kwargs.update(configuration.settings)
    converter.run(sourcePath, **kwargs)
    if converter.newFile:
        desktop = XSCRIPTCONTEXT.getDesktop()
        desktop.loadComponentFromURL(newFile, "_blank", 0, ())


def get_chapteroverview():
    '''Import a chapter overview from Aeon Timeline to a Writer document. 
    '''
    open_src(OdtChapterOverview.SUFFIX, OdtChapterOverview.EXTENSION)


def get_briefsynopsis():
    '''Import a brief synopsis from Aeon Timeline to a Writer document. 
    '''
    open_src(OdtBriefSynopsis.SUFFIX, OdtBriefSynopsis.EXTENSION)


def get_fullsynopsis():
    '''Import a full synopsis from Aeon Timeline to a Writer document. 
    '''
    open_src(OdtFullSynopsis.SUFFIX, OdtFullSynopsis.EXTENSION)


def get_charactersheets():
    '''Import character sheets from Aeon Timeline to a Writer document.
    '''
    open_src(OdtCharacterSheets.SUFFIX, OdtCharacterSheets.EXTENSION)


def get_locationsheets():
    '''Import location sheets from Aeon Timeline to a Writer document.
    '''
    open_src(OdtLocationSheets.SUFFIX, OdtLocationSheets.EXTENSION)


def get_report():
    '''Import a full report of the narrative from Aeon Timeline to a Writer document.
    '''
    open_src(OdtReport.SUFFIX, OdtReport.EXTENSION)
