# Please note:

Since Python scripts placed in LibreOffice extensions are very limited in importing non-standard modules, all modules used from the  *pywriter* and *aeon3ywlib* library first have to be "inlined" by *build* scripts.

The *cnvaeon* macro only works in the LibreOffice *UNO* context. In order to execute tests in the development environment, there is the *cnvaeon_stub_* script that has to be kept up date with the *cnvaeon_* script.