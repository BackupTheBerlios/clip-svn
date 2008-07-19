#ifndef __INDEXER_H__
#define __INDEXER_H__

#include <QtCore/QAbstractTableModel>
#include <QtCore/QRunnable>
#include <QtCore/QMutex>
#include <vec3D.h>
#include <reflection.h>


class SolutionItem {
    public:            
        int h;
        int k;
        int l;
        Vec3D rotatedMarker;
        Vec3D rationalHkl;
        Vec3D latticeVector;
        bool initialIndexed;        
        double angularDeviation() const;
        double spatialDeviation() const;
        double hklDeviation() const;
};

class Solution {
    public:
        Solution() {};
        Solution(const Solution& s) {
            items=s.items;
            indexingRotation=s.indexingRotation;
            bestRotation=s.bestRotation;
        };
        Solution operator=(const Solution& s) {
            items=s.items;
            indexingRotation=s.indexingRotation;
            bestRotation=s.bestRotation;
            return *this;                
        };
        QList<SolutionItem> items;
        Mat3D indexingRotation;
        Mat3D bestRotation;
        double angularDeviationSum() const;
        double spatialDeviationSum() const;
        double hklDeviationSum() const;
        
};

Q_DECLARE_METATYPE(Solution)

class Indexer: public QAbstractTableModel {
    Q_OBJECT
    public:
        struct IndexingParameter {
            QList<Vec3D> markerNormals;
            QList<Reflection> refs;
            QList<Mat3D> pointGroup;
            double maxAngularDeviation;
            double maxIntegerDeviation;
            unsigned int maxOrder;
            Mat3D orientationMatrix;
        };
            


        Indexer(QObject* parent=0);
        virtual int rowCount(const QModelIndex & parent = QModelIndex()) const;
        virtual int columnCount(const QModelIndex & parent = QModelIndex()) const ;
        virtual QVariant data(const QModelIndex & index, int role = Qt::DisplayRole) const;
        virtual QVariant headerData(int section, Qt::Orientation orientation, int role = Qt::DisplayRole) const;
        virtual void sort(int column, Qt::SortOrder order = Qt::AscendingOrder) ;
        
    
        void startIndexing(IndexingParameter& p);
        Solution getSolution(unsigned int n);
        
    public slots:
        void addSolution(Solution s);
        void threadFinished();
    
    signals:
        void stopWorker();
        void runningStateChanged(bool);
    private:
        class SolSort {
            public:
                SolSort(int col, Qt::SortOrder order);
                bool operator()(const Solution& s1,const Solution& s2);
            private:
                int sortColumn;
                Qt::SortOrder sortOrder;
        };
            
    
        QList<Solution> solution;
        int sortColumn;
        Qt::SortOrder sortOrder;
        IndexingParameter p;
};

class IndexWorker: public QObject, public QRunnable {
    Q_OBJECT
    protected:
        class AngleInfo {
            public:
                bool operator<(const AngleInfo &o) const;
                static bool cmpAngleInfoLowerBound(const AngleInfo &a1, const AngleInfo &a2);
                static bool cmpAngleInfoUpperBound(const AngleInfo &a1, const AngleInfo &a2);
                int index1, index2;
                double lowerBound;
                double cosAng;
                double upperBound;
        };
    public:
        IndexWorker(Indexer::IndexingParameter& p);

        void run();
        
        void checkGuess(const Reflection &c1, const Reflection &c2,  const IndexWorker::AngleInfo &a);
        void otimizeScale(SolutionItem& si);
    
        bool nextWork(int &i, int &j);
    
    public slots:
        void stop();
        
    signals:
        void publishSolution(Solution s);
    protected:
    
        bool newSolution(const Mat3D& M);

    
        int indexI;
        int indexJ;
        bool shouldStop;
        QMutex indexMutex;
    
        bool isInitiatingThread;
        QList<AngleInfo> angles;
        
        Indexer::IndexingParameter p;
        
        Mat3D OMatInv;

        QMutex solRotLock;
        QList<Mat3D> solutionRotations;
    
};

#endif
