#include <projector.h>
#import <cmath>
#import <iostream>
#import <QtCore/QTimer>
#import <QtGui/QCursor>

using namespace std;

Projector::Projector(QObject *parent): QObject(parent), crystal(), scene(this), projectedItems(), decorationItems(), textMarkerItems(), markerItems(), imgGroup() {
    enableSpots();
    setWavevectors(0.0, 2.0*M_1_PI);
    setMaxHklSqSum(0);
    setTextSize(4.0);
    setSpotSize(4.0);
    QTimer::singleShot(0, this, SLOT(decorateScene()));
    connect(this, SIGNAL(projectionParamsChanged()), this, SLOT(reflectionsUpdated()));
    connect(&scene, SIGNAL(sceneRectChanged(const QRectF&)), this, SLOT(updateImgTransformations()));
    scene.addItem(&imgGroup);
    imgGroup.setHandlesChildEvents(false);
    updateImgTransformations();
};

Projector::Projector(const Projector &p): crystal(p.crystal), scene(this),projectedItems(), decorationItems(), markerItems()  {
    enableSpots(p.spotsEnabled());
    setWavevectors(p.Qmin(), p.Qmax());
    setMaxHklSqSum(p.getMaxHklSqSum());
    setTextSize(p.getTextSize());
    setSpotSize(p.getSpotSize());
    connect(this, SIGNAL(projectionParamsChanged()), this, SLOT(reflectionsUpdated()));
    updateImgTransformations();
}; 


void Projector::connectToCrystal(Crystal *c) {
    if (not crystal.isNull()) {
        disconnect(this, 0, crystal, 0);
        disconnect(crystal, 0, this, 0);
    }
    crystal=c;
    crystal->addProjector(this);
    connect(crystal, SIGNAL(reflectionsUpdate()), this, SLOT(reflectionsUpdated()));
    emit projectionParamsChanged();
}
    

double Projector::Qmin() const {
    return QminVal;
}

double Projector::Qmax() const {
    return QmaxVal;
}


void Projector::setWavevectors(double Qmin, double Qmax)  {
    if ((Qmin<Qmax) and ((Qmin!=QminVal) or (Qmax!=QmaxVal))) {
        QmaxVal=Qmax;
        QminVal=Qmin;
        emit projectionParamsChanged();
        emit wavevectorsUpdated();
    }
}

QString formatOveline(int i) {
    if (i<0)
        return QString("<span style=""text-decoration:overline"">%1</span>").arg(-i);
    return QString("<span>%1</span>").arg(i);
}

QString formatHklText(int h, int k, int l) {
    if (h<10 and k<10 and l<10) {
        return formatOveline(h)+formatOveline(k)+formatOveline(l);
    } else {
        return formatOveline(h)+" "+formatOveline(k)+" "+formatOveline(l);
    }
}

void Projector::reflectionsUpdated() {
    if (crystal.isNull()) 
        return;
    
    //FIXME: Do Better
    while (textMarkerItems.size()>0) {
        QGraphicsItem* item=textMarkerItems.takeLast();
        scene.removeItem(item);
        delete item;
    }
    
    std::vector<Reflection>& r = crystal->getReflectionList();
    int n=0;
    int i=0;
    #ifdef __DEBUG__
    int beginSize=projectedItems.size();
    #endif

    if (!showSpots) {
        i=r.size();
    }
    for (; i<r.size() and n<projectedItems.size(); i++) {
        if (project(r[i], projectedItems.at(n))) {
            if (r[i].hklSqSum<=maxHklSqSum) {
                QGraphicsTextItem*  t = scene.addText("");
                t->setHtml(formatHklText(r[i].h, r[i].k, r[i].l));
                t->setPos(projectedItems.at(n)->pos());
                QRectF r=t->boundingRect();
                double sx=textSize*scene.width()/r.width();
                double sy=textSize*scene.height()/r.height();
                double s=sx<sy?sy:sx;
                t->scale(s,s);
                textMarkerItems.append(t);
            }
            n++;
        }
    }
    
    #ifdef __DEBUG__
    int rewritten=n;
    int deleted=0;
    int added=0;
    int projected=n;
    #endif
    QGraphicsItem* item;
    while (projectedItems.size()>n) {
        item = projectedItems.takeLast();
        scene.removeItem(item);
        delete item;
        #ifdef __DEBUG__
        deleted++;
        #endif
    }


    item = itemFactory();
    for (; i<r.size(); i++) {
        if (project(r[i], item))  {
            projectedItems.append(item);
            scene.addItem(item);
            item = itemFactory();
            #ifdef __DEBUG__
            projected++;
            added++;
            #endif
        }
    }
    delete item;
    
    #ifdef __DEBUG__
    cout << "startSize:" << beginSize;
    cout << " rewrite:" << rewritten;
    cout << " del:" << deleted;
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

unsigned int Projector::getMaxHklSqSum() const {
    return maxHklSqSum;
}

double Projector::getSpotSize() const {
    return 100.0*spotSize;
}
    
double Projector::getTextSize() const {
    return 100.0*textSize;
}

bool Projector::spotsEnabled() const {
    return showSpots;
}

void Projector::setMaxHklSqSum(unsigned int m) {
    maxHklSqSum=m;
    emit projectionParamsChanged();
}

void Projector::setTextSize(double d) {
    textSize=0.01*d;
    emit projectionParamsChanged();
}

void Projector::setSpotSize(double d) {
    spotSize=0.01*d;
    emit projectionParamsChanged();
}

void Projector::enableSpots(bool b) {
    showSpots=b;
    emit projectionParamsChanged();
}

void Projector::addMarker(const QPointF& p) {
    QRectF r(-0.5*spotSize, -0.5*spotSize, spotSize, spotSize);
    
    QGraphicsEllipseItem* marker=new QGraphicsEllipseItem(&imgGroup);
    marker->setFlag(QGraphicsItem::ItemIsMovable, true);
    //marker->setFlag(QGraphicsItem::ItemIgnoresTransformations, true);
    marker->setCursor(QCursor(Qt::SizeAllCursor));
    marker->setPen(QPen(Qt::black));
    marker->setPos(det2img.map(p));
    marker->setRect(r);
    
    markerItems.append(marker);
};

void Projector::delMarkerNear(const QPointF& p) {
    if (markerItems.isEmpty())
        return;
    double minDist;
    unsigned int minIdx;
    QGraphicsEllipseItem* m;
    QPointF imgPos=det2img.map(p);
    for (unsigned int i=0; i<markerItems.size(); i++) {
        m=markerItems.at(i);
        double d=hypot(imgPos.x()-m->pos().x(), imgPos.y()-m->pos().y());
        if (i==0 or d<minDist) {
            minDist=d;
            minIdx=i;
        }
    }
    m=markerItems.takeAt(minIdx);
    scene.removeItem(m);
    delete m;
};

QList<Vec3D> Projector::getMarkerNormals() {
    QList<Vec3D> r;
    for (unsigned int i=0; i<markerItems.size(); i++) 
        r << det2normal(img2det.map(markerItems.at(i)->pos()));
    return r;
}

void Projector::updateImgTransformations() {
    cout << "updateImgTransform" << endl;
    const QRectF r=scene.sceneRect();
    det2img.reset();
    if (r.isEmpty()) {
        img2det.reset();
    } else {
        det2img.scale(1.0/r.width(),  1.0/r.height());
        det2img.translate(-r.x(),  -r.y());
        img2det=det2img.inverted();
    }
    imgGroup.setTransform(img2det);
    emit imgTransformUpdated();
}
