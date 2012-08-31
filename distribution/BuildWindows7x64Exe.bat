echo "Building the gado control software for Windows 7 x64..."

:: Call the python build script
python BuildGadoExe.py py2exe

::Move test image into build directory so we don't crash
::(used in the image displays before we grab real images)
copy ..\src\test.jpg windows_7_x64_gado

::Done
echo "Done."