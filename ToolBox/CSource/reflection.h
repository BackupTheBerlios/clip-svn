
class  Reflection {
 public:

  // Index
  int h;
  int k;
  int l;
  
  // lowest order
  int lowestDiffOrder;

  // direct space d-Value
  double d;

  // All contributin orders
  vector<int> orders;
  // Real and imaginary part of Structure factor
  vector<double> Fr;
  vector<double> Fi;
  
  // reziprocal direction (with rotations)
  Vec3D normal;

  // Direction of scattered ray
  Vec3D scatteredRay;
  
  double projX;
  double projY;
  
};
