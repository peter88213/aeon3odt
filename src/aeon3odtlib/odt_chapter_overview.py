"""Provide a class for ODT part descriptions export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odtlib.odt_aeon import OdtAeon


class OdtChapterOverview(OdtAeon):
    """ODT part and chapter summaries file representation.

    Export a very brief synopsis.
    """
    DESCRIPTION = 'Chapter overview'
    SUFFIX = '_chapter_overview'

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Desc</text:h>
'''

    _chapterTemplate = '''<text:p text:style-name="Text_20_body">$Desc</text:p>
'''
