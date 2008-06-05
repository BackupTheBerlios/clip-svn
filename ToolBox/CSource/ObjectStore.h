#ifndef __OBJECTSTORE_H__
#define __OBJECTSTORE_H__

#include <QtCore/QObject>
#include <QtCore/QVector>
#include <QtCore/QList>

class ObjectStore: public QObject {
    Q_OBJECT
    public:
        ObjectStore(QObject* parent=0);
        unsigned int size();
        QObject* at(unsigned int i);
        
    public slots:
        void addObject(QObject *o);
        void removeObject(QObject *o);
    private:
        QList<QObject *> set;
};

#endif
