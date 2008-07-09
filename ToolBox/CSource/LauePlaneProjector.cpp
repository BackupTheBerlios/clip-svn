#include <LauePlaneProjector.h>
#include <cmath>
#include <QtGui/QGraphicsEllipseItem>
#include <QtGui/QCursor>
#include <SignalingEllipse.h>
#include <iostream>

using namespace std;

LauePlaneProjector::LauePlaneProjector(QObject* parent): Projector(parent), localCoordinates() {
    setDetSize(30.0, 110.0, 140.0);
    setDetOrientation(180.0, 0, 0);
    detDx=0.0;
    detDy=0.0;
};


QPointF LauePlaneProjector::scattered2det(const Vec3D &v) {
    Vec3D w=localCoordinates*v;
    if (w.x()<=0.0) {
        return QPointF();
    }
    return QPointF(w.y()/w.x()+detDx, w.z()/w.x()+detDy);
}

Vec3D LauePlaneProjector::det2scattered(const QPointF& p) {
    Vec3D v(1.0 , p.x()-detDx, p.y()-detDy);
    v.normalize();
    return localCoordinates.transposed()*v;
}

QPointF LauePlaneProjector::normal2det(const Vec3D& n) {
    return scattered2det(normal2scattered(n));
}


Vec3D LauePlaneProjector::det2normal(const QPointF& p) {
    return scattered2normal(det2scattered(p));
}


bool LauePlaneProjector::project(const Reflection &r, QGraphicsItem* item) {
    if (r.lowestDiffOrder==0) 
        return false;

    bool doesReflect=false;
    for (unsigned int i=0; i<r.orders.size(); i++) {
        unsigned int n=r.orders[i];
        if ((QminVal<=n*r.Qscatter) and (n*r.Qscatter<=QmaxVal)) {
            doesReflect=true;
            break;
        }
    }
    if (not doesReflect)
        return false;
        
    Vec3D v=localCoordinates*r.scatteredRay;
    double s=v.x();
    if (s<1e-10)
        return false;
    
    
    QGraphicsEllipseItem* e=dynamic_cast<QGraphicsEllipseItem*>(item);
    s=1.0/s;
    e->setRect(QRectF(-0.5*spotSize, -0.5*spotSize,spotSize,spotSize));
    e->setPos(v.y()*s+detDx, v.z()*s+detDy);
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
    
    QTransform t;
    t.scale(det2img.m11(), det2img.m22());    
    
    SignalingEllipseItem* center=new SignalingEllipseItem(-0.5*spotSize, -0.5*spotSize, spotSize, spotSize, &imgGroup);
    center->setPen(QPen(Qt::red));
    center->setFlag(QGraphicsItem::ItemIsMovable, true);
    center->setCursor(QCursor(Qt::SizeAllCursor));
    center->setTransform(t);
    
    SignalingEllipseItem* handle=new SignalingEllipseItem(-0.5*spotSize, -0.5*spotSize, spotSize, spotSize,center);
    handle->setPen(QPen(Qt::red));
    handle->moveBy(0.1, 0);
    handle->setFlag(QGraphicsItem::ItemIsMovable, true);
    handle->setCursor(QCursor(Qt::SizeAllCursor));
    QGraphicsEllipseItem* marker=new QGraphicsEllipseItem(0.1, 0.1, 0.13, 0.13, center);
    marker->setPen(QPen(Qt::red));
    
    decorationItems.append(center);
    decorationItems.append(handle);
    decorationItems.append(marker);
    
    center->setPos(0.5, 0.5);
    
    connect(center, SIGNAL(positionChanged()), this, SLOT(movedPBMarker()));
    connect(handle, SIGNAL(positionChanged()), this, SLOT(resizePBMarker()));
    resizePBMarker();
}


void LauePlaneProjector::resizePBMarker() {
    QGraphicsEllipseItem* center=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[0]);
    QGraphicsEllipseItem* handle=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[1]);
    QGraphicsEllipseItem* marker=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[2]);
    
    QPointF p=handle->pos();
    double l=hypot(p.x(), p.y());

    QRectF r(-l, -l, 2*l, 2*l);
    r.moveCenter(center->rect().center());
    marker->setRect(r);
}

void LauePlaneProjector::movedPBMarker() {
    QGraphicsEllipseItem* center=dynamic_cast<QGraphicsEllipseItem*>(decorationItems[0]);
    QPointF p=center->scenePos();
    //FIXME: This is only OK for 180DEG
    detDx=p.x();
    detDy=p.y();
    emit projectionParamsChanged();
}

QString LauePlaneProjector::configName() {
    return QString("LauePlaneCfg");
}

void LauePlaneProjector::setDetSize(double dist, double width, double height) {
    if ((detDist!=dist) or (detWidth!=width) or (detHeight!=height)) {
        detDist=dist;
        detWidth=width;
        detHeight=height;
        
        scene.setSceneRect(QRectF(-0.5*detWidth/detDist, -0.5*detHeight/detDist, detWidth/detDist, detHeight/detDist));
        emit projectionRectSizeChanged();
        emit projectionParamsChanged();
    }
}
    
void LauePlaneProjector::setDetOrientation(double omega, double chi, double phi) {
    if ((detOmega!=omega) or (detChi!=chi) or (detPhi!=phi)) {
        detOmega=omega;
        detChi=chi;
        detPhi=phi;
    
        localCoordinates=Mat3D(Vec3D(0,0,1), M_PI*(omega-180.0)/180.0)*Mat3D(Vec3D(0,1,0), M_PI*chi/180.0)*Mat3D(Vec3D(1,0,0), M_PI*phi/180.0);
        emit projectionParamsChanged();
    }
}
    
double LauePlaneProjector::dist() {
    return detDist;
}

double LauePlaneProjector::width() {
    return detWidth;
}

double LauePlaneProjector::height() {
    return detHeight;
}
double LauePlaneProjector::omega() {
    return detOmega;
}

double LauePlaneProjector::chi() {
    return detChi;
}

double LauePlaneProjector::phi() {
    return detPhi;
}

void LauePlaneProjector::doImgRotation(unsigned int CWRSteps, bool flip) {
    cout << "LauePlaneImageRotation " << CWRSteps << endl;
    Projector::doImgRotation(CWRSteps, flip);
    if (CWRSteps%2==1) {
        setDetSize(dist(), height(), width());
    }
}
