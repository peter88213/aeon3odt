"""Import Aeon Timeline 3 scene descriptions. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
SUFFIX = '_full_synopsis'

SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
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
