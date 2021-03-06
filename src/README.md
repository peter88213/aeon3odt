# Please note:

Since Python scripts placed in LibreOffice extensions are very limited in importing non-standard modules, all modules used from the  *pywriter* and *aeon3ywlib* library first have to be "inlined" by *build* scripts.

- Location of the  **aeon3ywlib**  library: https://github.com/peter88213/aeon3yw
- Location of the  **PyWriter**  library: https://github.com/peter88213/PyWriter

It is advised to clone these projects at the same directory level as the  *aeon3odt*  project and set a project reference to it. So the build scripts can generate the  *cnvaeon*  script.

The *cnvaeon* macro only works in the LibreOffice *UNO* context. In order to execute tests in the development environment, there is the *cnvaeon_stub_* script that has to be kept up date with the *cnvaeon_* script.