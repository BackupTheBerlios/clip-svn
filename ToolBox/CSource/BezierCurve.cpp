#include <BezierCurve.h>
#include <iostream>
#include <cmath>

using namespace std;

BezierCurve::BezierCurve(): params() {
    QList<QPointF> p;
    p.append(QPointF(0,0));
    p.append(QPointF(1,1));
    setPoints(p);
};

bool BezierCurve::setPoints(QList<QPointF>& p) {
    points=p;
    // this ist stolen from GIMP. Hale the GPL!!!
    // File: GIMP/app/base/curves.c
    params.clear();
    if (p.size()<2) {
        return false;
    } else if (p.size()==2) {
        CurveParams cp;
        cp.Xmin=-INFINITY;
        cp.Xmax=INFINITY;
        double dx=p.at(1).x()-p.at(0).x();
        if (dx==0.0)
            return false;
        double slope=(p.at(1).y()-p.at(0).y())/dx;
        cp.D0=p.at(0).y()-slope*p.at(0).x();
        cp.D1=slope;
        cp.D2=0.0;
        cp.D3=0.0;
        params.append(cp);
    } else {
        for (unsigned int i=p.size()-1; i--; ) {
            double p0=p.at(i).y();
            double p3=p.at(i+1).y();
            double p1;
            double p2;
            double dx=p.at(i+1).x()-p.at(i).x();
            if (dx==0.0)
                continue;
            
            if (i==0) {
                //only the right neighbor is available. Make the tangent at the
                //right endpoint parallel to the line between the left endpoint
                //and the right neighbor. Then point the tangent at the left towards
                //the control handle of the right tangent, to ensure that the curve
                //does not have an inflection point.
                double slope = (p.at(i+2).y() - p.at(i).y()) / (p.at(i+2).x() - p.at(i).x());
                p2 = p.at(i+1).y() - slope * dx / 3.0;
                p1 = p.at(i).y() + (p2 - p.at(i).y()) / 2.0;
            } else if (i==p.size()-2) {
                double slope = (p.at(i+1).y() - p.at(i-1).y()) / (p.at(i+1).x() - p.at(i-1).x());
                p1 = p.at(i).y() + slope * dx / 3.0;
                p2 = p.at(i+1).y() + (p1 - p.at(i+1).y()) / 2.0;
            } else {
                // Both neighbors are available. Make the tangents at the endpoints
                // parallel to the line between the opposite endpoint and the adjacent
                //neighbor.               
                double slope = (p.at(i+1).y() - p.at(i-1).y()) / (p.at(i+1).x() - p.at(i-1).x());
                p1 = p.at(i).y() + slope * dx / 3.0;
                slope = (p.at(i+2).y() - p.at(i).y()) / (p.at(i+2).x() - p.at(i).x());
                p2 = p.at(i+1).y() - slope * dx / 3.0;
            }
            double C0=p0;
            double C1=(        3*p1-3*p0)/dx;
            double C2=(   3*p2-6*p1+3*p0)/dx/dx;
            double C3=(p3-3*p2+3*p1-  p0)/dx/dx/dx;
            
            double x=p.at(i).x();
            CurveParams cp;
            
            cp.D0 = ((-C3*x +C2)*x-C1)*x+C0;
            cp.D1 = (3.0*C3*x -2.0*C2)*x+C1;
            cp.D2=C2 - 3.0*C3*x;
            cp.D3=C3;
            cp.Xmin=p.at(i).x();
            cp.Xmax=p.at(i+1).x();
            
            
            params.prepend(cp);
        }
        params.first().Xmin=-INFINITY;
        params.last().Xmax=INFINITY;
        return not params.empty();
    }
    return true;
}

QList<QPointF> BezierCurve::getPoints() {
    return points;
}

double BezierCurve::CurveParams::calc(double x) {
    return qMax(0.0, qMin(1.0, ((D3*x+D2)*x+D1)*x+D0));
}

double BezierCurve::operator()(double x) {
    if (params.empty())
        return 0.0;
    
    unsigned int p=getCurveParamIdx(x);
    return params[p].calc(x);
}

double BezierCurve::operator()(double x, unsigned int& hint) {
    while (params[hint].Xmax<x) hint++;
    while (params[hint].Xmin>x) hint--;
    return params[hint].calc(x);
}


QList<double> BezierCurve::range(double x0, double dx, unsigned int N) {
    QList<double> r;
    double x=x0;
    unsigned int p=getCurveParamIdx(x);
    unsigned int n=N;
    while (n) {
        CurveParams& cp=params[p];
        while (n && (x<cp.Xmax)) {
            r.append(cp.calc(x));
            x+=dx;
            n--;
        }
        p++;
    }
    return r;
}

QList<QPointF> BezierCurve::pointRange(double x0, double dx, unsigned int N) {
    QList<QPointF> r;
    double x=x0;
    unsigned int p=getCurveParamIdx(x);
    unsigned int n=N;
    while (n) {
        CurveParams& cp=params[p];
        while (n && (x<cp.Xmax)) {
            r.append(QPointF(x,cp.calc(x)));
            x+=dx;
            n--;
        }
        p++;
    }
    return r;
}


QList<double> BezierCurve::map(QList<double> X) {
    QList<double> r;
    for (unsigned int n=X.size(); n--; ) {
        double x=X[n];
        unsigned int p=getCurveParamIdx(x);
        r.prepend(params[p].calc(x));
    }
    return r;
}

QList<double> BezierCurve::mapSorted(QList<double> X) {
    QList<double> r;
    unsigned int p=getCurveParamIdx(X[0]);
    unsigned int n=X.size();
    while (n) {
        CurveParams& cp=params[p];
        double x;
        while (n && ((x=X[n-1])<cp.Xmax)) {
            r.prepend(cp.calc(x));
            n--;
        }
        p++;
    }
    return r;
}

QList<double> BezierCurve::mapSorted(QList<double> X, QList<unsigned int> Idx) {
    QList<double> r(X);
    unsigned int p=getCurveParamIdx(X[Idx[0]]);
    unsigned int n=X.size();
    while (n) {
        CurveParams& cp=params[p];
        double x;
        unsigned int idx=Idx[n-1];
        while (n && ((x=X[idx])<cp.Xmax)) {
            r[idx]=cp.calc(x);
            n--;
        }
        p++;
    }
    return r;
    
}

unsigned int BezierCurve::getCurveParamIdx(double x) {
    CurveParams cp;
    cp.Xmax=x;
    QList<CurveParams>::const_iterator iter=qLowerBound(params.constBegin(), params.constEnd(), cp);
    if (iter==params.constEnd())
        iter--;
    //cout << "iterpos " << iter-params.constBegin() << endl;
    return qMax(0,iter-params.constBegin());    
}

BezierCurve::CurveParams BezierCurve::getCurveParam(double x) {
    //cout << "get Curve Param for " << x << endl;
    unsigned int p=getCurveParamIdx(x);
    //cout << "is Param " << p << "/" << params.size() << endl;
    return params[p];
}


