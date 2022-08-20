""" Build  a stub for the aeon3odt unit tests.

For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}cnvaeon_stub_.py'
TARGET_FILE = f'{BUILD}cnvaeon_stub.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'aeon3odtlib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'aeon3ywlib', '../../aeon3yw/src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../src/')
    print('Done.')


if __name__ == '__main__':
    main()
