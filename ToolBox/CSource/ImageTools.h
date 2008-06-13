#ifndef __IMAGETOOLS_H__
#define __IMAGETOOLS_H__

#include <string>
#include <vector>
#include <QtGui/QImage>

#include "vec3D.h"

using namespace std;

class ParamSet {
    public:
        ParamSet();
        float upper;
        vector<float> D;
        float calc(float x);
};

class ImageTransfer {
    public:
        ImageTransfer();
        ~ImageTransfer();
        
        void setData(unsigned int width, unsigned int height, unsigned int format, unsigned char *data, unsigned int len);
        void setTransferCurve(int channel, std::vector<double> upper, std::vector<double> D);
  

        QImage* qImg();
    private:
        void deleteData();
        void doTransfer();
        void doRGBTransfer();
        void doFloatTransfer();
    
        unsigned char* rawData;
        unsigned int rawLen;
        unsigned int rawType;
        vector<unsigned int> sortedIdx;
    
        unsigned char* transferedData;
        unsigned int transferedLen;
        
        vector< vector<ParamSet> > curves;
    
        QImage* qimg;
        bool schedTransfer;
};

#endif
