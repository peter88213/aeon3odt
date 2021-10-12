""" Python unit tests for the aeon3odt project.

Test suite for aeon3yw.pyw.

For further information see https://github.com/peter88213/aeon3yw
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copyfile
import zipfile
import os
import unittest

import cnvaeon_stub

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'

# To be placed in TEST_DATA_PATH:
NORMAL_CSV = TEST_DATA_PATH + 'normal.csv'
PARTS_CONTENT = TEST_DATA_PATH + 'parts.xml'
CHAPTERS_CONTENT = TEST_DATA_PATH + 'chapters.xml'
SCENES_CONTENT = TEST_DATA_PATH + 'scenes.xml'
CHARACTERS_CONTENT = TEST_DATA_PATH + 'characters.xml'

# Test data
TEST_CSV = TEST_EXEC_PATH + 'yw7 Sample Project.csv'
TEST_PARTS = TEST_EXEC_PATH + 'yw7 Sample Project_chapter_overview.odt'
TEST_CHAPTERS = TEST_EXEC_PATH + 'yw7 Sample Project_brief_synopsis.odt'
TEST_SCENES = TEST_EXEC_PATH + 'yw7 Sample Project_full_synopsis.odt'
TEST_CHARACTERS = TEST_EXEC_PATH + 'yw7 Sample Project_character_sheets.odt'
ODF_CONTENT = 'content.xml'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def remove_all_testfiles():

    try:
        os.remove(TEST_EXEC_PATH + ODF_CONTENT)

    except:
        pass

    try:
        os.remove(TEST_CSV)
    except:
        pass

    try:
        os.remove(TEST_PARTS)
    except:
        pass

    try:
        os.remove(TEST_CHAPTERS)
    except:
        pass

    try:
        os.remove(TEST_CHARACTERS)
    except:
        pass

    try:
        os.remove(TEST_SCENES)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):

        try:
            os.mkdir(TEST_EXEC_PATH)

        except:
            pass

        remove_all_testfiles()

    def test_chapter_overview(self):
        copyfile(NORMAL_CSV, TEST_CSV)
        cnvaeon_stub.convert_csv(TEST_CSV, '_chapter_overview')

        with zipfile.ZipFile(TEST_PARTS, 'r') as myzip:
            myzip.extract(ODF_CONTENT, TEST_EXEC_PATH)
            myzip.close

        self.assertEqual(read_file(TEST_EXEC_PATH + ODF_CONTENT),
                         read_file(PARTS_CONTENT))

    def test_brief_synopsis(self):
        copyfile(NORMAL_CSV, TEST_CSV)
        cnvaeon_stub.convert_csv(TEST_CSV, '_brief_synopsis')

        with zipfile.ZipFile(TEST_CHAPTERS, 'r') as myzip:
            myzip.extract(ODF_CONTENT, TEST_EXEC_PATH)
            myzip.close

        self.assertEqual(read_file(TEST_EXEC_PATH + ODF_CONTENT),
                         read_file(CHAPTERS_CONTENT))

    def test_full_synopsis(self):
        copyfile(NORMAL_CSV, TEST_CSV)
        cnvaeon_stub.convert_csv(TEST_CSV, '_full_synopsis')

        with zipfile.ZipFile(TEST_SCENES, 'r') as myzip:
            myzip.extract(ODF_CONTENT, TEST_EXEC_PATH)
            myzip.close

        self.assertEqual(read_file(TEST_EXEC_PATH + ODF_CONTENT),
                         read_file(SCENES_CONTENT))

    def test_character_sheets(self):
        copyfile(NORMAL_CSV, TEST_CSV)
        cnvaeon_stub.convert_csv(TEST_CSV, '_character_sheets')

        with zipfile.ZipFile(TEST_CHARACTERS, 'r') as myzip:
            myzip.extract(ODF_CONTENT, TEST_EXEC_PATH)
            myzip.close

        self.assertEqual(read_file(TEST_EXEC_PATH + ODF_CONTENT),
                         read_file(CHARACTERS_CONTENT))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
