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
        void doImgRotation(unsigned int CWRSteps, bool flip);

        QImage* qImg();
    private:
        void deleteData();
        void doTransfer();
        void doRGBTransfer();
        void doFloatTransfer();
    
        unsigned imageWidth;
        unsigned imageHeight;

        QVector<unsigned char> rawData;
        unsigned int rawType;

        QVector<quint32> transferedData;
    
        // Needed for FloatTransfer
        QList<float> values;
        QVector<unsigned int> imgIndices;
    
        QList<BezierCurve> curves;
        
        QImage* qimg;
        bool schedTransfer;
    
        unsigned int CWRSteps;
        bool flipImg;        
};

#endif
