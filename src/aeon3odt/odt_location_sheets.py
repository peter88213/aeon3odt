"""Provide a class for ODT descriptions export.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.odt.odt_file import OdtFile


class OdtLocationSheets(OdtFile):
    """ODT location descriptions file representation.

    Export a location sheet.
    """

    DESCRIPTION = 'Location sheets'
    SUFFIX = '_location_sheets'

    fileHeader = OdtFile.CONTENT_XML_HEADER

    locationTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Title$AKA</text:h>
<text:p text:style-name="Text_20_body"><text:span text:style-name="Emphasis">$Tags</text:span></text:p>

<text:p text:style-name="Text_20_body" />
<text:p text:style-name="Text_20_body">$Desc</text:p>
'''

    fileFooter = OdtFile.CONTENT_XML_FOOTER

    def get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section. 
        """
        locationMapping = OdtFile.get_locationMapping(self, lcId)

        if self.locations[lcId].aka:
            locationMapping['AKA'] = ' ("' + self.locations[lcId].aka + '")'

        return locationMapping
