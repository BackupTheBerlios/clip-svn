class FitObject {
%TypeHeaderCode
#include <FitObject.h>
%End

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
};

// QPair<double, double> is implemented as a Python 2-element tuple.
%MappedType QPair<double, double>
{
%TypeHeaderCode
#include <qpair.h>
%End

%ConvertFromTypeCode
    // Create the tuple.
    return Py_BuildValue((char *)"dd", sipCpp->first, sipCpp->second);
%End

%ConvertToTypeCode
    // Check the type if that is all that is required.
    if (sipIsErr == NULL)
        return (PyTuple_Size(sipPy) == 2);

    QPair<double,double> *qp = new QPair<double,double>;

    qp->first = PyFloat_AsDouble(PyTuple_GET_ITEM(sipPy, 0));
    qp->second = PyFloat_AsDouble(PyTuple_GET_ITEM(sipPy, 1));

    *sipCppPtr = qp;

    return sipGetState(sipTransferObj);
%End
};
