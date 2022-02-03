"""Provide a class for ODT project report export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odt.odt_aeon import OdtAeon


class OdtReport(OdtAeon):
    """ODT scene summaries file representation.

    Export a full synopsis.
    """

    DESCRIPTION = 'Project report'
    SUFFIX = '_report'

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Title – $Desc</text:h>
'''

    _chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title – $Desc</text:h>
'''

    _sceneTemplate = '''<text:h text:style-name="Heading_20_3" text:outline-level="3">Scene $SceneNumber – ${Title}</text:h>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Tags: </text:span>$Tags</text:p>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Location: </text:span>$Locations</text:p>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Date/Time/Duration: </text:span>$ScDate $ScTime $Duration</text:p>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Participants: </text:span>$Characters</text:p>
<text:p text:style-name="Text_20_body">$Desc</text:p>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Notes:</text:span>$Notes</text:p>
'''

    _characterSectionHeading = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">Characters</text:h>
'''

    _characterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$FullName$AKA</text:h>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Tags: </text:span>$Tags</text:p>
<text:p text:style-name="Text_20_body">$Bio</text:p>
<text:p text:style-name="Text_20_body">$Goals</text:p>
<text:p text:style-name="Text_20_body">$Desc</text:p>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Notes: </text:span>$Notes</text:p>
'''

    _locationSectionHeading = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">Locations</text:h>
'''

    _locationTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$AKA</text:h>
<text:p text:style-name="Text_20_body_20_indent"><text:span text:style-name="Strong_20_Emphasis">Tags: </text:span>$Tags</text:p>
<text:p text:style-name="Text_20_body">$Desc</text:p>
'''
