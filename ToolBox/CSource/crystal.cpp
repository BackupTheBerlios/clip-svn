
#include <cmath>
#include <iostream>
#include <projector.h>
#include <crystal.h>

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
    Qmin=0.0;
    Qmax=1.0;
    connect(&connectedProjectors, SIGNAL(objectAdded()), this, SLOT(updateWavevectorsFromProjectors()));
    connect(&connectedProjectors, SIGNAL(objectRemoved()), this, SLOT(updateWavevectorsFromProjectors()));

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
    addRotation(Mat3D(axis, angle));
}

void Crystal::addRotation(const Mat3D& M) {
    MRot = M * MRot;
    MRot.orthogonalize();
    updateRotation();
    emit orientationChanged();
    emit reflectionsUpdate();
}

void Crystal::setRotation(const Mat3D& M) {
    MRot = M;
    updateRotation();
    emit orientationChanged();
    emit reflectionsUpdate();
}

void Crystal::setWavevectors(double _Qmin, double _Qmax) {
    if ((_Qmin<_Qmax) and ((_Qmin!=Qmin) or (_Qmax!=Qmax))) {
        Qmax=_Qmax;
        Qmin=_Qmin;
        reflections.clear();
        emit reflectionsUpdate();
    }
}

void Crystal::generateReflections() {
    reflections.clear();
    // Q=pi/d/sin(theta)
    // n*lambda=2*d*sin(theta) => n=2*d/lambda = 2*d*Q/2/pi
    int hMax = int(a*Qmax*M_1_PI);
    //cout << "hMax: " << hMax << endl;
    for (int h=-hMax; h<=hMax; h++) {

        //|h*as+k*bs|^2=h^2*|as|^2+k^2*|bs|^2+2*h*k*as*bs==(2*Qmax/2/pi)^2
        // k^2 +2*k *h*as*bs/|bs|^2 + (h^2*|as|^2-Qmax/pi)/|bs|^2 == 0
        double ns = 1.0/bstar.norm_sq();
        double p = astar*bstar*ns*h;
        double q1 = astar.norm_sq()*ns*h*h;
        double q2 = ns*Qmax*Qmax*M_1_PI*M_1_PI;
        double s = p*p-q1+q2;
        int kMin = (s>0)?int(-p-sqrt(s)):0;
        int kMax = (s>0)?int(-p+sqrt(s)):0;
        
        Vec3D v1=astar*h+bstar*kMin;
        Vec3D v2=astar*h+bstar*kMax;
        //cout << "kMin " << h << " " << kMin << " " << kMax << " " << v1.norm() << " " << v2.norm() << " " << Qmax*M_1_PI << endl;
        for (int k=kMin; k<=kMax; k++) {
      
            Vec3D v = MReziprocal*Vec3D(h,k,0);
            ns = 1.0/cstar.norm_sq();      
            p = v*cstar*ns;
            q1 = v.norm_sq()*ns;
            q2 = ns*Qmax*Qmax*M_1_PI*M_1_PI;
            s = p*p-q1+q2;	
            int lMin = (s>0)?int(-p-sqrt(s)):0;
            int lMax = (s>0)?int(-p+sqrt(s)):0;

            for (int l=lMin; l<=lMax; l++) {
                // store only lowest order reflections
                if (ggt(h,ggt(k,l))==1) {
                    v=MReziprocal*Vec3D(h,k,l);
                    double Q = 2.0*M_PI*v.norm();

                    if (Q<=2.0*Qmax) {
                        Reflection r;
                        r.h=h;
                        r.k=k;
                        r.l=l;
                        r.Q=Q;
                        r.d = 2.0*M_PI/Q;
                        for (unsigned int i=1; i<int(2.0*Qmax/r.Q+0.9); i++) {
                            // TODO: check sys absents
                            r.orders.push_back(i);
                        }

                        r.normalLocal=v*r.d;
                        reflections.push_back(r);
                        
                    }
                } 
            }
        }
    }
    updateRotation();
}
  
void Crystal::updateRotation() {
    for (unsigned int i=reflections.size(); i--; ) {
        Reflection &r = reflections[i];
        r.normal=MRot*r.normalLocal;
        r.lowestDiffOrder=0;

        // sin(theta) = v*e_x = v.x
        // x direction points toward source, z points upwards
        if (r.normal.x()>0.0) {
            //Q=pi/d/sin(theta)=0.5*r.Q/sin(theta)
            r.Qscatter = 0.25*M_1_PI*r.Q/r.normal.x();
            // Loop over higher orders
    
            for (unsigned int j=0; j<r.orders.size(); j++) {
                unsigned int n=r.orders[j];
                if  ((r.lowestDiffOrder==0) and (n*r.Qscatter>=Qmin) and (n*r.Qscatter<=Qmax)) {
                    r.lowestDiffOrder=n;
                    break;
                }
            }
        }
        if (r.lowestDiffOrder!=0) 
            r.scatteredRay = Projector::normal2scattered(r.normal);
        else
            r.scatteredRay = Vec3D();
    }
};
                            

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
    connect(p, SIGNAL(wavevectorsUpdated()), this, SLOT(updateWavevectorsFromProjectors()));
}


void Crystal::updateWavevectorsFromProjectors() {
    double hi;
    double lo;
    for (unsigned int i=0; i<connectedProjectors.size(); i++) {
        Projector* p=dynamic_cast<Projector*>(connectedProjectors.at(i));
        if ((i==0) or (p->Qmin()<lo))
            lo=p->Qmin();
        if ((i==0) or (p->Qmax()>hi))
            hi=p->Qmax();
    }
    setWavevectors(lo,hi);
}
