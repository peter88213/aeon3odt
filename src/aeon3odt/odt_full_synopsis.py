"""Provide a class for ODT scene descriptions export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odt.odt_aeon import OdtAeon


class OdtFullSynopsis(OdtAeon):
    """ODT scene summaries file representation.

    Export a full synopsis.
    """

    DESCRIPTION = 'Full synopsis'
    SUFFIX = '_full_synopsis'

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
