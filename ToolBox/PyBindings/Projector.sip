
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
        
        static Vec3D normal2scattered(const Vec3D&, bool* b /out/);
        static Vec3D scattered2normal(const Vec3D&, bool* b /out/);
        
        QTransform det2img;
        QTransform img2det;
        
        virtual QPointF scattered2det(const Vec3D&, bool* b /out/)=0;
        virtual Vec3D det2scattered(const QPointF&, bool* b /out/)=0;
        virtual QPointF normal2det(const Vec3D&, bool* b /out/)=0;
        virtual Vec3D det2normal(const QPointF&, bool* b /out/)=0;
        
        QGraphicsScene* getScene();
        Crystal* getCrystal();
        virtual QString configName()=0;
        double Qmin() const;
        double Qmax() const;
        unsigned int getMaxHklSqSum() const;
        double getTextSize() const;
        double getSpotSize() const;
        bool spotsEnabled() const;

        QList<Vec3D> getMarkerNormals();
        unsigned int markerNumber();
        QPointF getMarkerDetPos(unsigned int n);

        virtual unsigned int fitParameterNumber();
        virtual QString fitParameterName(unsigned int n);
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual QPair<double, double> fitParameterBounds(unsigned int n);
        virtual double fitParameterChangeHint(unsigned int n);
        
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

        virtual void doImgRotation(unsigned int CWRSteps, bool flip);
        void addInfoItem(const QString& text, const QPointF& p);
        void clearInfoItems();
        
    signals:  
        void projectedPointsUpdated();
        void wavevectorsUpdated();
        void projectionParamsChanged();
        void projectionRectSizeChanged();
        void projectionRectPosChanged();
        void imgTransformUpdated();
        
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
        
        QPointF scattered2det(const Vec3D&, bool* b /out/);
        Vec3D det2scattered(const QPointF&, bool* b /out/);
        QPointF normal2det(const Vec3D&, bool* b /out/);
        Vec3D det2normal(const QPointF&, bool* b /out/);
        virtual void decorateScene();
        virtual QString configName();
        void setDetOrientation(const Mat3D& M);
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
        
        QPointF scattered2det(const Vec3D&, bool* b /out/);
        Vec3D det2scattered(const QPointF&, bool* b /out/);
        QPointF normal2det(const Vec3D&, bool* b /out/);
        Vec3D det2normal(const QPointF&, bool* b /out/);
        double dist();
        double width();
        double height();
        double omega();
        double chi();
        double phi();
        double xOffset();
        double yOffset();
        
        virtual QString configName();
        
        void setDetSize(double dist, double width, double height);
        void setDetOrientation(double omega, double chi, double phi);
        void setDetOffset(double dx, double dy);
        virtual void decorateScene();
        void resizePBMarker();
        void movedPBMarker();
        virtual void doImgRotation(unsigned int CWRSteps, bool flip);

        virtual unsigned int fitParameterNumber();
        virtual QString fitParameterName(unsigned int n);
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual QPair<double, double> fitParameterBounds(unsigned int n);
        virtual double fitParameterChangeHint(unsigned int n);
        
    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item);
        virtual QGraphicsItem* itemFactory();
};



// QPair<double, double> is implemented as a Python 2-element tuple.
%MappedType QPair<double, double>
{
%TypeHeaderCode
#include <qpair.h>
%End

%ConvertFromTypeCode
    // Create the tuple.
    return Py_BuildValue((char *)"dd", sipCpp->first, sipCpp->second);
%End

%ConvertToTypeCode
    // Check the type if that is all that is required.
    if (sipIsErr == NULL)
        return (PyTuple_Size(sipPy) == 2);

    QPair<double,double> *qp = new QPair<double,double>;

    qp->first = PyFloat_AsDouble(PyTuple_GET_ITEM(sipPy, 0));
    qp->second = PyFloat_AsDouble(PyTuple_GET_ITEM(sipPy, 1));

    *sipCppPtr = qp;

    return sipGetState(sipTransferObj);
%End
};


