#ifndef __STEREOPROJECTOR_H__
#define __STEREOPROJECTOR_H__

#include <projector.h>

class StereoProjector: public Projector {
    Q_OBJECT
    public:
        StereoProjector(QObject* parent=0);
        virtual QPointF scattered2det(const Vec3D&, bool* b=NULL) const;
        virtual Vec3D det2scattered(const QPointF&, bool* b=NULL) const;
        virtual QPointF normal2det(const Vec3D&, bool* b=NULL) const;
        virtual Vec3D det2normal(const QPointF&, bool* b=NULL) const;
        
        virtual QString configName();
        virtual QString projectorName();
        virtual QString displayName();
        //virtual double TTmax() const;
        virtual void projector2xml(QXmlStreamWriter&);
//        virtual void loadFromXML(QXmlStreamReader&);
    public slots:
        virtual void decorateScene();
        void setDetOrientation(const Mat3D& M);
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
        virtual bool parseXMLElement(QXmlStreamReader&);
    
        Mat3D localCoordinates;
};

#endif
