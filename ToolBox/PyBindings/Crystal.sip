class Crystal: QObject {

%TypeHeaderCode
#include <crystal.h>
%End
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


        unsigned int reflectionCount();
        Reflection getReflection(unsigned int i);
        Reflection getClosestReflection(const Vec3D& normal);
        QList<Reflection>getReflectionList();

        Vec3D uvw2Real(const Vec3D&);
        Vec3D uvw2Real(int u, int v, int w);
        Vec3D hkl2Reziprocal(const Vec3D&);
        Vec3D hkl2Reziprocal(int h, int k, int l);

        Mat3D getRealOrientationMatrix();
        Mat3D getReziprocalOrientationMatrix();
        Mat3D getRotationMatrix();
        QList<Projector*> getConnectedProjectors();
        QString getSpacegroupSymbol();
        
        Vec3D getRotationAxis();
        Vec3D getLabSystamRotationAxis();
        RotationAxisType getRotationAxisType();
        
    public slots:
        void addRotation(const Vec3D& axis, double angle);
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        void setCell(double a, double b, double c, double alpha, double beta, double gamma);
        void setWavevectors(double lower, double upper);
        void addProjector(Projector*);
        void updateWavevectorsFromProjectors();
        void setSpacegroupSymbol(const QString& s);
        void setRotationAxis(const Vec3D& axis, RotationAxisType type=LabSystem);

    signals:
        void cellChanged();
        void orientationChanged();
        void reflectionsUpdate();
        void rotationAxisChanged();

};
