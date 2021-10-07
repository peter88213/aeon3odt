"""Provide a class for ODT project report export.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.odt.odt_file import OdtFile


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
