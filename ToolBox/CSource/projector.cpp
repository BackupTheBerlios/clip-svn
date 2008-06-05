#include <projector.h>


Projector::Projector(ObjectStore *c, QObject *parent): QObject(parent), crystal(), pojectedPoints() {
        crystalStore = *c;
};


void Projector::connectToCrystal(Crystal *c) {
    if (not crystal.isNull()) {
        disconnect(this, 0, crystal, 0);
        disconnect(crystal, 0, this, 0);
    }
    crystal=c;
    crystal->addProjector(this);
    connect(crystal, SIGNAL(reflectionsUpdate()), this, SLOT(reflectionsUpdated()));
}
    

double Projector::lowerWavelength() {
    return lower;
}

double Projector::upperWavelength() {
    return upper;
}


void Projector::setWavelength(double lower, double upper)  {
    if (lower<upper) and ((lower!=lowerLambda) or (upper!=upperLambda)) {
        lowerLambda=lower;
        upperlambda=upper;
        emit wavelengthUpdated();
    }
}

void reflectionsUpdated() {
    // TODO: Mach was
}


Vec3D Projector::normal2scattered(const Vec3D &v) {
    double x=v.x();
    double y=v.y();
    double z=v.z();
    return Vec3D(x*x-y*y-z*z, 2.0*x*y, 2.0*x*z);
}

Vec3D Projector::scattered2normal(const Vec3D &v) {
    //TODO: invert
}
