"""Provide a class for ODT chapter descriptions export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odtlib.odt_aeon import OdtAeon


class OdtBriefSynopsis(OdtAeon):
    """ODT chapter summaries snf scene titles file representation.

    Export a brief synopsis.
    """

    DESCRIPTION = 'Brief synopsis'
    SUFFIX = '_brief_synopsis'

    _partTemplate = '''<text:h text:style-name="Heading_20_1" text:outline-level="1">$Desc</text:h>
'''

    _chapterTemplate = '''<text:h text:style-name="Heading_20_2" text:outline-level="2">$Desc</text:h>
'''

    _sceneTemplate = '''<text:p text:style-name="Text_20_body">$Title</text:p>
'''
