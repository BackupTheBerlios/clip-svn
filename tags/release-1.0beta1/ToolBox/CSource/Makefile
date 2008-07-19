
PLAINSRC=vec3D mat3D ImageTools BezierCurve FitObject
QOBJSRC=crystal ObjectStore projector StereoProjector LauePlaneProjector SignalingEllipse Indexer


CXXFLAGS=-O4 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -I/usr/include/qt4 -I/usr/include/qt4 -I. -fPIC -D__DEBUG__
MOC=moc-qt4
MOC=C:\Programme\Qt\4.4.0\bin\moc

libToolBox.a:  $(PLAINSRC:=.o)  $(QOBJSRC:=.o) $(QOBJSRC:=.moc.o)
	ar rcs $@ $^

%.moc.cpp: %.h
	$(MOC) $^ > $@

libToolBox.so:  $(SRC:.cpp=.o)
	$(CXX) -shared $^ -o $@

