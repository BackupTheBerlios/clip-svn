class Indexer: QAbstractTableModel {

%TypeHeaderCode
#include <Indexer.h>
%End

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
};


class SolutionItem {
%TypeHeaderCode
#include <Indexer.h>
%End
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
%TypeHeaderCode
#include <Indexer.h>
%End
    public:
        Solution();
        QList<SolutionItem> items;
        Mat3D indexingRotation;
        Mat3D bestRotation;
        double angularDeviationSum() const;
        double spatialDeviationSum() const;
        double hklDeviationSum() const;
        
};

