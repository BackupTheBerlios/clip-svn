#include <projector.h>
#import <cmath>
#import <iostream>
#import <QtCore/QTimer>

using namespace std;

Projector::Projector(QObject *parent): QObject(parent), crystal(), scene(this), projectedItems(), decorationItems() {
    lowerLambda=1.0;
    upperLambda=100.0;
    QTimer::singleShot(0, this, SLOT(decorateScene()));
};

Projector::Projector(const Projector &p): crystal(p.crystal), scene(this),projectedItems(), decorationItems()  {
    lowerLambda=p.lowerLambda;
    upperLambda=p.upperLambda;
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
    
    std::vector<Reflection>& r = crystal->getReflectionList();
    int n=0;
    int i=0;

    for (; i<r.size() and n<projectedItems.size(); i++) {
        if (project(r[i], projectedItems.at(n))) {
            n++;
        }
    }
    #ifdef __DEBUG__
    int rewritten=n;
    int deleted=projectedItems.size()-n;
    int added=r.size()-i;
    int projected=n;
    #endif
    QGraphicsItem* item;
    for (; n<projectedItems.size(); n++) {
        item = projectedItems.takeLast();
        scene.removeItem(item);
        delete item;
    }


    item = itemFactory();
    for (; i<r.size(); i++) {
        if (project(r[i], item))  {
            projectedItems.append(item);
            scene.addItem(item);
            item = itemFactory();
            #ifdef __DEBUG__
            projected++;
            #endif
        }
    }
    delete item;
    
    #ifdef __DEBUG__
    cout << "rewrite:" << rewritten;
    cout << " det:" << deleted;
    cout << " add:" << added;
    cout << " projected:" << projected;
    cout << " itemSize:" << projectedItems.size() << endl;
    #endif
       
    emit projectedPointsUpdated();
}


Vec3D Projector::normal2scattered(const Vec3D &v) {
    double x=v.x();
    if (x<=0.0) 
        return Vec3D();
    double y=v.y();
    double z=v.z();
    return Vec3D(2*x*x-1.0, 2.0*x*y, 2.0*x*z);
}

Vec3D Projector::scattered2normal(const Vec3D& v) {
    double x=v.x();
    double y=v.y();
    double z=v.z();

    x=sqrt(0.5*(x+1.0));
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


