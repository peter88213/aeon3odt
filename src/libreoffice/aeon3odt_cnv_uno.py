"""User interface for the converter: UNO facade

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from aeon3odt.aeon3odt_converter import Aeon3odtConverter


class Aeon3odtCnvUno(Aeon3odtConverter):
    """Converter for yWriter project files.
    Variant with UNO UI.
    """

    def export_from_yw(self, sourceFile, targetFile):
        """Method for conversion from yw to other.
        Show only error messages.
        """
        message = self.convert(sourceFile, targetFile)

        if message.startswith('SUCCESS'):
            self.newFile = targetFile.filePath

        else:
            self.ui.set_info_how(message)
