"""Provide a class for ODT descriptions export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odtlib.odt_aeon import OdtAeon


class OdtLocationSheets(OdtAeon):
    """ODT location descriptions file representation.

    Export a location sheet.
    """

    DESCRIPTION = 'Location sheets'
    SUFFIX = '_location_sheets'

    _locationTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$AKA</text:h>
<text:p text:style-name="Text_20_body"><text:span text:style-name="Emphasis">$Tags</text:span></text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Desc</text:p>
'''
