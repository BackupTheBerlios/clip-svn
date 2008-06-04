
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

  bool setCell(double a, double b, double c, double alpha, double beta, double gammaa);

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

  bool setWavelengthBoundarys(double lower, double upper);

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
  string sg;
  double a,b,c,alpha,beta,gamma;
  double upperLambda;
  double lowerLambda;
  double invUpperLambda;
  double invLowerLambda;

};
