#ifndef __PROJECTOR_H__
#define __PROJECTOR_H__

#include <vector>
#include <reflection.h>
#include <QtCore/QObject>
#include <QtCore/QVector>
#include <QtCore/QPointF>
#include <QtCore/QPointer>
#include <QtGui/QGraphicsScene>
 #include <QtGui/QGraphicsItem>
 #include <QtCore/QString>
#include <crystal.h>


class Projector: public QObject {
    Q_OBJECT
    public:
        Projector(QObject* parent=0);
        Projector(const Projector&);

        double Qmin();
        double Qmax();

        static Vec3D normal2scattered(const Vec3D&);
        static Vec3D scattered2normal(const Vec3D&);

        virtual QPointF scattered2det(const Vec3D&)=0;
        virtual Vec3D det2scattered(const QPointF&)=0;
        virtual QPointF normal2det(const Vec3D&)=0;
        virtual Vec3D det2normal(const QPointF&)=0;
        
        QGraphicsScene* getScene();
        
        virtual QString configName()=0;
        
    public slots:
        void connectToCrystal(Crystal *);
        void setWavevectors(double Qmin, double Qmax);
        void reflectionsUpdated();
        void addRotation(const Vec3D &axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        virtual void decorateScene()=0;

    signals:  
        void projectedPointsUpdated();
        void wavevectorsUpdated();
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item)=0;
        virtual QGraphicsItem* itemFactory()=0;
    
        QList<QGraphicsItem*> projectedItems;
        QList<QGraphicsItem*> decorationItems;
    
        QPointer<Crystal> crystal;

        double QminVal;
        double QmaxVal;
        QGraphicsScene scene;
};



#endif
