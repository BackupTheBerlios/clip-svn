
SRC=vec3D.cpp mat3D.cpp ImageTools.cpp crystal.cpp
MOCS=crystal.moc.cpp


#CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -fPIC -D__DEBUG__
CXXFLAGS=-O2 -I/usr/include/qt4 -I/usr/include/qt4 -I. -fPIC  -D__DEBUG__
#CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -fPIC

libToolBox.a:  $(SRC:.cpp=.o) $(MOCS:.cpp=.o)
	ar rcs $@ $^

%.moc.cpp: %.h
	moc-qt4 $^ > $@

libToolBox.so:  $(SRC:.cpp=.o)
	$(CXX) -shared $^ -o $@

