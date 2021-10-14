# Please note:

Since Python scripts placed in LibreOffice extensions are very limited in importing non-standard modules, all modules used from the  _PyWriter_  library first have to be "inlined" by "build" scripts.

Location of the  _paeon_  library: https://github.com/peter88213/paeon
Location of the  _PyWriter_  library: https://github.com/peter88213/PyWriter

It is advised to clone these projects at the same directory level as the  *yw-cnv*  project. So the build scripts can generate the  *yw-cnv*  scripts.

The *cnvaeon* macro only works in the LibreOffice Python context. In order to execute tests in the development environment, there is the *cnvaeon_stub_* script that has to be keppt up date with the *cnvaeon_* script.