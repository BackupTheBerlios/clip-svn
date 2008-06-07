#include <StereoProjector.h>
#include <cmath>

StereoProjector::StereoProjector(ObjectStore* crystals, QObject* parent): Projector(crystals, parent) {
    setStereoProjectionDir(Vec3D(1,0,0));
};


QPointF StereoProjector::scattered2det(const Vec3D &v) {
    return normal2det(scattered2normal(v));
}

Vec3D StereoProjector::det2scattered(const QPointF& p) {
    return normal2scattered(det2normal(p));
}

QPointF StereoProjector::normal2det(const Vec3D& n) {
    Vec3D v=R*n;
    double s=1.0+v.x();
    if (s<1e-5)
        return QPointF();
    return QPointF(v.y()/s, v.z()/s);
}


Vec3D StereoProjector::det2normal(const QPointF& p) {
    double x=p.x();
    double y=p.y();
    double n=1.0/(x*x+y*y+1.0);
    return Vec3D(n*(x*x+y*y-1.0), 2*x*n, 2*y*n);    
}


void StereoProjector::setStereoProjectionDir(const Vec3D &v) {
    dir = v;
    if (dir==Vec3D(1,0,0)) {
        R=Mat3D();
    } else if (dir==Vec3D(-1,0,0)) {
        R=Mat3D();
        *R.at(0,0)=-1.0;
        *R.at(2,2)=-1.0;
    } else {
        Vec3D p=Vec3D(1, 0, 0)%dir;
        p.normalize();
        R=Mat3D(p, -acos(dir.x()));
    }
    reflectionsUpdated();
}

bool StereoProjector::project(const Reflection &r) {
    Vec3D v=R*r.normal;
    double s=1.0+v.x();
    if (s<1e-5)
        return false;
    projectedPoints.push_back(QPointF(v.y()/s, v.z()/s));
    return true;
}

