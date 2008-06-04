#include <iostream>
#include <iomanip>
#include "diffract.h"
#include <cmath>
//#include <cctbx/sgtbx/symbols.h>



int ggt(int a, int b) {
  while (b) {
    int tb=b;
    b=a%b;
    a=tb;
  }
  return abs(a);
}





Diffract::Diffract(): cell(6, 0.0), Mreal(), Mrezi(), rot(), reflections(), scatteredIdx(), reflexCond() {
}

Diffract::~Diffract() {
}

unsigned int Diffract::reflectionsCount() {
  if (reflections.size()==0)
    generateReflections();
  return reflections.size();
}

Reflex Diffract::getReflex(unsigned int i) {
  if (i<reflexCount()) {
    return reflections[i];
  } else {
    return Reflex();
  }
}

unsigned int Diffract::scatteringReflexCount() {
  if (scatteredIdx.size()==0)
    generateScatteredRayDirections();
  return scatteredIdx.size();
}

Reflex Diffract::getScatteredReflex(unsigned int i) {
  if (i<scatteredReflexCount()) {
    return reflections[scatteredIdx[i]];
  } else {
    return Reflex();
  }
}

bool Diffract::setCell(vector<double> uc) {
  if (uc.size()!=6) return false;
  cell = uc;

  // Cosini und Sini of angles between lattice vectors
  double Ca=cos(M_PI/180.0*cell[3]);
  double Cb=cos(M_PI/180.0*cell[4]);
  double Cc=cos(M_PI/180.0*cell[5]);
  double Sc=sin(M_PI/180.0*cell[5]);

  // Volume of real and reciprocal space unit cell
  double Vreal=cell[0]*cell[1]*cell[2]*sqrt(1.0+2.0*Ca*Cb*Cc-Ca*Ca-Cb*Cb-Cc*Cc);
  double Vrezi=1.0/Vreal;
   
  // Coordinate system: 
  //      a points towards x
  //      b lies in xy plane
  //      c completes the right handed system
  Vec3D a_real(cell[0], 0, 0);
  Vec3D b_real(Cc*cell[1], Sc*cell[1], 0);
  Vec3D c_real(Cb, (Ca-Cb*Cc)/Sc, sqrt(1.0-Cb*Cb-(Ca-Cb*Cc)/Sc*(Ca-Cb*Cc)/Sc));
  c_real *= cell[2];
  
  Mreal=Mat3D(a_real, b_real, c_real);

  // This gives for the reziprocal space unit vectors:
  //      c* is along the z direction
  //      b* lies in the yz plane
  //      a* again completes the right handed system

  
  Mrezi = Mreal.inverse()

  reflections.clear();
  scatteringRef.clear();
  return true;
}

bool Diffract::setReflexConditions(vector<ReflexCondition> rc) {
  reflexCond=rc;
  return true;
}
    

void Diffract::addRotation(Vec3D axis, double angle) {
  rot = Mat3D(axis, angle)*rot;
  reflections.clear();
  scatteringRef.clear();
}

void Diffract::setRotation(Mat3D M) {
  rot = M;
  reflections.clear();
  scatteredIdx.clear();
}

void Diffract::generateReflex() {
  // Groesse der Ewaldkugel 
  double dMin = 0.5;
  double dMinInv=1.0/dMin;

  // Maximale hkl die in die Ewaldkugel noch passen k�nen
  int h_max = int(dMinInv/M_rezi[0].norm()+0.9);
  int k_max = int(dMinInv/M_rezi[1].norm()+0.9);
  int l_max = int(dMinInv/M_rezi[2].norm()+0.9);

  //cout << "hkl_max:   " << h_max << "  " << k_max << " " << l_max << endl;
  reflexe.clear();
  for (int h=-h_max; h<=h_max; h++) {
    for (int k=-k_max; k<=k_max; k++) {
      for (int l=-l_max; l<=l_max; l++) {
	// Aequivalente Richtungen werden zusmmengefasst [1 0 0] = [2 0 0]
	if (ggt(h,ggt(k,l))==1) {
	  Vec3D v(h,k,l);
	  v=M_rezi*v;
	  double d = 1.0/v.norm();

	  Reflex r;
	  // Loop ber alle m�lichen vielfachen (lambda/2) 
	  int n_max = int(d/dMin+0.9);
	  //cout << "[" << h << "," << k << ","  << l << "] " <<  n_max << "," << d << endl;
	  for (int n=1; n<=n_max; n++) {
            bool valid=true;
            for (unsigned int c=reflexCond.size(); c--; ) {
              ReflexCondition rc=reflexCond[c];
              if ((!rc.hZero || h==0) && (!rc.hZero || h==0) && (!rc.hZero || h==0)) {
                int sum = n*(h*rc.h+k*rc.k+l*rc.l);
                if ((sum%rc.modulo)!=0)
                  valid=false;
              }
            }
                
	    //if (!sg || !sg->is_sys_absent(cctbx::miller::index<int>(n*h,n*k,n*l))) {
            if (valid)
	      r.orders.push_back(n);
            //}
	  }
	  if (!r.orders.empty()) {
	    r.h=h;
	    r.k=k;
	    r.l=l;
	    r.d = d;
	    r.normal = Vec3D(h,k,l);
	    r.normal = M_rezi*r.normal;
	    r.normal.normalize();
	    r.lowestDiffOrder=0;
	    reflexe.push_back(r);
          }
        }
      } 
    }
  }
}

// Berechnet aus den Reflex-Normalen und der Orientierung zum Strahl 
// die Richtungen der gestreuten Strahlen
void Diffract::generateScatteredRayDirections() {

  double dMin = 0.5;
  double dMax = 12.0;
  double dMin_inv = 1.0/dMin;
  double dMax_inv = 1.0/dMax;

  scatteringRef.clear();

  // M_rezi drehen
    for (unsigned int i=0; i<reflexCount(); i++) {
    Vec3D v(rot*reflexe[i].normal);
    if (v.z()>0) {
      // sin(theta) = v*e_z = v.z
      double tmp = reflexe[i].d*v.z();
      int nMin_sq = int (dMax_inv*tmp);
      int nMax_sq = int (dMin_inv*tmp+0.9);

      vector<int>::iterator end = reflexe[i].orders.end();
      for (vector<int>::iterator it=reflexe[i].orders.begin(); it!=end; it++) {
	if (*it>=nMin_sq and *it<=nMax_sq) {
	  reflexe[i].lowestDiffOrder=*it;
	  break;
	}
      }

      if (reflexe[i].lowestDiffOrder) {
	scatteringRef.push_back(i);
	reflexe[i].scatteredRay = Vec3D(2.0*v.x()*v.z(), 2.0*v.y()*v.z(), v.z()*v.z()-v.x()*v.x()-v.y()*v.y());
      }
    }
  }
}


Vec3D Diffract::reduced2Real(Vec3D v) {
  return rot*M_real*v;
}

Vec3D Diffract::reduced2Rezi(Vec3D v) {
  return rot*M_rezi*v;
}

Mat3D Diffract::getRealOrientationMatrix() {
  return M_real;
}

Mat3D Diffract::getReziprocalOrientationMatrix() {
  return M_rezi;
}

Mat3D Diffract::getRotationMatrix() {
  return rot;
}
