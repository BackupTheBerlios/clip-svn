#include <projector.h>
#import <cmath>
#import <iostream>

using namespace std;

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
    
    unsigned int projected=0;
    unsigned int noproj=0;
    std::vector<Reflection>& r = crystal->getReflectionList();
    int n=0;
    int i=0;

    //cout << "refUpdate" << n << " " << i <<endl;
    cout << "Start: " << projected << " " << projectedItems.size() << " " << r.size() << " " << i << " " << n << endl;
    
    for (; i<r.size() and n<projectedItems.size(); i++) {
        //cout << "rewrite " << i << " " << n << endl;
        if (project(r[i], projectedItems.at(n))) {
            n++;
            projected++;
        } else {
            noproj++;
        }
    }
    cout << "rewrite: " << projected << " " << projectedItems.size() << " " << r.size() << " " << i << " " << n << " " << noproj << endl;
    QGraphicsItem* item;
    for (; n<projectedItems.size(); n++) {
        //cout << "del" << n  << endl;
        item = projectedItems.takeLast();
        scene.removeItem(item);
        delete item;
    }
    cout << "del:" << projected << " " << projectedItems.size() << " " << r.size() << " " << i << " " << n << endl;


    //cout << "Afterrewrite" << i << " " << n << endl;
    item = itemFactory();
    for (; i<r.size(); i++) {
        //cout << "add" << i  << endl;
        if (project(r[i], item))  {
            projectedItems.append(item);
            scene.addItem(item);
            item = itemFactory();
            projected++;
        }
    }
    delete item;
    cout << "add:" << projected << " " << projectedItems.size() << " " << r.size() << " " << i << " " << n << endl;
    
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
