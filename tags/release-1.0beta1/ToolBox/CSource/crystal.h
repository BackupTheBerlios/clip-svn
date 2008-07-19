#ifndef __CRYSTAL_H__
#define __CRYSTAL_H__

#include <QtCore/QObject>
#include <vec3D.h>
#include <mat3D.h>
#include <ObjectStore.h>
#include <reflection.h>
#include <FitObject.h>


class Projector;

class Crystal: public QObject, public FitObject {
    Q_OBJECT 
    public:
        enum RotationAxisType {
            LabSystem,
            ReziprocalSpace,
            DirectSpace
        };

        Crystal();
        Crystal(const Crystal &);
        ~Crystal();

        void generateReflections();
        void updateRotation();
        unsigned int reflectionCount();
        Reflection getReflection(unsigned int i);
        Reflection getClosestReflection(const Vec3D& normal);
        QList<Reflection> getReflectionList();

        Vec3D uvw2Real(const Vec3D&);
        Vec3D uvw2Real(int u, int v, int w);
        Vec3D hkl2Reziprocal(const Vec3D&);
        Vec3D hkl2Reziprocal(int h, int k, int l);

        Mat3D getRealOrientationMatrix() const;
        Mat3D getReziprocalOrientationMatrix() const;
        Mat3D getRotationMatrix() const;
        QString getSpacegroupSymbol() const;
        QList<int> getSpacegroupConstrains() const;
        
        Vec3D getRotationAxis() const;
        Vec3D getLabSystamRotationAxis() const;
        RotationAxisType getRotationAxisType() const;

        QList<Projector*> getConnectedProjectors();
        
        QList<double> getCell();
        void enableUpdate(bool b=true);
    public slots:
        void addRotation(const Vec3D& axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        void setCell(double a, double b, double c, double alpha, double beta, double gamma);
        void setWavevectors(double Qmin, double Qmax);
        void addProjector(Projector*);
        void updateWavevectorsFromProjectors();
        void setSpacegroupSymbol(const QString& s);
        void setSpacegroupConstrains(QList<int> constrains);
        void setRotationAxis(const Vec3D& axis, RotationAxisType type=LabSystem);
        
    signals:
        void cellChanged();
        void orientationChanged();
        void reflectionsUpdate();
        void rotationAxisChanged();
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

        QList<Reflection> reflections;
        double a,b,c,alpha,beta,gamma;
        double Qmin;
        double Qmax;
        ObjectStore connectedProjectors;
        QString spacegroupSymbol;
        QList<int> spacegroupConstrains;
        
        Vec3D rotationAxis;
        RotationAxisType axisType;
        
        bool updateEnabled;
};


#endif
