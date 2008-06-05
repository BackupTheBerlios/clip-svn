#ifndef __projector_h__
#define __projector_h__

#include <vector>
#include <reflection.h>
#include <qobject.h>
#include <qvector.h>
#include <qpointf.h>


class Projector: public QObject {
    Q_OBJECT
    public:
        Projector();
        QVector<QPointF> projectedPoints;    
    public slots:
        void setReflections(const std::vector<reflections> &ref);
    signals:  
        void projectedPointsUpdated();
};

class PlaneProjector: public Projector {
    Q_OBJECT
    public:
        PlaneProjector();
        void calcProjection();
        QVector<QPointF> projectedPoints;
    
    public slots:
        void setReflections(const std::vector<reflections> &ref);
    signals:  
        void projectedPointsUpdated();
};




#endif
