#ifndef __STEREOPROJECTOR_H__
#define __STEREOPROJECTOR_H__

#include <projector.h>

class StereoProjector: public Projector {
    Q_OBJECT
    public:
        StereoProjector(ObjectStore*, QObject* parent=0);
        void setStereoProjectionDir(const Vec3D &v);
        virtual QPointF scattered2det(const Vec3D&);
        virtual Vec3D det2scattered(const QPointF&);
        virtual QPointF normal2det(const Vec3D&);
        virtual Vec3D det2normal(const QPointF&);
    protected:
        virtual bool project(const Reflection &r);
        Vec3D dir;
        Mat3D R;
};

#endif
