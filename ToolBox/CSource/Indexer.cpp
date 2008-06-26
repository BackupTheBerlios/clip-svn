#include <Indexer.h>
#include <QtCore/QThreadPool>
#include <QtCore/QMutexLocker>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <QtCore/QtAlgorithms>

#include <vec3D.h>
#include <mat3D.h>



using namespace std;

Indexer::Indexer(QObject* parent): QAbstractTableModel(parent) {}

int Indexer::rowCount(const QModelIndex & parent) const {
    return solution.count();
}

int Indexer::columnCount(const QModelIndex & parent) const {
    return 3;
}

QVariant Indexer::data(const QModelIndex & index, int role) const {
    if (role==Qt::DisplayRole) {
        if (index.column()==0) {
            return QVariant(solution.at(index.row()).spatialDeviationSum());
        } else if (index.column()==1) {
            return QVariant(solution.at(index.row()).angularDeviationSum());
        } else if (index.column()==2) {
            return QVariant(solution.at(index.row()).hklDeviationSum());
        }
    }
    return QVariant();
}

QVariant Indexer::headerData(int section, Qt::Orientation orientation, int role) const {
    if (role==Qt::DisplayRole) {
        if (orientation==Qt::Horizontal) {
            if (section==0) {
                return QVariant("Spacial");
            } else if (section==1) {
                return QVariant("Angular");
            } else if (section==2) {
                return QVariant("HKL");
            }
        } else {
            return QVariant(section+1);
        }
    } 
    return QVariant();
}
    

void Indexer::sort(int column, Qt::SortOrder order) {
    sortColumn=column;
    sortOrder=order;
    qSort(solution.begin(), solution.end(), SolSort(sortColumn, sortOrder));
    reset();
}
    
void Indexer::startIndexing(Indexer::IndexingParameter& p) {
    solution.clear();
    reset();
    IndexWorker* worker=new IndexWorker(p);
    qRegisterMetaType<Solution>();
    connect(worker, SIGNAL(publishSolution(Solution)), this, SLOT(addSolution(Solution)));
    connect(worker, SIGNAL(destroyed()), this, SLOT(threadFinished()));
    QThreadPool::globalInstance()->start(worker);
}
    
void Indexer::addSolution(Solution s) {
    QList<Solution>::iterator iter=qLowerBound(solution.begin(), solution.end(), s, SolSort(sortColumn, sortOrder));
    QList<Solution>::iterator saveiter=iter;
    SolSort less(sortColumn, sortOrder);
    bool differs=true;
    while (iter!=solution.end() and s.angularDeviationSum()==iter->angularDeviationSum()) {
        // TODO: Try Matrics from Laue Group
        Mat3D M(s.bestRotation);
        M*=iter->bestRotation.transposed();
        M-=Mat3D();
        if (M.sqSum()<1e-15) {
            differs=false;
            iter=solution.end();
        } else {
            iter++;
        }
    }
    if (differs) {
        int n=saveiter-solution.begin();
        beginInsertRows(QModelIndex(),n,n);
        solution.insert(saveiter,s);
        endInsertRows();
    } else {
        cout << "Skip Sol" <<  endl;
    }
}

Solution Indexer::getSolution(unsigned int n) {
    return solution[n];
}

void Indexer::threadFinished() {
    cout << "Thread finished and destroyed" << endl;
}


Indexer::SolSort::SolSort(int col, Qt::SortOrder order) {
    sortColumn=col;
    sortOrder=order;
};

bool Indexer::SolSort::operator()(const Solution& s1,const Solution& s2) {
    bool b=true;
    if (sortColumn==0) {
        b=s1.angularDeviationSum()<s2.angularDeviationSum();
    } else if (sortColumn==1) {
        b=s1.spatialDeviationSum()<s2.spatialDeviationSum();
    } else if (sortColumn==2) {
        b=s1.hklDeviationSum()<s2.hklDeviationSum();
    }
    if (sortOrder==Qt::DescendingOrder)
        b=not b;
    return b;
}










double SolutionItem::angularDeviation() const {
    return fabs(acos(rotatedMarker*latticeVector));
}

double SolutionItem::spatialDeviation() const {
    return fabs((rotatedMarker-latticeVector).norm());
}

double SolutionItem::hklDeviation() const {
    return fabs(rationalHkl[0]-h)+fabs(rationalHkl[1]-k)+fabs(rationalHkl[2]-l);
}

double Solution::angularDeviationSum() const {
    double s=0.0;
    for (unsigned int n=items.size(); n--; )
        s+=items.at(n).angularDeviation();
    return s;
}

double Solution::spatialDeviationSum() const {
    double s=0.0;
    for (unsigned int n=items.size(); n--; )
        s+=items.at(n).spatialDeviation();
    return s;
}

double Solution::hklDeviationSum() const {
    double s=0.0;
    for (unsigned int n=items.size(); n--; )
        s+=items.at(n).hklDeviation();
    return s;
}





IndexWorker::IndexWorker(Indexer::IndexingParameter &p): QObject(), QRunnable(), indexMutex(), refs(), markerNormals(), angles() {
    indexI=1;
    indexJ=0;
    isInitiatingThread=true;
    markerNormals=p.markerNormals;
    refs=p.refs;
    maxAng=M_PI*p.maxAngularDeviation/180.0;
    maxIntDev=p.maxIntegerDeviation;
    maxOrder=p.maxOrder;
    OMat=p.orientationMatrix;    
    OMatInv=OMat.inverse();
        
    for (unsigned int i=markerNormals.size(); i--; ) {
        for (unsigned int j=i; j--; ) {
            AngleInfo info;
            info.index1=i;
            info.index2=j;
            info.cosAng=markerNormals.at(i)*markerNormals.at(j);
            double c=acos(info.cosAng);
            double c1=cos(c+maxAng);
            double c2=cos(c-maxAng);
            info.lowerBound=(c1<c2)?c1:c2;
            info.upperBound=(c1>c2)?c1:c2;
            angles.append(info);
        }
    }
    qSort(angles);
}

void IndexWorker::run() {
    if (isInitiatingThread) {
        isInitiatingThread=false;
        unsigned int count=0;
        while (QThreadPool::globalInstance()->tryStart(this)) {
            count++;
        }
        cout << "Started " << count << " additional threads" << endl;
    }
    int i, j;
    AngleInfo lower;

    while (nextWork(i,j)) {
        double cosAng=refs.at(i).normalLocal*refs.at(j).normalLocal;
        lower.upperBound=cosAng;
        QList<IndexWorker::AngleInfo>::iterator iter=qLowerBound(angles.begin(), angles.end(), lower, IndexWorker::AngleInfo::cmpAngleInfoUpperBound);
        bool ok=false;
        while (iter!=angles.end() && cosAng>=iter->lowerBound) {
            if (iter->lowerBound<=cosAng && cosAng<iter->upperBound) {
                checkGuess(refs.at(i), refs.at(j),  *iter);
                checkGuess(refs.at(j), refs.at(i),  *iter);
            }
            iter++;
        }
    }
}

Mat3D bestRotation(Mat3D M) {
    Mat3D L,R;
    M.svd(L,R);
    double d=L.det()*R.det();
    if (d<0.0) {
        Mat3D T;
        *T.at(2,2)=-1.0;
        return L*T*R;
    } else {
        return L*R;
    }
};

void IndexWorker::checkGuess(const Reflection &c1, const Reflection &c2,  const AngleInfo &a) {
    // Prepare Best Rotation Matrix from c1,c2 -> a(1) a(2)
    Mat3D R=c1.normalLocal^markerNormals[a.index1];
    R+=(c2.normalLocal^markerNormals[a.index2]);
    
    R=bestRotation(R);


    // Try Indexation of missing reflexions
    Solution s;
    s.indexingRotation=R;
    
    for (unsigned int n=markerNormals.size(); n--; ) {
        SolutionItem si;
        Vec3D hklUnitVect(OMatInv*R*markerNormals.at(n));
        hklUnitVect.normalize();
        si.initialIndexed=true;
        if (n==a.index1) {
            si.h=c1.h;
            si.k=c1.k;
            si.l=c1.l;
            s.items.append(si);
        } else if (n==a.index2) {
            si.h=c2.h;
            si.k=c2.k;
            si.l=c2.l;
            s.items.append(si);
        } else {
            si.initialIndexed=false;
            bool ok;
            for (unsigned int order=1; order<=maxOrder; order++) {
                ok=true;
                // TODO: Not all ints are possible!!!
                double scale=sqrt(order);
                Vec3D t(hklUnitVect*scale);
                for (unsigned int i=3; i--; ) {
                    if (fabs(fabs(t[i])-round(fabs(t[i])))>maxIntDev) {
                        ok=false;
                        break;
                    }
                }
                if (ok) {
                    si.h=(int)round(t[0]);
                    si.k=(int)round(t[1]);
                    si.l=(int)round(t[2]);
                    s.items.append(si);
                    break;
                }
            }
            if (not ok) 
                break;
        }
    }
    
    if (markerNormals.size()==s.items.size()) {
        // yes, we have a solution!!!
        R*=0.0;
        for (unsigned int n=s.items.size(); n--; ) {
            SolutionItem& si = s.items[n];
            Vec3D v(si.h, si.k, si.l);
            v=OMat*v;
            v.normalize();
            si.latticeVector=v;            
            R+=v^markerNormals[n];
        }
        s.bestRotation=bestRotation(R);
        for (unsigned int n=s.items.size(); n--; ) {
            SolutionItem& si = s.items[n];
            si.rotatedMarker=s.bestRotation*markerNormals.at(n);
            otimizeScale(si);
        }
        emit publishSolution(s);
    }
    
}

void IndexWorker::otimizeScale(SolutionItem& si) {
    Vec3D hkl(si.h,si.k,si.l);
    si.rationalHkl=OMatInv*si.rotatedMarker;
    si.rationalHkl*=hkl*si.rationalHkl/si.rationalHkl.norm_sq();
    //sum (hkl-scale*rhkl)^2 = min
    // dsum/scale = 2sum (hkl_i-s*rhkl_i)*rhkl_i == 0!
    // => s* sum( rhkl_i^2 ) = sum ( rhkl_i * hkl_i )
}

bool IndexWorker::nextWork(int &i, int &j) {
    QMutexLocker lock(&indexMutex);
    if (indexI>=refs.size())
        return false;

    i=indexI;
    j=indexJ;
    
    indexJ++;
    if (indexJ==indexI) {
        indexI++;
        indexJ=0;
    }
    return true;
}    

bool IndexWorker::AngleInfo::operator<(const AngleInfo& o) const {
    return cosAng<o.cosAng;
}

bool IndexWorker::AngleInfo::cmpAngleInfoLowerBound(const AngleInfo &a1, const AngleInfo &a2) {
    return a1.lowerBound<a2.lowerBound;
}
bool IndexWorker::AngleInfo::cmpAngleInfoUpperBound(const AngleInfo &a1, const AngleInfo &a2) {
    return a1.upperBound<a2.upperBound;
}


