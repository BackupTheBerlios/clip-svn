import os
import sipconfig
from PyQt4 import pyqtconfig

build_file = 'ToolBox.sbf'

#config=sipconfig.Configuration()
config = pyqtconfig.Configuration()


qt_sip_flags = config.pyqt_sip_flags

# Run SIP to generate the code.  Note that we tell SIP where to find the qt
# module's specification files using the -I flag.
s=" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I", config.pyqt_sip_dir, qt_sip_flags, "ToolBox.sip"])
print s
os.system(s)

makefile = sipconfig.SIPModuleMakefile(config, build_file)

makefile.extra_libs=['QtCore4', 'QtGui4', 'ToolBox']
makefile.extra_lib_dirs=['..', '.',  'c:\\Programme\\Python25\\PyQt4\\bin',  '../CSource']
makefile.extra_include_dirs=['..', '../CSource', 'C:\\Programme\\Qt\\4.4.0\\include',  'C:\\Programme\\Qt\\4.4.0\\include\\QtCore', 'C:\\Programme\\Qt\\4.4.0\\include\\QtGui']
#makefile.extra_lflags=['ToolBox.a']

makefile.generate()
