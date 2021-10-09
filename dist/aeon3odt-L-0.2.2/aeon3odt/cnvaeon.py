"""Convert Aeon Timeline 3 project data to odt. 

Version 0.2.2

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from configparser import ConfigParser

from aeon3odt.odt_full_synopsis import OdtFullSynopsis
from aeon3odt.odt_brief_synopsis import OdtBriefSynopsis
from aeon3odt.odt_chapter_overview import OdtChapterOverview
from aeon3odt.odt_character_sheets import OdtCharacterSheets
from aeon3odt.odt_location_sheets import OdtLocationSheets
from aeon3odt.odt_report import OdtReport

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


from aeon3odt.csv_converter import CsvConverter


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
