
SRC=vec3D.cpp mat3D.cpp ImageTools.cpp

CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -fPIC -D__DEBUG__
#CXXFLAGS=-O2 -I/usr/include/qt4 -IC:\Programme\Qt\4.4.0\include -fPIC

libToolBox.a:  $(SRC:.cpp=.o)
	ar rcs $@ $^

%.moc.cpp: %.h
	moc-qt4 $^ > $@

libToolBox.so:  $(SRC:.cpp=.o)
	$(CXX) -shared $^ -o $@

