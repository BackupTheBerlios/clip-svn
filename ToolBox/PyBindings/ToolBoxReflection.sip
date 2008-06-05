
class  Reflection {
%TypeHeaderCode
#include <reflection.h>
%End
    public:

        // Index
        int h;
        int k;
        int l;
  
        // lowest order
        int lowestDiffOrder;

        // direct space d-Value
        double d;

        // All contributing orders
        std::vector<int> orders;
        // Real and imaginary part of Structure factor
        //vector<double> Fr;
        //vector<double> Fi;
  
        // reziprocal direction (with rotations)
        Vec3D normal;

        // Direction of scattered ray
        Vec3D scatteredRay;
};
