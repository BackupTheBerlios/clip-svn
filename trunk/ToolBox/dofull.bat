cd CSource
mingw32-make
copy libToolBox.a ../PyBindings
cd ../PyBindings
python configure.py
mingw32-make
copy ToolBox.pyd ..\..
cd ..
