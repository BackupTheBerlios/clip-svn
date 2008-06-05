class Crystal: QObject {

%TypeHeaderCode
#include <crystal.h>
%End
    public:

        Crystal();
        Crystal(const Crystal &);
        ~Crystal();

        void setCell(double a, double b, double c, double alpha, double beta, double gammaa);

        void generateReflections();

        void addRotation(const Vec3D& axis, double angle);
        void setRotation(const Mat3D& M);

        unsigned int reflectionCount();
        Reflection getReflection(unsigned int i);
        std::vector<Reflection>& getReflectionList();

        Vec3D uvw2Real(const Vec3D&);
        Vec3D hkl2Reziprocal(const Vec3D&);

        Mat3D getRealOrientationMatrix();
        Mat3D getReziprocalOrientationMatrix();
        Mat3D getRotationMatrix();

        void setWavelengthBoundarys(double lower, double upper);

};
