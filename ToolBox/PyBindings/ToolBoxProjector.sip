
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
        
        double lowerWavelength();
        double upperWavelength();
        static Vec3D normal2scattered(const Vec3D&);
        static Vec3D scattered2normal(const Vec3D&);

        virtual QPointF scattered2det(const Vec3D&)=0;
        virtual Vec3D det2scattered(const QPointF&)=0;
        virtual QPointF normal2det(const Vec3D&)=0;
        virtual Vec3D det2normal(const QPointF&)=0;
        
        QGraphicsScene* getScene();
    public slots:
        void connectToCrystal(Crystal *);
        void setWavelength(double lower, double upper);
        void reflectionsUpdated();
        void addRotation(const Vec3D& axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        virtual void decorateScene()=0;
    signals:  
        void projectedPointsUpdated();
        void wavelengthUpdated();
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
        virtual void decorateScene();
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
};


