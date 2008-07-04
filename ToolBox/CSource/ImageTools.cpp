#include "ImageTools.h"

#include <iostream>
#include <stdio.h>
#include <algorithm>

#ifdef WIN32
#include <winsock2.h>
#else
#include <netinet/in.h>
#endif


class mySort {
    public:
        mySort(float* _weight) {
            weight=_weight;
        }
        bool operator()(unsigned int a, unsigned int b) {
            return weight[a]<weight[b];
        }
    private:
        float* weight;
};

ImageTransfer::ImageTransfer(): sortedIdx(),curves() {
    for (unsigned int i=4; i--; )
        curves.append(BezierCurve());
    rawData=NULL;
    rawLen=0;
    transferedData=NULL;
    transferedLen=0;
    qimg=NULL;
    schedTransfer=false;
#ifdef __DEBUG__
    cout << "ImageTransfer constructor" << endl;
#endif
}

ImageTransfer::~ImageTransfer() {
    // TODO: Delete data
}

void ImageTransfer::deleteData() {
    if (rawData!=NULL) {
        delete rawData;
        rawData=NULL;
        rawLen=0;
    }
    if (transferedData!=NULL) {
        delete transferedData;
        transferedData=NULL;
        transferedLen=0;
    }
    if (qimg!=NULL) {
        delete qimg;
        qimg=NULL;
    }
    sortedIdx.clear();
    
}

void ImageTransfer::setData(unsigned int width, unsigned int height, unsigned int format, unsigned char *inData, unsigned int len) {
    deleteData();
#ifdef __DEBUG__
    cout << "get Data, len=" << len << " width=" << width << " height=" << height << endl;
#endif
    rawData = new unsigned char[len];
    memcpy(rawData, inData, len);
    rawLen=len;
    rawType=format;
    
    if (format==0) {
        // floating point
        unsigned int N=rawLen/4;
#ifdef __DEBUG__
    cout << "pixel" << N << endl;
#endif
        float* arr=(float*)rawData;
        sortedIdx.resize(N);
        for (unsigned int i=N; i--; ) 
            sortedIdx[i]=i;
        sort(sortedIdx.begin(), sortedIdx.end(), mySort(arr));
        float maxVal=arr[sortedIdx[N-1]];
        for (unsigned int i=N; i--; )
            arr[i]/=maxVal;
        transferedLen=4*N;
    } else if (format==1) {
        // 24bit RGB
        transferedLen=4*len/3;
    }
    
    transferedData = new unsigned char[transferedLen];
    qimg = new QImage((unsigned char *)transferedData, width, height, QImage::Format_RGB32);
    schedTransfer=true;
}


void ImageTransfer::setTransferCurves(QList<BezierCurve> bc) {
    curves=bc;
    schedTransfer=true;
}

QList<BezierCurve> ImageTransfer::getTransferCurves() {
    return curves;
}


void ImageTransfer::doFloatTransfer() {
    unsigned int N=rawLen/4;
    float* arr=(float*)rawData;
    
    //cout << "Load init CP " << curves.size() << endl;
    BezierCurve::CurveParams vP=curves[0].getCurveParam(0);
    //cout << "Loaded init CP " << endl;
    unsigned int hints[3];
    hints[0]=0;
    hints[1]=0;
    hints[2]=0;
    unsigned int n=N;
    while (n) {
        //cout << "Loop No " << n << endl;

        unsigned int idx;
        double val;
        while (n && (val=arr[sortedIdx[N-n]])<=vP.Xmax) {
            //cout << "calc val " << val << endl;
            double vval=vP.calc(val);
            //cout << "get val " << vval << endl;
                
            unsigned int rgbVal=0xFF;
            for (unsigned int i=3; i--; ) {
                rgbVal<<=8;
                rgbVal|=(unsigned int)(255.0*curves[i+1](vval,hints[i]));
            }
            //cout << "calc rgb vals" << rgbVal << endl;
            while (n && val==arr[idx=sortedIdx[N-n]]) {
                ((unsigned int *)transferedData)[idx]=rgbVal;
                n--;
            }
            //cout << "all vals written" << endl;
        }
        vP=curves[0].getCurveParam(val);
    }
}

void ImageTransfer::doRGBTransfer() {
    //FIXME: Implement
}

void ImageTransfer::doTransfer() {
    if (rawType==0) {
        doFloatTransfer();
    } else if (rawType==1) {
        doRGBTransfer();
    }
}

QImage* ImageTransfer::qImg() {
    if (schedTransfer) {
        doTransfer();
        schedTransfer=false;
    }
    return qimg;
}
