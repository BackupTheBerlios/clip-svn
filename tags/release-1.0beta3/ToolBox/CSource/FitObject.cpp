#include <FitObject.h>

FitObject::FitObject():fitParameter() {
}

FitObject::~FitObject() {
}

void FitObject::setFitParameterNames(QList<QString> names) {
    fitParameter.clear();
    for (unsigned int i=0; i<names.size(); i++) {
        FitParameter p;
        p.name=names[i];
        p.enabled=false;
        p.bounds=qMakePair((double)-INFINITY, (double)INFINITY);
        p.changeHint=1.0;
        fitParameter << p;
    }
}

unsigned int FitObject::fitParameterNumber() {
    return fitParameter.size();
}

QString FitObject::fitParameterName(unsigned int n) {
    if (n<fitParameter.size())
        return fitParameter[n].name;
    return "";
}

double FitObject::fitParameterValue(unsigned int n) {
    return 0.0;
}

void FitObject::fitParameterSetValue(unsigned int n, double val) {
}

QPair<double, double> FitObject::fitParameterBounds(unsigned int n) {
    if (n<fitParameter.size())
        return fitParameter[n].bounds;
    return qMakePair((double)-INFINITY, (double)INFINITY);
}

double FitObject::fitParameterChangeHint(unsigned int n) {
    if (n<fitParameter.size())
        return fitParameter[n].changeHint;    
    return 1.0;
}

bool FitObject::fitParameterEnabled(unsigned int n) {
    if (n<fitParameter.size())
        return fitParameter[n].enabled;
    return false;
}

void FitObject::fitParameterSetEnabled(unsigned int n, bool enable) {
    if (n<fitParameter.size())
        fitParameter[n].enabled=enable;
}
