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

bool cmpAngleInfoLowerBound(const AngleInfo &a1, const AngleInfo &a2) {
    return a1.lowerBound<a2.lowerBound;
};

bool cmpAngleInfoUpperBound(const AngleInfo &a1, const AngleInfo &a2) {
    return a1.upperBound<a2.upperBound;
};


IndexWorker::IndexWorker(): indexMutex(), refs(), markerNormals(), angles() {
    indexI=1;
    indexJ=0;
    isInitiatingThread=true;
    solutionCount=0;
}

void IndexWorker::setMarkerNormals(QList<Vec3D> _markerNormals) {
    markerNormals=_markerNormals;
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
void IndexWorker::setRefs(QList<Reflection> _refs) {
    refs=_refs;  
}

void IndexWorker::setMaxAngularDeviation(double _maxAng) {
    maxAng=M_PI*_maxAng/180.0;
    for (unsigned int i=angles.size(); i--; ) {
        double c=acos(angles.at(i).cosAng);
        double c1=cos(c+maxAng);
        double c2=cos(c-maxAng);
        angles[i].lowerBound=(c1<c2)?c1:c2;
        angles[i].upperBound=(c1>c2)?c1:c2;
    }
}

void IndexWorker::setMaxIntegerDeviation(double _maxIntDev) {
    maxIntDev=_maxIntDev;
}

void IndexWorker::setMaxVectorOrder(unsigned int _maxOrder) {
    maxOrder=_maxOrder;
}

void IndexWorker::setOrientationMatrix(const Mat3D& _OM) {
    OMat=_OM;
    OMatInv=OMat.inverse();
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
        QList<AngleInfo>::iterator iter=qLowerBound(angles.begin(), angles.end(), lower, cmpAngleInfoUpperBound);
        bool ok=false;
        while (iter!=angles.end() && cosAng>=iter->lowerBound) {
            if (iter->lowerBound<=cosAng && cosAng<iter->upperBound) {
                checkGuess(refs.at(i), refs.at(j),  *iter);
                checkGuess(refs.at(j), refs.at(i),  *iter);
            }
            iter++;
        }
    }
    cout << "Solutions: " << solutionCount << endl;
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
    Mat3D T(OMatInv*R);


    // Try Indexation of missing reflexions
    Solution s;
    s.indexingRotation=R;
    
    for (unsigned int n=markerNormals.size(); n--; ) {
        SolutionItem si;
        si.bestScale=0.0;
        si.marker=markerNormals.at(n);
        si.hklUnitVect=T*si.marker;
        si.hklUnitVect.normalize();
        si.initialIndexed=true;
        if (n==a.index1) {
            si.bestScale=sqrt(c1.hklSqSum);
        } else if (n==a.index2) {
            si.bestScale=sqrt(c2.hklSqSum);
        } else {
            si.initialIndexed=false;
            for (unsigned int order=1; order<=maxOrder; order++) {
                // TODO: Not all ints are possible!!!
                double scale=sqrt(order);
                Vec3D t(si.hklUnitVect*scale);
                bool ok=true;
                for (unsigned int i=3; i--; ) {
                    if (fabs(fabs(t[i])-round(fabs(t[i])))>maxIntDev) {
                        ok=false;
                        break;
                    }
                }
                if (ok) {
                    si.bestScale=scale;
                    break;
                }
            }
        }
        if (si.bestScale!=0.0) {
            otimizeScale(si);
            si.rationalHkl=si.hklUnitVect*si.bestScale;
            si.h=(int)round(si.rationalHkl[0]);
            si.k=(int)round(si.rationalHkl[1]);
            si.l=(int)round(si.rationalHkl[2]);
            s.items.append(si);
        } else {
            break;
        }
    }
    
    if (markerNormals.size()==s.items.size()) {
        // yes, we have a solution!!!
        R*=0.0;
        for (unsigned int n=s.items.size(); n--; ) {
            const SolutionItem& si = s.items.at(n);
            Vec3D v(si.h, si.k, si.l);
            v=OMat*v;
            v.normalize();
            R+=v^si.marker;
        }
        s.bestRotation=bestRotation(R);
        solutionCount++;
    }
    
}

void IndexWorker::otimizeScale(SolutionItem& si) {
    //TODO: Implementation!!!
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
