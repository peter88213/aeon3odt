""" Build  a stub for the aeon3odt unit tests.
        

For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys 
sys.path.insert(0, f'{os.getcwd()}/../../PyWriter/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}cnvaeon_stub_.py'
TARGET_FILE = f'{BUILD}cnvaeon_stub.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'aeon3odt', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywaeon3', '../../aeon3yw/src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../../PyWriter/src/')
    print('Done.')


if __name__ == '__main__':
    main()
