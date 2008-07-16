#include <projector.h>
#import <cmath>
#import <iostream>
#import <QtCore/QTimer>
#import <QtGui/QCursor>

using namespace std;

Projector::Projector(unsigned int numParams, QObject *parent): QObject(parent), crystal(), scene(this), projectedItems(), decorationItems(), textMarkerItems(), markerItems(), imgGroup() {
    enableSpots();
    enableProjection();
    scene.setItemIndexMethod(QGraphicsScene::NoIndex);
    setWavevectors(0.0, 1.0*M_1_PI);
    setMaxHklSqSum(0);
    setTextSize(4.0);
    setSpotSize(4.0);
    QTimer::singleShot(0, this, SLOT(decorateScene()));
    connect(this, SIGNAL(projectionParamsChanged()), this, SLOT(reflectionsUpdated()));
    connect(&scene, SIGNAL(sceneRectChanged(const QRectF&)), this, SLOT(updateImgTransformations()));
    scene.addItem(&imgGroup);
    imgGroup.setHandlesChildEvents(false);
    //imgGroup.setFlag(QGraphicsItem::ItemIgnoresTransformations, true);
    updateImgTransformations();
    for (; numParams--; ) fitParameterEnabledState.append(false);
};

Projector::Projector(const Projector &p): det2img(p.det2img), img2det(p.img2det), crystal(), scene(this), projectedItems(), decorationItems(), markerItems(), textMarkerItems(), infoItems(), fitParameterEnabledState(p.fitParameterEnabledState)  {
    cout << "Projector Copy Constructor" << endl;
    enableSpots(p.spotsEnabled());
    enableProjection(p.projectionEnabled);
    setWavevectors(p.Qmin(), p.Qmax());
    setMaxHklSqSum(p.getMaxHklSqSum());
    setTextSize(p.getTextSize());
    setSpotSize(p.getSpotSize());
    
    for (unsigned int n=p.markerNumber(); n--; )
        addMarker(p.getMarkerDetPos(n));
    
    connect(this, SIGNAL(projectionParamsChanged()), this, SLOT(reflectionsUpdated()));
    connect(&scene, SIGNAL(sceneRectChanged(const QRectF&)), this, SLOT(updateImgTransformations()));
    
    updateImgTransformations();
} 



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

void Projector::addInfoItem(const QString& text, const QPointF& p) {
    QGraphicsRectItem* bg=new QGraphicsRectItem();
    bg->setPen(QPen(Qt::black));
    bg->setBrush(QBrush(QColor(0xF0,0xF0,0xF0)));
    bg->setPos(p);
    bg->setFlag(QGraphicsItem::ItemIsMovable, true);
    bg->setCursor(QCursor(Qt::SizeAllCursor));
    bg->setZValue(1);
    QGraphicsTextItem*  t = new QGraphicsTextItem(bg);
    t->setHtml(text);
    QRectF r=t->boundingRect();
    double sx=textSize*scene.width()/r.width();
    double sy=textSize*scene.height()/r.height();
    double s=sx<sy?sy:sx;
    
    bg->setRect(t->boundingRect());
    bg->scale(s,s);
    scene.addItem(bg);
    infoItems.append(bg);
}

void Projector::clearInfoItems() {
    while (infoItems.size()>0) {
        QGraphicsItem* item=infoItems.takeLast();
        delete item;
    }
}

void Projector::reflectionsUpdated() {
    if (crystal.isNull() or not projectionEnabled) 
        return;
    cout << "Project..." << endl;
    //FIXME: Do Better
    while (textMarkerItems.size()>0) {
        QGraphicsItem* item=textMarkerItems.takeLast();
        scene.removeItem(item);
        delete item;
    }

    clearInfoItems();
    
    QList<Reflection> r = crystal->getReflectionList();
    int n=0;
    int i=0;
    #ifdef __DEBUG__
    int beginSize=projectedItems.size();
    #endif

    if (!showSpots) {
        i=r.size();
    }
    for (; i<r.size() and n<projectedItems.size(); i++) {
        if (project(r.at(i), projectedItems.at(n))) {
            if (r.at(i).hklSqSum<=maxHklSqSum) {
                QGraphicsTextItem*  t = scene.addText("");
                t->setHtml(formatHklText(r.at(i).h, r.at(i).k, r.at(i).l));
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
        if (project(r.at(i), item))  {
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


Vec3D Projector::normal2scattered(const Vec3D &v, bool* b) {
    double x=v.x();
    if (x<=0.0) {
        if (b) *b=false;
        return Vec3D();
    }
    double y=v.y();
    double z=v.z();
    if (b) *b=true;
    return Vec3D(2*x*x-1.0, 2.0*x*y, 2.0*x*z);
}

Vec3D Projector::scattered2normal(const Vec3D& v, bool* b) {
    double x=v.x();
    double y=v.y();
    double z=v.z();

    x=sqrt(0.5*(x+1.0));
    if (x==0.0) {
        if (b) *b=false;
        return Vec3D();
    }
    if (b) *b=true;
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

Crystal* Projector::getCrystal() {
    return crystal;
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
    //QRectF r(-5.0,-5.0,10.0,10.0);
    
    QGraphicsEllipseItem* marker=new QGraphicsEllipseItem(&imgGroup);
    marker->setFlag(QGraphicsItem::ItemIsMovable, true);
    //marker->setFlag(QGraphicsItem::ItemIgnoresTransformations, true);
    marker->setCursor(QCursor(Qt::SizeAllCursor));
    marker->setPen(QPen(Qt::black));
    marker->setRect(r);
    marker->setPos(det2img.map(p));
    QTransform t;
    t.scale(det2img.m11(), det2img.m22());
    marker->setTransform(t);

    QPointF mp=marker->scenePos();
    cout << "Marker " << p.x() << "  "<< p.y() << " " << mp.x() << "  "<< mp.y() << " ";
    mp=marker->pos();
    cout << mp.x() << "  "<< mp.y() << endl;
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

unsigned int Projector::markerNumber() const {
    return markerItems.size();
}

QPointF Projector::getMarkerDetPos(unsigned int n) const {
    return img2det.map(markerItems.at(n)->pos());
}

QList<Vec3D> Projector::getMarkerNormals() const {
    QList<Vec3D> r;
    for (unsigned int i=0; i<markerItems.size(); i++) 
        r << det2normal(img2det.map(markerItems.at(i)->pos()));
    return r;
}

void Projector::updateImgTransformations() {
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
    QTransform t;
    t.scale(det2img.m11(), det2img.m22());
    for (unsigned int i=imgGroup.childItems().size(); i--; ) 
        imgGroup.childItems().at(i)->setTransform(t);
    emit imgTransformUpdated();
}

// Rotates and flips the Decorations, which are bound to the Image
void Projector::doImgRotation(unsigned int CWRSteps, bool flip) {
    QTransform t;
    for (unsigned int i=imgGroup.childItems().size(); i--; ) {
        QGraphicsItem* e=imgGroup.childItems().at(i);
        double x = e->pos().x();
        double y = e->pos().y();
        
        if (flip) x=1.0-x;
        double t;
        switch(CWRSteps) {
            case 1:
                t=x;
                x=y;
                y=1.0-t;
                break;
            case 2:
                x=1.0-x;
                y=1.0-y;
                break;
            case 3:
                t=x;
                x=1.0-y;
                y=t;
                break;
        }
        e->setPos(x,y);
    }
}


unsigned int Projector::fitParameterNumber() {
    return 0;
}

QString Projector::fitParameterName(unsigned int n) {
    return "";
}

double Projector::fitParameterValue(unsigned int n) {
    return 0.0;
}

void Projector::fitParameterSetValue(unsigned int n, double val) {}

QPair<double, double> Projector::fitParameterBounds(unsigned int n) {
    return qMakePair((double)-INFINITY, (double)INFINITY);
}

double Projector::fitParameterChangeHint(unsigned int n) {
    return 1.0;
}

bool Projector::fitParameterEnabled(unsigned int n) {
    return fitParameterEnabledState[n];
}

void Projector::fitParameterSetEnabled(unsigned int n, bool enable) {
    fitParameterEnabledState[n]=enable;
}

void Projector::enableProjection(bool b) {
    projectionEnabled=b;
}
