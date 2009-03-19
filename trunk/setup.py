from cx_Freeze import setup, Executable

inc=[]
inc.append("sip")
inc.append("PyQt4.QtCore")
inc.append("PyQt4.QtGui")
inc.append("LauePlaneCfg")
inc.append("StereoCfg")

opts=dict(includes=inc,
          icon="icons/clip.ico",
          compressed=True,
          base="Win32GUI",
          append_script_to_exe=True,
          optimize=1)


setup(
        name = "Clip",
        version = "3.0c",
        description = "The Cologne Laue Indexation Program",
        executables = [Executable("clip.py")],
        options={"build_exe": opts})

