::This is the batch file that builds the executable for Windows 7/Vista, both 32 and 64-bit
echo "Building the gado control software for Windows 7/Vista (x32 & x64)..."

::If it exists, delete the dist directory
rmdir /s /q windows_(Vista_7)_gado

::Create temp directories to hold source for building
md gado
md lib

::Copy over temp source files
xcopy ..\src\gado gado /s /q /y
xcopy ..\src\lib lib /s /q /y

copy ..\src\main.py .
copy ..\src\lib\Pmw .

:: Call the python build script
python BuildGadoExe.py py2exe

::Move test image into build directory so we don't crash
::(used in the image displays before we grab real images)
copy ..\src\test.jpg windows_(Vista_7)_gado

::Delete the build folders, it only clutters things
rmdir /s /q build
rmdir /s /q gado
rmdir /s /q lib
del main.py
del Pmw.py
del PmwBlt.py
del PmwColor.py

::Done
echo "Done."