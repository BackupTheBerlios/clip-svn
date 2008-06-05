class ObjectStore:  QObject {
%TypeHeaderCode
#include <ObjectStore.h>
%End
    public:
        ObjectStore(QObject* parent=0);
        unsigned int size();
        QObject* at(unsigned int i);
        
    public slots:
        void addObject(QObject *o);
        void removeObject(QObject *o);
};
