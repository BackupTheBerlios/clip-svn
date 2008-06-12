#include <projector.h>
#import <cmath>

Projector::Projector(QObject *parent): QObject(parent), crystal(), scene(this), projectedItems(), decorationItems() {
    lowerLambda=1.0;
    upperLambda=100.0;
    decorateScene();
};

Projector::Projector(const Projector &p): crystal(p.crystal), scene(this),projectedItems(), decorationItems()  {
    lowerLambda=p.lowerLambda;
    upperLambda=p.upperLambda;
    decorateScene();
}; 


void Projector::connectToCrystal(Crystal *c) {
    if (not crystal.isNull()) {
        disconnect(this, 0, crystal, 0);
        disconnect(crystal, 0, this, 0);
    }
    crystal=c;
    crystal->addProjector(this);
    connect(crystal, SIGNAL(reflectionsUpdate()), this, SLOT(reflectionsUpdated()));
    reflectionsUpdated();
}
    

double Projector::lowerWavelength() {
    return lowerLambda;
}

double Projector::upperWavelength() {
    return upperLambda;
}


void Projector::setWavelength(double lower, double upper)  {
    if ((lower<upper) and ((lower!=lowerLambda) or (upper!=upperLambda))) {
        lowerLambda=lower;
        upperLambda=upper;
        emit wavelengthUpdated();
    }
}

void Projector::reflectionsUpdated() {
    if (crystal.isNull()) 
        return;
    
    std::vector<Reflection>&   r = crystal->getReflectionList();
    unsigned int n=projectedItems.size();
    unsigned int i=r.size();
    while (i and n) {
        if (project(r[i], projectedItems.at(n))) 
            n--;
        i--;
    }

    QGraphicsItem* item = itemFactory();
    for (; i-- ; ) {
        if (project(r[i], item))  {
            projectedItems.append(item);
            scene.addItem(item);
            item = itemFactory();
        }
    }
    delete item;
    
    for (; n--; ) {
        item = projectedItems.takeFirst();
        scene.removeItem(item);
        delete item;
    }
    emit projectedPointsUpdated();
}


Vec3D Projector::normal2scattered(const Vec3D &v) {
    double x=v.x();
    if (x<=0.0) 
        return Vec3D();
    double y=v.y();
    double z=v.z();
    return Vec3D(x*x-y*y-z*z, 2.0*x*y, 2.0*x*z);
}

Vec3D Projector::scattered2normal(const Vec3D& v) {
    double x=v.x();
    double y=v.y();
    double z=v.z();
    x=sqrt(0.5*(x-1.0));
    if (x==0.0) 
        return Vec3D();
    return Vec3D(x, 0.5*y/x, 0.5*z/x);
}

void Projector::addRotation(const Vec3D& axis, double angle) {
    if (not crystal.isNull())
        crystal->addRotation(axis, angle);
}

void Projector::addRotation(const Mat3D& M) {
    if (not crystal.isNull())
        crystal->addRotation(M);
}

void Projector::setRotation(const Mat3D& M) {
    if (not crystal.isNull())
        crystal->setRotation(M);
}

QGraphicsScene* Projector::getScene() {
    return &scene;
}

void Projector::decorateScene() {
}
