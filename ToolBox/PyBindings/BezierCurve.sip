class BezierCurve {
%TypeHeaderCode
    #include <BezierCurve.h>
%End
    public:
        BezierCurve();
        bool setPoints(QList<QPointF> &p);
        QList<QPointF> getPoints();
        double operator()(double x);
            
        QList<double> range(double x0, double dx, unsigned int N);
        QList<QPointF> pointRange(double x0, double dx, unsigned int N);
        QList<double> map(QList<double>& X);
        QList<double> mapSorted(QList<double>& X);
        
};
