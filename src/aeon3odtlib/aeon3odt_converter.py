"""Provide a converter class for Aeon 3Timeline csv import.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from aeon3ywlib.csv_timeline3 import CsvTimeline3
from aeon3ywlib.json_timeline3 import JsonTimeline3
from aeon3odtlib.odt_full_synopsis import OdtFullSynopsis
from aeon3odtlib.odt_brief_synopsis import OdtBriefSynopsis
from aeon3odtlib.odt_chapter_overview import OdtChapterOverview
from aeon3odtlib.odt_character_sheets import OdtCharacterSheets
from aeon3odtlib.odt_location_sheets import OdtLocationSheets
from aeon3odtlib.odt_report import OdtReport


class Aeon3odtConverter(YwCnvFf):
    """A converter for universal export from a yWriter 7 project.

    Overrides the superclass constants EXPORT_SOURCE_CLASSES,
    EXPORT_TARGET_CLASSES.
    """
    EXPORT_SOURCE_CLASSES = [CsvTimeline3, JsonTimeline3]
    EXPORT_TARGET_CLASSES = [OdtFullSynopsis,
                             OdtBriefSynopsis,
                             OdtChapterOverview,
                             OdtCharacterSheets,
                             OdtLocationSheets,
                             OdtReport,
                             ]
