#ifndef __IMAGETOOLS_H__
#define __IMAGETOOLS_H__

#include <string>

#include <QtGui/QImage>
#include <vec3D.h>
#include <BezierCurve.h>


class ImageTransfer {
    public:
        ImageTransfer();
        ~ImageTransfer();
        
        void setData(unsigned int width, unsigned int height, unsigned int format, unsigned char *data, unsigned int len);
        QList<BezierCurve> getTransferCurves();
        void setTransferCurves(QList<BezierCurve> bc);
  

        QImage* qImg();
    private:
        void deleteData();
        void doTransfer();
        void doRGBTransfer();
        void doFloatTransfer();
    
        unsigned char* rawData;
        unsigned int rawLen;
        unsigned int rawType;
        QVector<unsigned int> sortedIdx;
    
        unsigned char* transferedData;
        unsigned int transferedLen;
        
        QList<BezierCurve> curves;
    
        QImage* qimg;
        bool schedTransfer;
};

#endif
