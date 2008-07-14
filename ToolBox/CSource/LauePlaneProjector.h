#ifndef __LAUEPLANEPROJECTOR_H__
#define __LAUEPLANEPROJECTOR_H__

#include <projector.h>

class LauePlaneProjector: public Projector {
    Q_OBJECT
    public:
        LauePlaneProjector(QObject* parent=0);
        virtual QPointF scattered2det(const Vec3D&, bool* b=NULL);
        virtual Vec3D det2scattered(const QPointF&, bool* b=NULL);
        virtual QPointF normal2det(const Vec3D&, bool* b=NULL);
        virtual Vec3D det2normal(const QPointF&, bool* b=NULL);
    
        virtual QString configName();
        double dist();
        double width();
        double height();
        double omega();
        double chi();
        double phi();
        double xOffset();
        double yOffset();
        virtual void doImgRotation(unsigned int CWRSteps, bool flip);
        
        // Functions for fitting parameters
        virtual unsigned int fitParameterNumber();
        virtual QString fitParameterName(unsigned int n);
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual QPair<double, double> fitParameterBounds(unsigned int n);
        virtual double fitParameterChangeHint(unsigned int n);        
            
    public slots:
        void setDetSize(double dist, double width, double height);
        void setDetOrientation(double omega, double chi, double phi);
        void setDetOffset(double dx, double dy);
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
