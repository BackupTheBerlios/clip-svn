class Crystal: QObject {

%TypeHeaderCode
#include <crystal.h>
%End
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
        void addRotation(const Mat3D& M);
        void setRotation(const Mat3D& M);
        void setCell(double a, double b, double c, double alpha, double beta, double gamma);
        void setWavelengthBoundaries(double lower, double upper);
        void addProjector(Projector*);
        void updateWavelengthFromProjectors();
    signals:
        void cellChanged();
        void orientationChanged();
        void reflectionsUpdate();
};
