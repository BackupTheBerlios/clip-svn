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





Diffract::Diffract(): boxSize(2, 1.0), cell(6, 0.0), M_real(), M_rezi(), rot(), M_proj(), V_proj(), reflexe(), scatteringRef(), projectedRef(), projectedCoords(), reflexCond() {
  //sg = NULL;
  projectionType = Plane;
}

Diffract::~Diffract() {
}

unsigned int Diffract::reflexCount() {
  if (reflexe.size()==0)
    generateReflex();
  return reflexe.size();
}

Reflex Diffract::getReflex(unsigned int i) {
  if (i<reflexCount()) {
    return reflexe[i];
  } else {
    return Reflex();
  }
}

unsigned int Diffract::scatteringReflexCount() {
  if (scatteringRef.size()==0)
    generateScatteredRayDirections();
  return scatteringRef.size();
}

Reflex Diffract::getScatteringReflex(unsigned int i) {
  if (i<scatteringReflexCount()) {
    return reflexe[scatteringRef[i]];
  } else {
    return Reflex();
  }
}

unsigned int Diffract::projectedReflexCount() {
  if (projectedRef.size()==0)
    calcProjection();
  return projectedRef.size();
}

Reflex Diffract::getProjectedReflex(unsigned int i) {
  if (i<projectedReflexCount()) {
    return reflexe[projectedRef[i]];
  } else {
    return Reflex();
  }
}

vector<double> Diffract::getProjectedCoord(unsigned int i) {
  unsigned int s=projectedCoords.size();
  if (s==0) {
    calcProjection();
    s=projectedCoords.size();
  }
  if (i<s) 
    return projectedCoords[i];
  vector<double> r(2,0.0);
  return r;
}

vector<vector<double> > Diffract::getCoord() {
  if (projectedCoords.size()==0)
    calcProjection();
  return projectedCoords;
}

bool Diffract::setSym(string s, vector<double> uc) {
  if (uc.size()!=6) return false;
  cell = uc;
  try {
    	/*
	if (sg)
      	delete sg;
    	sg = new cctbx::sgtbx::space_group(cctbx::sgtbx::space_group_symbols(s));
	*/	
  }
  catch (...) {
    cout << "exception" << endl;
    //delete sg;
    //sg=NULL;
    return false;
  }


  // Cosini und Sini der Winkel zwischen den Gittervektoren
  double Ca=cos(M_PI/180.0*cell[3]);
  double Cb=cos(M_PI/180.0*cell[4]);
  double Cc=cos(M_PI/180.0*cell[5]);
  double Sc=sin(M_PI/180.0*cell[5]);

  // Volumen der Einheitszelle im realen und reziproken Raum
  double Vreal=cell[0]*cell[1]*cell[2]*sqrt(1.0+2.0*Ca*Cb*Cc-Ca*Ca-Cb*Cb-Cc*Cc);
  double Vrezi=1.0/Vreal;
   
  // Realraum Gittervektoren, a zeigt in x-Richtung, b liegt in der xy-Ebene, c ist dann festgelegt.
  // a,b,c sind die Kristallachse, x,y,z bezeichnen ein orthonormalsystem
  Vec3D a_real(cell[0], 0, 0);
  Vec3D b_real(Cc*cell[1], Sc*cell[1], 0);
  Vec3D c_real(Cb, (Ca-Cb*Cc)/Sc, sqrt(1.0-Cb*Cb-(Ca-Cb*Cc)/Sc*(Ca-Cb*Cc)/Sc));
  c_real *= cell[2];
  
  M_real=Mat3D(a_real, b_real, c_real);

  // Reziproke Gittervektoren als Kreuzprodukte. Nach der Wahl der Realraum Gittervektoren
  // liegt c* entlang der z-Achse, b* in der yz-Ebene und a* ist durch diese Wahl wieder festgelegt. insbesondere ist 
  // c* = (0,0,1/c) !!!

  
  M_rezi = Mat3D(b_real%c_real, c_real%a_real, a_real%b_real);
  M_rezi*=Vrezi;

  reflexe.clear();
  scatteringRef.clear();
  projectedRef.clear();
  projectedCoords.clear();
  return true;
}

bool Diffract::setReflexConditions(vector<ReflexCondition> rc) {
  reflexCond=rc;
  return true;
}
    
void Diffract::setProjection(ProjectionType type, Mat3D localCoord, Vec3D v) {
  projectionType = type;
  M_proj = localCoord;
  V_proj = v;
  projectedRef.clear();
  projectedCoords.clear();
}

void Diffract::addRotation(Vec3D axis, double angle) {
  rot = Mat3D(axis, angle)*rot;
  scatteringRef.clear();
  projectedRef.clear();
  projectedCoords.clear();
}

void Diffract::setRotation(Mat3D M) {
  rot = M;
  scatteringRef.clear();
  projectedRef.clear();
  projectedCoords.clear();
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

// Rechnet aus den Richtungen der gestreuten Strahlen die
// Position auf dem Detector
void Diffract::calcProjection() {
  projectedRef.clear();
  projectedCoords.clear();
  Vec3D ex = M_proj[0];
  Vec3D ey = M_proj[1];
  Vec3D n = M_proj[2];
  if (projectionType==Plane) {

    // M_proj ist lokales orthogonales Koordinatensystem
    // 0 und 1 liegen in der Detektorebene, 2 ist die Detektornormale
    // 
    // V_proj.x und y sind die Verschiebungen entlang der lokalen Koordinatenachsen
    // V_proj.z ist der minimale Abstand der Ebene vom Ursprung
    
      
    for (unsigned int i=0; i<scatteringReflexCount(); i++) {
      unsigned int j = scatteringRef[i];
      Vec3D r=reflexe[j].scatteredRay;
      //r.normalize();
      double c = r*n;
      if (c>0) {
	//r=(r/c-n)*V_proj.z();
	r=r*V_proj.z()/c;
	double x = r*ex-V_proj.x();
	double y = r*ey-V_proj.y();
	
	reflexe[j].projX = x;
	reflexe[j].projY = y;
	projectedRef.push_back(j);
	vector<double> coord(2,0.0);
	coord[0] = x;
	coord[1] = y;
	projectedCoords.push_back(coord);
      }
    }
  } else if (projectionType==Cylinder) {
    // M_proj ist lokales orthogonales Koordinatensystem
    // 2 ist die Zylinderachse, 0 und 1 sind senkrecht dazu
    // 
    // V_proj.x und y sind die Verschiebungen der Zylinderachse entlang der lokalen Koordinatenachsen
    // V_proj.z ist der Zylinderradius

    Vec3D offset = ex*V_proj.x()+ey*V_proj.y();

    for (unsigned int i=0; i<scatteringRef.size(); i++) {
      unsigned int j = scatteringRef[i];
      Vec3D v=reflexe[j].scatteredRay;
      Vec3D v_perp=v-n*(n*v);
      double n2vp=v_perp.norm_sq();
      
      if (n2vp>0.0) {
	
	double lambda = (v_perp*offset)/n2vp;
	lambda = sqrt(lambda*lambda+(V_proj.z()*V_proj.z()-offset.norm_sq())/n2vp)-lambda;
	v=v*lambda+offset;
	double x = 2.0*V_proj.z()*atan2(v*ex, v*ey);
	double y = v*n;
	reflexe[j].projX = x;
	reflexe[j].projY = y;
	projectedRef.push_back(j);
	vector<double> coord(2,0.0);
	coord[0] = x;
	coord[1] = y;
	projectedCoords.push_back(coord);
      }
    }
  }
}

vector<double> Diffract::rSpace2Det(Vec3D v) {
  vector<double> coord(0);
  if (v.z()>0) {
    v = Vec3D(2.0*v.x()*v.z(), 2.0*v.y()*v.z(), v.z()*v.z()-v.x()*v.x()-v.y()*v.y());
    Vec3D ex = M_proj[0];
    Vec3D ey = M_proj[1];
    Vec3D n = M_proj[2];
    if (projectionType==Plane) {
      double c = v*n;
      if (c>0) {
	v=v*V_proj.z()/c;
	coord.push_back(v*ex-V_proj.x());
	coord.push_back(v*ey-V_proj.y());
      }
    } else if (projectionType==Cylinder) {
      Vec3D v_perp=v-n*(n*v);
      double n2vp=v_perp.norm_sq();
      Vec3D offset = ex*v.x()+ey*v.y();

      if (n2vp>0.0) {
	
	double lambda = (v_perp*offset)/n2vp;
	lambda = sqrt(lambda*lambda+(v.z()*v.z()-offset.norm_sq())/n2vp)-lambda;
	v=v*lambda+offset;
	
	coord.push_back(2.0*V_proj.z()*atan2(v*ex, v*ey));
	coord.push_back(v*n);
      }
    }
  }
  return coord;
}

Vec3D Diffract::det2RSpace(vector<double> p) {
  Vec3D r(0.0,0.0,0.0);
  Vec3D ex = M_proj[0];
  Vec3D ey = M_proj[1];
  Vec3D n = M_proj[2];
  Vec3D tmp;
  if (projectionType==Plane) {
    tmp=ex*(p[0]+V_proj.x())+ey*(p[1]+V_proj.y())+n*V_proj.z();
  }
  //    z'=z^2-x^2-y^2
  // norm'=z^2+x^2+y^2
  // z'+norm' = 2z^2
  double z = tmp.z()+tmp.norm();
  if (z>0.0) {
    z=sqrt(0.5*z);
    r=Vec3D(0.5*tmp.x()/z, 0.5*tmp.y()/z, z);
    r.normalize();
  }
  return r;
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
