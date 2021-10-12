"""Provide a class for ODT character descriptions export.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.odt.odt_file import OdtFile


class OdtCharacterSheets(OdtFile):
    """ODT character descriptions file representation.

    Export a character sheet.
    """

    DESCRIPTION = 'Character sheets'
    SUFFIX = '_character_sheets'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    characterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$FullName$AKA</text:h>

<text:p text:style-name="Text_20_body"><text:span text:style-name="Emphasis">$Tags</text:span></text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Bio</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Goals</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Desc</text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body"><text:span text:style-name="Emphasis">$Notes</text:span></text:p>

'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER

    def get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section. 
        """
        characterMapping = OdtFile.get_characterMapping(self, crId)

        if self.characters[crId].aka:
            characterMapping['AKA'] = ' ("' + self.characters[crId].aka + '")'

        if self.characters[crId].fullName:
            characterMapping['FullName'] = '/' + self.characters[crId].fullName

        return characterMapping
