"""Convert Aeon Timeline 3 project data to odt. 

Unit test stub

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.ui.ui import Ui
from aeon3odt.aeon3odt_converter import Aeon3odtConverter

SETTINGS = dict(
    part_number_prefix='Part',
    chapter_number_prefix='Chapter',
    type_event='Event',
    type_character='Character',
    type_location='Location',
    type_item='Item',
    character_label='Participant',
    location_label='Location',
    item_label='Item',
    part_desc_label='Label',
    chapter_desc_label='Label',
    scene_desc_label='Summary',
    scene_title_label='Label',
    notes_label='Notes',
    tag_label='Tags',
    viewpoint_label='Viewpoint',
    character_bio_label='Summary',
    character_aka_label='Nickname',
    character_desc_label1='Characteristics',
    character_desc_label2='Traits',
    character_desc_label3='',
    location_desc_label='Summary',
)


def convert_csv(sourcePath, suffix=''):
    ui = Ui('')
    converter = Aeon3odtConverter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    kwargs.update(SETTINGS)
    converter.run(sourcePath, **kwargs)
