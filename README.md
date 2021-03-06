# The aeon3odt extension for LibreOffice: Import Aeon Timeline 3 project data

For more information, see the [project homepage](https://peter88213.github.io/aeon3odt) with description and download instructions.

## Development

*aeon3odt* depends on the [pywriter](https://github.com/peter88213/PyWriter) and the [aeon3yw](https://github.com/peter88213/aeon3yw) libraries which must be present in your file system. It is organized as an Eclipse PyDev project. The official release branch on GitHub is *main*.

### Mandatory directory structure for building the application script

```
.
├── PyWriter/
│   └── src/
│       └── pywriter/
├── aeon3yw/
│   └── src/
│       └── aeon3ywlib/
└── aeon3odt/
    ├── src/
    ├── test/
    └── tools/
        └── build.xml
```

### Conventions

- Minimum Python version is 3.6. 
- The Python **source code formatting** follows widely the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide, except the maximum line length, which is 120 characters here.

### Development tools

- [Python](https://python.org) version 3.9
- [Eclipse IDE](https://eclipse.org) with [PyDev](https://pydev.org) and [EGit](https://www.eclipse.org/egit/)
- [Apache Ant](https://ant.apache.org/) for building the application script
- [pandoc](https://pandoc.org/) for building the HTML help pages

## Credits

- [OpenOffice Extension Compiler](https://wiki.openoffice.org/wiki/Extensions_Packager#Extension_Compiler) by Bernard Marcelly.

## License

This extension is distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
