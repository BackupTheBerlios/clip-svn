#ifndef __BEZIERCURVE_H__
#define __BEZIERCURVE_H__

#include <QtCore/QPointF>
#include <QtCore/QList>

#define MIN(x,y) (((x)<(y))?(x):(y))
#define MAX(x,y) (((x)>(y))?(x):(y))

class BezierCurve {
    public:
        BezierCurve();
        bool setPoints(QList<QPointF> &p);
        QList<QPointF> getPoints();
    
        float operator()(float x);
        float operator()(float x, unsigned int& hint);
            
        QList<float> range(float x0, float dx, unsigned int N);
        QList<QPointF> pointRange(float x0, float dx, unsigned int N);
        QList<float> map(QList<float> X);
        QList<float> mapSorted(QList<float> X);
        QList<float> mapSorted(QList<float> X, QList<unsigned int> sortIdx);
    private:
        struct CurveParams{
            float Xmin;
            float Xmax;
            float D0;
            float D1;
            float D2;
            float D3;
            bool operator<(const CurveParams& c) const {return Xmax<c.Xmax; };
            float calc(float x)   {
                return MAX(0.0, MIN(1.0, ((D3*x+D2)*x+D1)*x+D0));
            }
        };
        CurveParams getCurveParam(float x);

        unsigned int getCurveParamIdx(float x);
        QList<CurveParams> params;
        QList<QPointF> points;
};


#endif

