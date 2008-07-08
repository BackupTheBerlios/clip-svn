#ifndef __LAUEPLANEPROJECTOR_H__
#define __LAUEPLANEPROJECTOR_H__

#include <projector.h>

class LauePlaneProjector: public Projector {
    Q_OBJECT
    public:
        LauePlaneProjector(QObject* parent=0);
        virtual QPointF scattered2det(const Vec3D&);
        virtual Vec3D det2scattered(const QPointF&);
        virtual QPointF normal2det(const Vec3D&);
        virtual Vec3D det2normal(const QPointF&);
    
        virtual QString configName();
        double dist();
        double width();
        double height();
        double omega();
        double chi();
        double phi();
        virtual void doImgRotation(unsigned int CWRSteps, bool flip);
        
    public slots:
        void setDetSize(double dist, double width, double height);
        void setDetOrientation(double omega, double chi, double phi);
        virtual void decorateScene();
        void resizePBMarker();
        void movedPBMarker();
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
    
        Mat3D localCoordinates;
        double detDist;
        double detWidth;
        double detHeight;
        double detOmega;
        double detChi;
        double detPhi;
        double detDx;
        double detDy;
};

#endif
