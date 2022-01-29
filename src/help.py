"""Show html help files. 

This is a workaround for the apparently not working help interface of LibreOffice.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/aeon3odt
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

import os
import webbrowser


def show_help():
    scriptLocation = os.path.dirname(__file__)
    helpFile = f'{scriptLocation}/help.html'
    webbrowser.open(helpFile)
