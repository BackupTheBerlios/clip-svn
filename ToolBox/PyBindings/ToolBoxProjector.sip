
class Projector: QObject {
%TypeHeaderCode
#include <vec3D.h>
#include <QtCore/QObject>
#include <QtGui/QGraphicsScene>
#include <projector.h>
%End
    public:
        Projector(QObject* parent=0);
        Projector(const Projector&);
        
        static Vec3D normal2scattered(const Vec3D&);
        static Vec3D scattered2normal(const Vec3D&);
        
        virtual QPointF scattered2det(const Vec3D&)=0;
        virtual Vec3D det2scattered(const QPointF&)=0;
        virtual QPointF normal2det(const Vec3D&)=0;
        virtual Vec3D det2normal(const QPointF&)=0;
        
        QGraphicsScene* getScene();
        virtual QString configName()=0;
        double Qmin() const;
        double Qmax() const;
        unsigned int getMaxHklSqSum() const;
        double getTextSize() const;
        double getSpotSize() const;
        bool spotsEnabled() const;
        
        QList<Vec3D> getMarkerNormals();
    public slots:
        void connectToCrystal(Crystal *);
        void setWavevectors(double Qmin, double Qmax);
        void reflectionsUpdated();
        void addRotation(const Vec3D& axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        virtual void decorateScene()=0;
        void setTextSize(double d);
        void setSpotSize(double d);
        void setMaxHklSqSum(unsigned int m);
        void enableSpots(bool b=true);
        void addMarker(const QPointF &p);
        void delMarkerNear(const QPointF &p);
    signals:  
        void projectedPointsUpdated();
        void wavevectorsUpdated();
        void projectionParamsChanged();
        void projectionRectSizeChanged();
        void projectionRectPosChanged();
        
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item)=0;
        virtual QGraphicsItem* itemFactory()=0;

};



class StereoProjector: Projector {
%TypeHeaderCode
#include <vec3D.h>
#include <QtCore/QObject>
#include <StereoProjector.h>
#include <projector.h>
%End
    public:
        StereoProjector(QObject* parent=0);
        
        QPointF scattered2det(const Vec3D&);
        Vec3D det2scattered(const QPointF&);
        QPointF normal2det(const Vec3D&);
        Vec3D det2normal(const QPointF&);
        virtual void decorateScene();
        virtual QString configName();
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
};


class LauePlaneProjector: Projector {
%TypeHeaderCode
#include <vec3D.h>
#include <QtCore/QObject>
#include <LauePlaneProjector.h>
#include <projector.h>
%End
    public:
        LauePlaneProjector(QObject* parent=0);
        
        QPointF scattered2det(const Vec3D&);
        Vec3D det2scattered(const QPointF&);
        QPointF normal2det(const Vec3D&);
        Vec3D det2normal(const QPointF&);
        double dist();
        double width();
        double height();
        double omega();
        double chi();
        double phi();
        virtual QString configName();
        
        void setDetSize(double dist, double width, double height);
        void setDetOrientation(double omega, double chi, double phi);
        virtual void decorateScene();
        void updatePBMarker();
        void movedPBMarker();
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
};


