"""Provide a converter class for universal import and export.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.pywriter_globals import ERROR
from aeon3odtlib.aeon3odt_converter import Aeon3odtConverter


class Aeon3odtCnvUno(Aeon3odtConverter):
    """A converter for universal import and export.
    
    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.

    Support yWriter 7 projects and most of the Novel subclasses 
    that can be read or written by OpenOffice/LibreOffice.
    - No message in case of success when converting from yWriter.
    """

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Show only error messages.
        Overrides the superclass method.
        """
        message = self.convert(source, target)
        if message.startswith(ERROR):
            self.ui.set_info_how(message)
        else:
            self.newFile = target.filePath
