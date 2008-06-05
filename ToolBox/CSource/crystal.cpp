
#include <cmath>
#include <iostream>
#include "crystal.h"

using namespace std;

int ggt(int a, int b) {
    while (b) {
        int tb=b;
        b=a%b;
        a=tb;
    }
    return abs(a);
}

Crystal::Crystal(): reflections(), MReal(), MReziprocal(), MRot(), connectedProjectors(this) {
    setCell(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    upperLambda = 1000000.0;
    lowerLambda = 0.1;
    self.connect(connectedProjectors, SIGNAL(objectAdded()), this, SLOT(updateWavelengthFromProjectors()));
    self.connect(connectedProjectors, SIGNAL(objectRemoved()), this, SLOT(updateWavelengthFromProjectors()));

}

Crystal::Crystal(const Crystal& c) {};

Crystal::~Crystal() {};
 
void Crystal::setCell(double _a, double _b, double _c, double _alpha, double _beta, double _gamma) {
    // discard minor changes (may affect fit)
    if (fabs(_a-a)>1e-8 || fabs(_b-b)>1e-8 || fabs(_c-c)>1e-8 || fabs(_alpha-alpha)>1e-8 ||fabs(_beta-beta)>1e-8 || fabs(_gamma-gamma)>1e-8) {
        a=_a;
        b=_b;
        c=_c;
        alpha=_alpha;
        beta=_beta;
        gamma=_gamma;

        // Clear old reflections, will be automatically regenerated if needed
        reflections.clear();

        // Cosini und Sini of angles between lattice vectors
        double Ca=cos(M_PI/180.0*alpha);
        double Cb=cos(M_PI/180.0*beta);
        double Cc=cos(M_PI/180.0*gamma);
        double Sc=sin(M_PI/180.0*gamma);
    
        // volume of the unit cell in real abnd reziprocal space
        double Vreal=a*b*c*sqrt(1.0+2.0*Ca*Cb*Cc-Ca*Ca-Cb*Cb-Cc*Cc);
        double Vrezi=1.0/Vreal;
        
        // in real space, a directs in x-direction, b is in the xy-plane and c completes the right handed set
        Vec3D a_real(a, 0, 0);
        Vec3D b_real(Cc*b, Sc*b, 0);
        Vec3D c_real(Cb, (Ca-Cb*Cc)/Sc, sqrt(1.0-Cb*Cb-(Ca-Cb*Cc)/Sc*(Ca-Cb*Cc)/Sc));
        c_real *= c;
  
        MReal=Mat3D(a_real, b_real, c_real);

        // reciprocal orientation matrix is inverse transposed of real one!
        MReziprocal = MReal.inverse().transpose();
        astar=MReziprocal[0];
        bstar=MReziprocal[1];
        cstar=MReziprocal[2];
        emit cellChanged();
        emit reflectionsUpdate();
    }
}

void Crystal::addRotation(const Vec3D& axis, double angle) {
    MRot *= Mat3D(axis, angle);
    MRot.orthogonalize();
    reflections.clear();
    emit orientationChanged();
    emit reflectionsUpdate();
}

void Crystal::setRotation(const Mat3D& M) {
    MRot = M;
    reflections.clear();
    emit orientationChanged();
    emit reflectionsUpdate();
}

void Crystal::setWavelengthBoundarys(double lower, double upper) {
    lowerLambda=lower;
    upperLambda=upper;
    reflections.clear();
    emit reflectionsUpdate();
}

void Crystal::generateReflections() {
    reflections.clear();
    int hMax = int(a/lowerLambda);
    //cout << "hMax: " << hMax << endl;
    for (int h=-hMax; h<=hMax; h++) {

        double ns = 1.0/bstar.norm_sq();
        double p = astar*bstar*ns*h;
        double q1 = astar.norm_sq()*ns*h*h;
        double q2 = ns/lowerLambda/lowerLambda;
        double s = p*p-q1+q2;
        int kMax = (s>0)?int(sqrt(s)+abs(p)):0;

        for (int k=-kMax; k<=kMax; k++) {
      
            Vec3D v = MReziprocal*Vec3D(h,k,0);

            ns = 1.0/cstar.norm_sq();      
            p = v*cstar*ns;
            q1 = v.norm_sq()*ns;
            q2 = ns/lowerLambda/lowerLambda;
            s = p*p-q1+q2;	
        
            int lMax = (s>0)?int(sqrt(s)+abs(p)):0;
            for (int l=-lMax; l<=lMax; l++) {
                // store only lowest order reflections
                if (ggt(h,ggt(k,l))==1) {
                    v=MReziprocal*Vec3D(h,k,l);
                    double d = 1.0/v.norm();

                    if (d>lowerLambda) {
                        Reflection r;
                        r.h=h;
                        r.k=k;
                        r.l=l;
                        r.d = d;
                        r.lowestDiffOrder=0;

                        v*=d;
                        v=MRot*v;
                        r.normal = v;
                        // sin(theta) = v*e_x = v.x
                        // x direction points toward source, z points upwards
                        double scatterLambda = 2.0*r.d*v.x();
                        // Loop over higher orders
                        
                        int NMax = int(d/lowerLambda+0.9);
                        for (int n=1; n<=NMax; n++) {
                            // Check sysAbsents
                            r.orders.push_back(n);
                            if  ((r.lowestDiffOrder==0) and (n*lowerLambda<=scatterLambda) and (n*upperLambda>=scatterLambda))
                                r.lowestDiffOrder=n;
                        }
                        if (!r.orders.empty()) {
                            if (r.lowestDiffOrder!=0) 
                                r.scatteredRay = Projector::normal2scattered(v);
                            reflections.push_back(r);
                        }
                    }
                } 
            }
        }
    }
}
  


unsigned int Crystal::reflectionCount() {
    std::vector<Reflection>& r = getReflectionList();
    return r.size();
}

Reflection Crystal::getReflection(unsigned int i) {
    std::vector<Reflection>& r = getReflectionList();
    if (i<r.size()) {
        return r[i];
    } else {
        return Reflection();
    }
}
  
std::vector<Reflection>& Crystal::getReflectionList() {
    if (reflections.empty()) 
        generateReflections();
    return reflections;
}


Vec3D Crystal::uvw2Real(const Vec3D& v) {
    return MRot*MReal*v;
}

Vec3D Crystal::uvw2Real(const int u, const int v, const int w) {
    return uvw2Real(Vec3D(u,v,w));
}


Vec3D Crystal::hkl2Reziprocal(const Vec3D& v) {
    return MRot*MReziprocal*v;
}

Vec3D Crystal::hkl2Reziprocal(const int h, const int k, const int l) {
    return hkl2Reziprocal(Vec3D(h,k,l));
}


Mat3D Crystal::getRealOrientationMatrix() {
    return MReal;
}

Mat3D Crystal::getReziprocalOrientationMatrix() {
    return MReziprocal;
}

Mat3D Crystal::getRotationMatrix() {
    return MRot;
}

void Crystal::addProjector(Projector* p) {
    connectedProjectors.addObject(p);
    connect(p, SIGNAL(wavelengthUpdated()), this, SLOT(updateWavelengthFromProjectors()));
}


void Crystal::updateWavelengthFromProjectors() {
    double up=10000.0;
    double lo=1.0;
    for (unsigned int i=0; i<connectedProjectors.size(); i++) {
        Projector* p=dynamic_cast<Projector*>(connectedProjectors.at(i));
        if ((i==0) or (p->lowerWavelength()<lo))
            lo=p->lowerWavelength();
        if ((i==0) or (p->upperWavelength()<up))
            up=p->upperWavelength();
    }
    if ((up!=upperLambda) or (lo!=lowerLambda)) 
        setWavelengthBoundaries(lo,up);
}
