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
            bool ok=true;
            for (unsigned int order=1; order<=maxOrder; order++) {
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
                    hklUnitVect*=scale;
                    si.h=(int)round(hklUnitVect[0]);
                    si.k=(int)round(hklUnitVect[1]);
                    si.l=(int)round(hklUnitVect[2]);
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
            const SolutionItem& si = s.items.at(n);
            Vec3D v(si.h, si.k, si.l);
            v=OMat*v;
            v.normalize();
            si.latticeVector=v;
            R+=v^markerNormals[n];
        }
        si.rotatedMarker=R*markerNormals.at(n);
        otimizeScale(si);
        s.bestRotation=bestRotation(R);
        solutionCount++;
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
