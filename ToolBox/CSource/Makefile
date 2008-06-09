
PLAINSRC=vec3D mat3D ImageTools
QOBJSRC=crystal ObjectStore projector StereoProjector


CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -I. -fPIC -D__DEBUG__
#CXXFLAGS=-O2 -I/usr/include/qt4 -I/usr/include/qt4 -I. -fPIC  -D__DEBUG__
#CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -fPIC
#MOC=moc-qt4
MOC=C:\Programme\Qt\4.4.0\bin\moc

libToolBox.a:  $(PLAINSRC:=.o)  $(QOBJSRC:=.o) $(QOBJSRC:=.moc.o)
	ar rcs $@ $^

%.moc.cpp: %.h
	$(MOC) $^ > $@

libToolBox.so:  $(SRC:.cpp=.o)
	$(CXX) -shared $^ -o $@

