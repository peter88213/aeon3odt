"""Provide a converter class for Aeon 3Timeline csv import.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywaeon3.csv_timeline import CsvTimeline

from aeon3odt.odt_full_synopsis import OdtFullSynopsis
from aeon3odt.odt_brief_synopsis import OdtBriefSynopsis
from aeon3odt.odt_chapter_overview import OdtChapterOverview
from aeon3odt.odt_character_sheets import OdtCharacterSheets
from aeon3odt.odt_location_sheets import OdtLocationSheets
from aeon3odt.odt_report import OdtReport


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
