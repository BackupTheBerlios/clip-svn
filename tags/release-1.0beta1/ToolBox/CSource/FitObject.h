#ifndef __FITOBJECT_H__
#define __FITOBJECT_H__

#include <QtCore/QList>
#include <QtCore/QPair>
#include <cmath>


class FitObject {
    public:
        FitObject();
        virtual ~FitObject();
        
        void setFitParameterNames(QList<QString> names);
        
        virtual unsigned int fitParameterNumber();
        virtual QString fitParameterName(unsigned int n);
        virtual double fitParameterValue(unsigned int n);
        virtual void fitParameterSetValue(unsigned int n, double val);
        virtual QPair<double, double> fitParameterBounds(unsigned int n);
        virtual double fitParameterChangeHint(unsigned int n);
        virtual bool fitParameterEnabled(unsigned int n);
        virtual void fitParameterSetEnabled(unsigned int n, bool enable);
        
    protected:
        struct FitParameter {
            QString name;
            bool enabled;
            QPair<double, double> bounds;
            double changeHint;
        };
        
        QList<FitObject::FitParameter> fitParameter;
};

#endif
