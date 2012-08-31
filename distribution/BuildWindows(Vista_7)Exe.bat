::This is the batch file that builds the executable for Windows 7/Vista, both 32 and 64-bit
echo "Building the gado control software for Windows 7/Vista (x32 & x64)..."

:: Call the python build script
python BuildGadoExe.py py2exe

::Move test image into build directory so we don't crash
::(used in the image displays before we grab real images)
copy ..\src\test.jpg windows_(Vista_7)_gado

::Delete the build folder, it only clutters things
rmdir /s /q build

::Done
echo "Done."