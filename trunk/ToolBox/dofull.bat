cd CSource
mingw32-make
cd ../PyBindings
python configure.py
mingw32-make
copy ToolBox.pyd ..\..
cd ..
