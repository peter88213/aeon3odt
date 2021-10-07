"""Convert Aeon Timeline 3 project data to odt. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from configparser import ConfigParser

from pywriter.odt.odt_proof import OdtProof
from pywriter.odt.odt_manuscript import OdtManuscript
from pywriter.odt.odt_scenedesc import OdtSceneDesc
from pywriter.odt.odt_chapterdesc import OdtChapterDesc
from pywriter.odt.odt_partdesc import OdtPartDesc
from pywriter.odt.odt_xref import OdtXref
from pywriter.ods.ods_scenelist import OdsSceneList
from pywriter.ods.ods_plotlist import OdsPlotList
from pywriter.ods.ods_charlist import OdsCharList
from pywriter.ods.ods_loclist import OdsLocList
from pywriter.ods.ods_itemlist import OdsItemList
from pywriter.odt.odt_characters import OdtCharacters
from pywriter.odt.odt_items import OdtItems
from pywriter.odt.odt_locations import OdtLocations

import uno
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, INFOBOX, WARNINGBOX, ERRORBOX, QUERYBOX
from com.sun.star.beans import PropertyValue

from libreoffice.uno_tools import *
from libreoffice.aeon3odt_uno import Aeon3odtUno
from libreoffice.ui_uno import UiUno

INI_FILE = 'openyw.ini'


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

    # Ask for yWriter 7 project to open:

    csvFile = FilePicker(path=defaultFile)

    if csvFile is None:
        return

    sourcePath = uno.fileUrlToSystemPath(csvFile)
    ywExt = os.path.splitext(sourcePath)[1]

    if not ywExt in ['.csv']:
        msgbox('Please choose a csv file exported by Aeon Timeline 3.',
               'Import from yWriter', type_msg=ERRORBOX)
        return

    # Store selected yWriter project as "last opened".

    newFile = csvFile.replace(ywExt, suffix + newExt)
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
    converter = YwCnvUno()
    converter.ui = UiUno('Import from Aeon Timeline 3')
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)

    if converter.newFile:
        desktop = XSCRIPTCONTEXT.getDesktop()
        doc = desktop.loadComponentFromURL(newFile, "_blank", 0, ())


def get_chapterdesc():
    '''Import chapter descriptions from Aeon 3 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_csv(OdtChapterDesc.SUFFIX, OdtChapterDesc.EXTENSION)


def get_scenedesc():
    '''Import scene descriptions from Aeon 3 to a Writer document
    with invisible chapter and scene markers. 
    '''
    open_csv(OdtSceneDesc.SUFFIX, OdtSceneDesc.EXTENSION)


def get_chardesc():
    '''Import character descriptions from Aeon 3 to a Writer document.
    '''
    open_csv(OdtCharacters.SUFFIX, OdtCharacters.EXTENSION)


def get_locdesc():
    '''Import location descriptions from Aeon 3 to a Writer document.
    '''
    open_csv(OdtLocations.SUFFIX, OdtLocations.EXTENSION)
