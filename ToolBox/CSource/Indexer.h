#ifndef __INDEXER_H__
#define __INDEXER_H__

#include <QtCore/QAbstractTableModel>
#include <QtCore/QRunnable>
#include <QtCore/QMutex>
#include <vec3D.h>
#include <reflection.h>




class Indexer: QAbstractTableModel {
    public:
        Indexer();
        int rowCount(const QModelIndex & parent = QModelIndex());
        int columnCount(const QModelIndex & parent = QModelIndex());
        QVariant data(const QModelIndex & index, int role = Qt::DisplayRole);
        void sort(int column, Qt::SortOrder order = Qt::AscendingOrder);
    
        void startIndexing();
    
    
};


class SolutionItem {
    public:            
        int h;
        int k;
        int l;
        Vec3D rotatedMarker;
        Vec3D rationalHkl;
        Vec3D latticeVector;
        bool initialIndexed;        
};

class Solution {
    public:
        QList<SolutionItem> items;
        Mat3D indexingRotation;
        Mat3D bestRotation;
};



class AngleInfo {
    public:
        bool operator<(const AngleInfo &o) const  {return cosAng<o.cosAng; };
        int index1, index2;
        double lowerBound;
        double cosAng;
        double upperBound;
};

class IndexWorker: public QRunnable {
    public:
        IndexWorker();
        void setMarkerNormals(QList<Vec3D> _markerNormals);
        void setRefs(QList<Reflection> _refs);
        void setMaxAngularDeviation(double _maxAng);
        void setMaxIntegerDeviation(double _maxSpace);
        void setMaxVectorOrder(unsigned int _maxOrder);
        void setOrientationMatrix(const Mat3D& _OM);

        void run();
        
        void checkGuess(const Reflection &c1, const Reflection &c2,  const AngleInfo &a);
        void otimizeScale(SolutionItem& si);
    
        bool nextWork(int &i, int &j);
    protected:
        int indexI;
        int indexJ;
        QMutex indexMutex;
        bool isInitiatingThread;
        QList<AngleInfo> angles;
        QList<Vec3D> markerNormals;
        QList<Reflection> refs;
        double maxAng;
        double maxIntDev;
        unsigned int maxOrder;
        Mat3D OMat;
        Mat3D OMatInv;
        
        unsigned int solutionCount;
};

#endif
