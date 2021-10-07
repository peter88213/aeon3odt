"""Provide a class for ODT part descriptions export.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.odt.odt_file import OdtFile


class OdtVeryBriefSynopsis(OdtFile):
    """ODT part and chapter summaries file representation.

    Export a very brief synopsis.
    """

    DESCRIPTION = 'Chapter descriptions'
    SUFFIX = '_parts'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Desc</text:h>
'''

    chapterTemplate = '''<text:p text:style-name="Text_20_body">$Desc</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER
