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
    public slots:
        virtual void decorateScene();

    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
    
        Mat3D localCoordinates;
        double detWidth;
        double detHeight;
};

#endif
