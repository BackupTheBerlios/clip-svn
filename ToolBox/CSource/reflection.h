#ifndef __REFLECTION_H__
#define __REFLECTION_H__

#include <vector>
#include <mat3D.h>
#include <vec3D.h>

class  Reflection {
    public:

        // Index
        int h;
        int k;
        int l;
  
        // lowest order (if ==0, this reflection is not in scattering position)
        int lowestDiffOrder;

        // direct space d-Value
        double d;
            
        // Reziprocal lattice Vector = 2pi/d
        double Q;
            
        // Order 1 scattering Wavevectors (Q/2/sin(theta)/2/pi)
        double Qscatter;

        // All contributing orders
        std::vector<int> orders;
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

#endif
