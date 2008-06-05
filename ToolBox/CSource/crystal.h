#ifndef __crystal_h__
#define __crystal_h__

#include <QtCore/QObject>
#include "vec3D.h"
#include "mat3D.h"
#include "reflection.h"



class Crystal: public QObject {
    Q_OBJECT 
    public:

        Crystal();
        Crystal(const Crystal &);
        ~Crystal();


        void generateReflections();


        unsigned int reflectionCount();
        Reflection getReflection(unsigned int i);
        std::vector<Reflection>& getReflectionList();

        Vec3D uvw2Real(const Vec3D&);
        Vec3D uvw2Real(int u, int v, int w);
        Vec3D hkl2Reziprocal(const Vec3D&);
        Vec3D hkl2Reziprocal(int h, int k, int l);

        Mat3D getRealOrientationMatrix();
        Mat3D getReziprocalOrientationMatrix();
        Mat3D getRotationMatrix();

    public slots:
        void addRotation(const Vec3D& axis, double angle);
        void setRotation(const Mat3D& M);
        void setCell(double a, double b, double c, double alpha, double beta, double gamma);
        void setWavelengthBoundarys(double lower, double upper);


    signals:
        void cellChanged();
        void orientationChanged();
        void reflectionsUpdate();
    
    private:
        // Real and reziprocal orientation Matrix
        Mat3D MReal;
        Mat3D MReziprocal;

        // Rotation Matrix
        Mat3D MRot;

        // Reziprocal lattice vectors
        Vec3D astar;
        Vec3D bstar;
        Vec3D cstar;

        vector<Reflection> reflections;
        double a,b,c,alpha,beta,gamma;
        double upperLambda;
        double lowerLambda;
};


#endif
