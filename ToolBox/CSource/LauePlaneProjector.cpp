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
    QGraphicsEllipseItem* center=scene.addEllipse(-0.015, -0.015, 0.03, 0.03, QPen(Qt::red));
    center->setFlag(QGraphicsItem::ItemIsMovable, true);
    QGraphicsEllipseItem* handle=scene.addEllipse(-0.015, -0.015, 0.03, 0.03, QPen(Qt::red));
    handle->moveBy(0.1, 0);
    handle->setFlag(QGraphicsItem::ItemIsMovable, true);
    handle->setParentItem(center);

    QGraphicsEllipseItem* marker=scene.addEllipse(0.1, 0.1, 0.13, 0.13, QPen(Qt::red));
    marker->setParentItem(center);
    
    decorationItems.append(center);
    decorationItems.append(handle);
    decorationItems.append(marker);
    
    connect(&scene, SIGNAL(changed(const QList<QRectF> &)), this, SLOT(updatePBMarker()));
    updatePBMarker();
}


void LauePlaneProjector::updatePBMarker() {
    QGraphicsEllipseItem* center=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[0]);
    QGraphicsEllipseItem* handle=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[1]);
    QGraphicsEllipseItem* marker=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[2]);
    
    QPointF p=handle->pos();
    double l=hypot(p.x(), p.y());
    #ifdef __DEBUG__
    cout << "bpmarker (" << center->pos().x() << "," << center->pos().y() << ") l=" << l << endl;
    #endif

    QRectF r(-l, -l, 2*l, 2*l);
    r.moveCenter(center->rect().center());
    marker->setRect(r);
}
    
QString LauePlaneProjector::configName() {
    return QString("LauePlaneCfg");
}

    
