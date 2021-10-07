"""Convert Aeon Timeline 3 project data to odt. 

Unit test stub

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.ui.ui import Ui
from aeon3odt.csv_converter import CsvConverter

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


def convert_csv(sourcePath, suffix=''):
    ui = Ui('')
    converter = CsvConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    kwargs.update(SETTINGS)
    converter.run(sourcePath, **kwargs)
