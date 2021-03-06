#include <StereoProjector.h>
#include <cmath>
#include <QtGui/QGraphicsEllipseItem>
#include <iostream>

using namespace std;

StereoProjector::StereoProjector(QObject* parent): Projector(parent), localCoordinates() {
    setWavevectors(0.0, 1.5*M_1_PI);
    scene.setSceneRect(QRectF(-1.0, -1.0, 2.0, 2.0));
};


QPointF StereoProjector::scattered2det(const Vec3D &v, bool* b) const {
    if (b) {
        Vec3D v(scattered2normal(v,b));
        if (*b) {
            return normal2det(v,b);
        } else {
            return QPointF();
        }
    }
    return normal2det(scattered2normal(v));
}

Vec3D StereoProjector::det2scattered(const QPointF& p, bool* b) const {
    if (b) {
        Vec3D v(det2normal(p,b));
        if (*b) {
            return normal2scattered(v,b);
        } else {
            return Vec3D();
        }
    }
    return normal2scattered(det2normal(p));
}

QPointF StereoProjector::normal2det(const Vec3D& n, bool* b) const {
    Vec3D v=localCoordinates*n;
    double s=1.0+v.x();
    if (s<1e-5) {
        if (b) *b=false;
        return QPointF();
    }
    if (b) *b=true;
    return QPointF(v.y()/s, v.z()/s);
}


Vec3D StereoProjector::det2normal(const QPointF& p, bool* b) const {
    double x=p.x();
    double y=p.y();
    double n=1.0/(x*x+y*y+1.0);
    if (b) *b=true;
    return localCoordinates.transposed()*Vec3D(n*(1.0-x*x-y*y), 2*x*n, 2*y*n);    
}


bool StereoProjector::project(const Reflection &r, QGraphicsItem* item) {
    bool doesReflect=false;
    for (unsigned int i=0; i<r.orders.size(); i++) {
        unsigned int n=r.orders[i];
        if ((QminVal<=n*r.Q) and (n*r.Q<=QmaxVal)) {
            doesReflect=true;
            break;
        }
    }
    if (not doesReflect)
        return false;
    
    Vec3D v=localCoordinates*r.normal;
    double s=1.0+v.x();
    if (s<1e-5) {
        return false;
    }
    QGraphicsEllipseItem* e=dynamic_cast<QGraphicsEllipseItem*>(item);
    s=1.0/s;
    e->setRect(QRectF(-0.5*spotSize, -0.5*spotSize,spotSize,spotSize));
    e->setPos(v.y()*s, v.z()*s);
    return true;
}
        
QGraphicsItem* StereoProjector::itemFactory() {
    QGraphicsEllipseItem* e=new QGraphicsEllipseItem();
    e->setPen(QPen(Qt::green));
    return e;
}

void StereoProjector::decorateScene() {
    cout << "StereoDecorate" << endl;
    while (!decorationItems.empty()) {
        QGraphicsItem* item = decorationItems.takeLast();
        scene.removeItem(item);
        delete item;
    }
    decorationItems.append(scene.addEllipse(-1.0, -1.0, 2.0, 2.0, QPen(Qt::gray)));
    decorationItems.append(scene.addLine(-1.0, 0.0, 1.0, 0.0, QPen(Qt::gray)));
    decorationItems.append(scene.addLine(0.0, -1.0, 0.0, 1.0, QPen(Qt::gray)));
}

QString StereoProjector::configName() {
    return QString("StereoCfg");
}

void StereoProjector::setDetOrientation(const Mat3D& M) {
    localCoordinates=M;
    emit projectionParamsChanged();
}
