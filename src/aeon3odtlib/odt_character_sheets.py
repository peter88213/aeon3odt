"""Provide a class for ODT character descriptions export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odtlib.odt_aeon import OdtAeon


class OdtCharacterSheets(OdtAeon):
    """ODT character descriptions file representation.

    Export a character sheet.
    """

    DESCRIPTION = 'Character sheets'
    SUFFIX = '_character_sheets'

    _characterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$FullName$AKA</text:h>

<text:p text:style-name="Text_20_body"><text:span text:style-name="Emphasis">$Tags</text:span></text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Bio</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Goals</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Desc</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Notes</text:p>

'''
