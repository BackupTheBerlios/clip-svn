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

Crystal::Crystal(): QObject(), FitObject(), reflections(), MReal(), MReziprocal(), MRot(), connectedProjectors(this), rotationAxis(1,0,0) {
    setCell(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    Qmin=0.0;
    Qmax=1.0;
    connect(&connectedProjectors, SIGNAL(objectAdded()), this, SLOT(updateWavevectorsFromProjectors()));
    connect(&connectedProjectors, SIGNAL(objectRemoved()), this, SLOT(updateWavevectorsFromProjectors()));
    axisType=LabSystem;
    enableUpdate();
    QList<int> constrains;
    constrains << 0 << 0 << 0 << 0 << 0 << 0;
    setSpacegroupConstrains(constrains);
    setSpacegroupSymbol("P1");
}

Crystal::Crystal(const Crystal& c) {
    cout << "Crystal Copy Constructor" << endl;
    setCell(c.a,c.b,c.c,c.alpha,c.beta,c.gamma);
    Qmin=c.Qmin;
    Qmax=c.Qmax;
    connect(&connectedProjectors, SIGNAL(objectAdded()), this, SLOT(updateWavevectorsFromProjectors()));
    connect(&connectedProjectors, SIGNAL(objectRemoved()), this, SLOT(updateWavevectorsFromProjectors()));
    
    setRotation(c.getRotationMatrix());
    setSpacegroupSymbol(c.getSpacegroupSymbol());
    setRotationAxis(c.getRotationAxis(), c.getRotationAxisType());
    enableUpdate(c.updateEnabled);
};

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
        MReziprocal = MReal.inverse();
        MReziprocal.transpose();
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
    #ifdef __DEBUG__
    cout << "AddRotation" << endl;
    #endif
    MRot = M * MRot;
    MRot.orthogonalize();
    updateRotation();
    emit orientationChanged();
    emit reflectionsUpdate();
}

void Crystal::setRotation(const Mat3D& M) {
    #ifdef __DEBUG__
    cout << "setRotation" << endl;
    #endif
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
    if (not updateEnabled)
        return;
    #ifdef __DEBUG__
    cout << "Generate Reflextions" << endl;
    #endif
    reflections.clear();
    // Q=0.5/d/sin(theta)
    // n*lambda=2*d*sin(theta) => n=2*d/lambda = 2*Q*d
    int hMax = int(2.0*a*Qmax);
    //cout << "hMax: " << hMax << endl;
    for (int h=-hMax; h<=hMax; h++) {

        //|h*as+k*bs|^2=h^2*|as|^2+k^2*|bs|^2+2*h*k*as*bs==(2*Qmax)^2
        // k^2 +2*k *h*as*bs/|bs|^2 + (h^2*|as|^2-4*Qmax^2)/|bs|^2 == 0
        double ns = 1.0/bstar.norm_sq();
        double p = astar*bstar*ns*h;
        double q1 = astar.norm_sq()*ns*h*h;
        double q2 = 4.0*ns*Qmax*Qmax;
        double s = p*p-q1+q2;
        int kMin = (s>0)?int(-p-sqrt(s)):0;
        int kMax = (s>0)?int(-p+sqrt(s)):0;
        
        for (int k=kMin; k<=kMax; k++) {

            Vec3D v = MReziprocal*Vec3D(h,k,0);
            ns = 1.0/cstar.norm_sq();      
            p = v*cstar*ns;
            q1 = v.norm_sq()*ns;
            q2 = 4.0*ns*Qmax*Qmax;
            s = p*p-q1+q2;	
            int lMin = (s>0)?int(-p-sqrt(s)):0;
            int lMax = (s>0)?int(-p+sqrt(s)):0;

            for (int l=lMin; l<=lMax; l++) {
                // store only lowest order reflections
                if (ggt(h,ggt(k,l))==1) {
                    v=MReziprocal*Vec3D(h,k,l);
                    double Q = 0.5*v.norm();

                    if (Q<=Qmax) {
                        Reflection r;
                        r.h=h;
                        r.k=k;
                        r.l=l;
                        r.hklSqSum=h*h+k*k+l*l;
                        r.Q=Q;
                        r.d = 0.5/Q;
                        for (unsigned int i=1; i<int(2.0*Qmax*r.d+0.9); i++) {
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
    if (not updateEnabled)
        return;
    #ifdef __DEBUG__
    cout << "Update Reflextions" << endl;
    #endif
    for (unsigned int i=reflections.size(); i--; ) {
        Reflection &r = reflections[i];
        r.normal=MRot*r.normalLocal;
        r.lowestDiffOrder=0;
        r.highestDiffOrder=0;

        // sin(theta) = v*e_x = v.x
        // x direction points toward source, z points upwards
        if (r.normal.x()>0.0) {
            //Q=0.5/d/sin(theta)=r.Q/sin(theta)
            r.Qscatter = r.Q/r.normal.x();
            // Loop over higher orders
    
            unsigned int j=0;
            while (j<r.orders.size() && r.orders[j]*r.Qscatter<Qmin) j++;
            if (j<r.orders.size() && r.orders[j]*r.Qscatter>=Qmin) r.lowestDiffOrder=r.orders[j];
            while (j<r.orders.size() && r.orders[j]*r.Qscatter<=Qmax) {
                r.highestDiffOrder=r.orders[j];
                j++;
            }
        }    
        if (r.lowestDiffOrder!=0) 
            r.scatteredRay = Projector::normal2scattered(r.normal);
        else
            r.scatteredRay = Vec3D();
    }
}


unsigned int Crystal::reflectionCount() {
    QList<Reflection> r = getReflectionList();
    return r.size();
}

Reflection Crystal::getReflection(unsigned int i) {
    QList<Reflection> r = getReflectionList();
    if (i<r.size()) {
        return r[i];
    } else {
        return Reflection();
    }
}

Reflection Crystal::getClosestReflection(const Vec3D& normal) {
    QList<Reflection> r = getReflectionList();
    int minIdx=-1;
    double minDist=0;
    for (unsigned int n=r.size(); n--; ) {
        double dist=(r[n].normal-normal).norm_sq();
        if (dist<minDist or minIdx<0) {
            minDist=dist;
            minIdx=n;
        }
    }
    if (minIdx>=0) {
        return r[minIdx];
    } else {
        return Reflection();
    }
}


QList<Reflection> Crystal::getReflectionList() {
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


Mat3D Crystal::getRealOrientationMatrix() const {
    return MReal;
}

Mat3D Crystal::getReziprocalOrientationMatrix() const {
    return MReziprocal;
}

Mat3D Crystal::getRotationMatrix() const {
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

QList<Projector*> Crystal::getConnectedProjectors() {
    QList<Projector*> r;
    for (unsigned int i=0; i<connectedProjectors.size(); i++)
        r << dynamic_cast<Projector*>(connectedProjectors.at(i));
    return r;
}

QString Crystal::getSpacegroupSymbol() const {
    return spacegroupSymbol;
}

void Crystal::setSpacegroupSymbol(const QString& s) {
    spacegroupSymbol=s;
}

void Crystal::setRotationAxis(const Vec3D& axis, RotationAxisType type) {
    if ((axis!=rotationAxis) or (axisType!=type)) {
        rotationAxis=axis;
        axisType=type;
        emit rotationAxisChanged();
    }
}

Vec3D Crystal::getRotationAxis() const {
    return rotationAxis;
}

Vec3D Crystal::getLabSystamRotationAxis() const {
    if (axisType==ReziprocalSpace) {
        Vec3D v(MRot*MReziprocal*rotationAxis);
        v.normalize();
        return v;
    } else if (axisType==DirectSpace) {
        Vec3D v(MRot*MReal*rotationAxis);
        v.normalize();
        return v;
    }
    return rotationAxis.normalized();
}

Crystal::RotationAxisType Crystal::getRotationAxisType() const {
    return axisType;
}

QList<double> Crystal::getCell() {
    QList<double> cell;
    cell << a << b << c << alpha << beta << gamma;
    return cell;
}

void Crystal::enableUpdate(bool b) {
    updateEnabled=b;
}

void Crystal::setSpacegroupConstrains(QList<int> constrains) {
    spacegroupConstrains=constrains;
    QList<QString> fitParameterTempNames;
    fitParameterTempNames << "b" << "c" << "alpha" << "beta" << "gamma";
    QList<QString> fitParameterNames;
    for (unsigned int n=1; n<constrains.size(); n++) {
        if (constrains[n]==0)
            fitParameterNames << fitParameterTempNames[n-1];
    }    
    setFitParameterNames(fitParameterNames);
}

QList<int> Crystal::getSpacegroupConstrains() const {
    return spacegroupConstrains;
}
