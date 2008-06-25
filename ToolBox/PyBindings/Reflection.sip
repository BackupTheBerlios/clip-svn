
class  Reflection {
%TypeHeaderCode
#include <reflection.h>
%End
    public:

        // Index
        int h;
        int k;
        int l;
        
        int hklSqSum;
        // lowest order
        int lowestDiffOrder;
        
        // direct space d-Value
        double d;
        // Reziplocl length
        double Q;
        // Order 1 scattering Wavevectors (Q/2/sin(theta)/2/pi)
        double Qscatter;

        // All contributing orders
        QList<int> orders;
        // Real and imaginary part of Structure factor
        //vector<double> Fr;
        //vector<double> Fi;
        
        // reziprocal direction (without rotations)
        Vec3D normalLocal;
        
        // reziprocal direction (with rotations)
        Vec3D normal;

        // Direction of scattered ray
        Vec3D scatteredRay;
};
