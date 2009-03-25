cd CSource
mingw32-make
cd ../PyBindings
del ToolBox.pyd
mingw32-make
copy ToolBox.pyd ..\..
cd ..
