#ifndef __PROJECTOR_H__
#define __PROJECTOR_H__

#include <vector>
#include <reflection.h>
#include <QtCore/QObject>
#include <QtCore/QVector>
#include <QtCore/QPointF>
#include <QtCore/QPointer>
#include <crystal.h>


class Projector: public QObject {
    Q_OBJECT
    public:
        Projector(ObjectStore*, QObject* parent=0);
        Projector(const Projector&);
        QList<QPointF> projectedPoints;  
        double lowerWavelength();
        double upperWavelength();
        static Vec3D normal2scattered(const Vec3D&);
        static Vec3D scattered2normal(const Vec3D&);

        virtual QPointF scattered2det(const Vec3D&)=0;
        virtual Vec3D det2scattered(const QPointF&)=0;
        virtual QPointF normal2det(const Vec3D&)=0;
        virtual Vec3D det2normal(const QPointF&)=0;
        
    public slots:
        void connectToCrystal(Crystal *);
        void setWavelength(double lower, double upper);
        void reflectionsUpdated();
        void addRotation(const Vec3D &axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        
    signals:  
        void projectedPointsUpdated();
        void wavelengthUpdated();
    protected:
        virtual bool project(const Reflection &r)=0;
        QPointer<Crystal> crystal;
        ObjectStore& crystalStore;
        double upperLambda;
        double lowerLambda;
};



#endif
