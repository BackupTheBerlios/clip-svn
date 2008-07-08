class BezierCurve {
%TypeHeaderCode
    #include <BezierCurve.h>
%End
    public:
        BezierCurve();
        bool setPoints(QList<QPointF> &p);
        QList<QPointF> getPoints();
        float operator()(float x);
            
        QList<float> range(float x0, float dx, unsigned int N);
        QList<QPointF> pointRange(float x0, float dx, unsigned int N);
        QList<float> map(QList<float>& X);
        QList<float> mapSorted(QList<float>& X);
};

%MappedType QList<float>
{
%TypeHeaderCode
#include <qlist.h>
%End

%ConvertFromTypeCode
    // Create the list.
    PyObject *l;

    if ((l = PyList_New(sipCpp->size())) == NULL)
        return NULL;

    // Set the list elements.
    for (int i = 0; i < sipCpp->size(); ++i)
    {
        PyObject *pobj;

        if ((pobj = PyFloat_FromDouble(sipCpp->value(i))) == NULL)
        {
            Py_DECREF(l);

            return NULL;
        }

        PyList_SET_ITEM(l, i, pobj);
    }

    return l;
%End

%ConvertToTypeCode
    // Check the type if that is all that is required.
    if (sipIsErr == NULL)
        return PyList_Check(sipPy);

    QList<float> *ql = new QList<float>;

    for (int i = 0; i < PyList_GET_SIZE(sipPy); ++i)
        ql->append((float)PyFloat_AsDouble(PyList_GET_ITEM(sipPy, i)));

    *sipCppPtr = ql;

    return sipGetState(sipTransferObj);
%End
};

