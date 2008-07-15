#ifndef __PROJECTOR_H__
#define __PROJECTOR_H__

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
        Projector(unsigned int numParams, QObject* parent=0);
        Projector(const Projector&);

        // Functions for transformations in the different Coordinate systems
    
        static Vec3D normal2scattered(const Vec3D&, bool* b=NULL);
        static Vec3D scattered2normal(const Vec3D&, bool* b=NULL);
        
        QTransform det2img;
        QTransform img2det;
    
        virtual QPointF scattered2det(const Vec3D&, bool* b=NULL)=0;
        virtual Vec3D det2scattered(const QPointF&, bool* b=NULL)=0;
        virtual QPointF normal2det(const Vec3D&, bool* b=NULL)=0;
        virtual Vec3D det2normal(const QPointF&, bool* b=NULL)=0;
        
        QGraphicsScene* getScene();
        Crystal* getCrystal();
        virtual QString configName()=0;

        double Qmin() const;
        double Qmax() const;
        unsigned int getMaxHklSqSum() const;
        double getTextSize() const;
        double getSpotSize() const;
        bool spotsEnabled() const;
        
        unsigned int markerNumber();
        QPointF getMarkerDetPos(unsigned int n);
        QList<Vec3D> getMarkerNormals();
        
        // Functions for fitting parameters
        virtual unsigned int fitParameterNumber();
        virtual QString fitParameterName(unsigned int n);
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual QPair<double, double> fitParameterBounds(unsigned int n);
        virtual double fitParameterChangeHint(unsigned int n);
        virtual bool fitParameterEnabled(unsigned int n);
        virtual void fitParameterSetEnabled(unsigned int n, bool enable);
        
    public slots:
        void connectToCrystal(Crystal *);
        void setWavevectors(double Qmin, double Qmax);
        void reflectionsUpdated();

        void addRotation(const Vec3D &axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);

        virtual void decorateScene()=0;
        void setMaxHklSqSum(unsigned int m);
        void setTextSize(double d);
        void setSpotSize(double d);
        void enableSpots(bool b=true);

        void addMarker(const QPointF& p);
        void delMarkerNear(const QPointF& p);
        
        virtual void doImgRotation(unsigned int CWRSteps, bool flip);

        void addInfoItem(const QString& text, const QPointF& p);
        void clearInfoItems();
        
    signals:  
        void projectedPointsUpdated();
        void wavevectorsUpdated();
        void projectionParamsChanged();
        void projectionRectPosChanged();
        void projectionRectSizeChanged();
        void imgTransformUpdated();

    protected:
        virtual bool project(const Reflection &r, QGraphicsItem* item)=0;
        virtual QGraphicsItem* itemFactory()=0;
    
        // These are the reflections
        QList<QGraphicsItem*> projectedItems;
        // Stuff like Primary beam marker, Coordinate lines
        QList<QGraphicsItem*> decorationItems;
        // written indexes in the scene
        QList<QGraphicsItem*> textMarkerItems;
        // Markers for indexation and fit
        QList<QGraphicsEllipseItem*> markerItems;
        // Info Items. These will be set on Mousepress from Python and be deleted on orientation change or slot!
        QList<QGraphicsItem*> infoItems;
    
        // Pointer to the connectred crystal
        QPointer<Crystal> crystal;
    
        QList<bool> fitParameterEnabledState;

        double QminVal;
        double QmaxVal;
        unsigned int maxHklSqSum;
        double textSize;
        double spotSize;
        bool showSpots;
        
        QGraphicsScene scene;
        
        QTransform img2detTransform;
        QTransform det2imgTransform;
        
        QGraphicsItemGroup imgGroup;
    protected slots:
        virtual void updateImgTransformations();
};



#endif
