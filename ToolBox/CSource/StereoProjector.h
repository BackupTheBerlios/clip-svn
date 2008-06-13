#ifndef __STEREOPROJECTOR_H__
#define __STEREOPROJECTOR_H__

#include <projector.h>

class StereoProjector: public Projector {
    Q_OBJECT
    public:
        StereoProjector(QObject* parent=0);
        virtual QPointF scattered2det(const Vec3D&);
        virtual Vec3D det2scattered(const QPointF&);
        virtual QPointF normal2det(const Vec3D&);
        virtual Vec3D det2normal(const QPointF&);
    
        virtual QString configName();
    public slots:
        virtual void decorateScene();

    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
    
        Mat3D localCoordinates;
};

#endif
