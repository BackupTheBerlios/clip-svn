#include <LauePlaneProjector.h>
#include <cmath>
#include <QtGui/QGraphicsEllipseItem>
#include <iostream>

using namespace std;

LauePlaneProjector::LauePlaneProjector(QObject* parent): Projector(parent), localCoordinates() {
    detWidth=3.0;
    detHeight=4.0;
    scene.setSceneRect(QRectF(-0.5*detWidth, -0.5*detHeight, detWidth, detHeight));
};


QPointF LauePlaneProjector::scattered2det(const Vec3D &v) {
    Vec3D w=localCoordinates*v;
    if (w.x()<=0.0) {
        return QPointF();
    }
    return QPointF(w.y()/w.x(), w.z()/w.x());
}

Vec3D LauePlaneProjector::det2scattered(const QPointF& p) {
    Vec3D v(1.0 , p.x(), p.y());
    v.normalize();
    return localCoordinates.transpose()*v;
}

QPointF LauePlaneProjector::normal2det(const Vec3D& n) {
    return scattered2det(normal2scattered(n));
}


Vec3D LauePlaneProjector::det2normal(const QPointF& p) {
    return scattered2normal(det2scattered(p));
}


bool LauePlaneProjector::project(const Reflection &r, QGraphicsItem* item) {
    Vec3D v=localCoordinates*r.scatteredRay;
    double s=v.x();
    if (s<1e-5) {
        return false;
    }
    QGraphicsEllipseItem* e=dynamic_cast<QGraphicsEllipseItem*>(item);
    s=1.0/s;
    double w=0.015;
    e->setRect(QRectF(v.y()*s-0.5*w, v.z()*s-0.5*w,w,w));
    return true;
}
        
QGraphicsItem* LauePlaneProjector::itemFactory() {
    QGraphicsEllipseItem* e=new QGraphicsEllipseItem();
    e->setPen(QPen(Qt::green));
    return e;
}

void LauePlaneProjector::decorateScene() {
    while (!decorationItems.empty()) {
        QGraphicsItem* item = decorationItems.takeLast();
        scene.removeItem(item);
        delete item;
    }
}


