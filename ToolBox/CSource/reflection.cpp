

Crystal::Crystal();
Crystal::Crystal(Crystal &);

bool Crystal::setSG(string name);
bool Crystal::setCell(double a, double b, double c, double alpha, double beta, double gappa);

  void generateReflections();

  void addRotation(Vec3D angle, double angle);
  void setRotation(Mat3D M);

  unsigned int reflexCount();
  Reflection getReflection(unsigned int i);
  std::vector<Reflection>& getReflectionList();

  Vec3D reduced2Real(Vec3D);
  Vec3D reduced2Reziprocal(Vec3D);
  Vec3D real2reduced(Vec3D);
  Vec3D reziprocal2reduced(Vec3D);

  Mat3D getRealOrientationMatrix();
  Mat3D getReziprocalOrientationMatrix();
  Mat3D getRotationMatrix();


 private:
  Mat3D MReal;
  Mat3D MReziprocal;
  Mat3D MRot;

  vector<Reflex> reflections;
  string sg;
  double a,b,c,alpha,beta,gamma;
};
