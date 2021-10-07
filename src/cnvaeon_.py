"""Convert Aeon Timeline 3 project data to odt. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from configparser import ConfigParser

from aeon3odt.odt_full_synopsis import OdtFullSynopsis
from aeon3odt.odt_brief_synopsis import OdtBriefSynopsis
from aeon3odt.odt_very_brief_synopsis import OdtVeryBriefSynopsis
from aeon3odt.odt_character_sheets import OdtCharacterSheets
from aeon3odt.odt_location_sheets import OdtLocationSheets
from aeon3odt.odt_report import OdtReport

import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.beans import PropertyValue

from libreoffice.uno_tools import *
from libreoffice.csv_cnv_uno import CsvCnvUno
from libreoffice.ui_uno import UiUno

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


def get_partdesc():
    '''Import part descriptions from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtVeryBriefSynopsis.SUFFIX, OdtVeryBriefSynopsis.EXTENSION)


def get_chapterdesc():
    '''Import chapter descriptions from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtBriefSynopsis.SUFFIX, OdtBriefSynopsis.EXTENSION)


def get_scenedesc():
    '''Import scene descriptions from Aeon 3 to a Writer document. 
    '''
    open_csv(OdtFullSynopsis.SUFFIX, OdtFullSynopsis.EXTENSION)


def get_chardesc():
    '''Import character descriptions from Aeon 3 to a Writer document.
    '''
    open_csv(OdtCharacterSheets.SUFFIX, OdtCharacterSheets.EXTENSION)


def get_locdesc():
    '''Import location descriptions from Aeon 3 to a Writer document.
    '''
    open_csv(OdtLocationSheets.SUFFIX, OdtLocationSheets.EXTENSION)


def get_report():
    '''Import a full report of the narrative from Aeon 3 to a Writer document.
    '''
    open_csv(OdtReport.SUFFIX, OdtReport.EXTENSION)
