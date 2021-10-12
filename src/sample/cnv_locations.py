"""Import Aeon Timeline 3 location sheets. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
SUFFIX = '_location_sheets'

SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
    type_character='Character',
    type_location='Location',
    type_item='Item',
    part_desc_label='Label',
    chapter_desc_label='Label',
    scene_desc_label='Summary',
    scene_title_label='Label',
    notes_label='Notes',
    tag_label='Tags',
    location_label='Location',
    item_label='Item',
    character_label='Participant',
    viewpoint_label='Viewpoint',
    character_bio_label='Summary',
    character_aka_label='Nickname',
    character_desc_label1='Characteristics',
    character_desc_label2='Traits',
    character_desc_label3='',
    location_desc_label='Summary',
)

import sys

from pywriter.ui.ui_tk import UiTk
from aeon3odt.csv_converter import CsvConverter


def run(sourcePath, suffix=''):
    ui = UiTk('Aeon 3 import')
    converter = CsvConverter()
    converter.ui = ui
    kwargs = {'suffix': SUFFIX}
    kwargs.update(SETTINGS)
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
