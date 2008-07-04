#ifndef __BEZIERCURVE_H__
#define __BEZIERCURVE_H__

#include <QtCore/QPointF>
#include <QtCore/QList>

class BezierCurve {
    public:
        struct CurveParams{
            double Xmin;
            double Xmax;
            double D0;
            double D1;
            double D2;
            double D3;
            bool operator<(const CurveParams& c) const {return Xmax<c.Xmax; };
            double calc(double);
        };

        BezierCurve();
        bool setPoints(QList<QPointF> &p);
        QList<QPointF> getPoints();
    
        double operator()(double x);
        double operator()(double x, unsigned int& hint);
            
        QList<double> range(double x0, double dx, unsigned int N);
        QList<QPointF> pointRange(double x0, double dx, unsigned int N);
        QList<double> map(QList<double> X);
        QList<double> mapSorted(QList<double> X);
        QList<double> mapSorted(QList<double> X, QList<unsigned int> sortIdx);
        CurveParams getCurveParam(double x);
    private:
        unsigned int getCurveParamIdx(double x);
        QList<CurveParams> params;
        QList<QPointF> points;
};


#endif

