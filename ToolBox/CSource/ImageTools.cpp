#include "ImageTools.h"

#include <iostream>
#include <stdio.h>
#include <algorithm>

#ifdef WIN32
#include <winsock2.h>
#else
#include <netinet/in.h>
#endif



ImageTransfer::ImageTransfer(): values(), indexForValues() {
    for (unsigned int i=4; i--; )
        curves.append(BezierCurve());
    rawData=NULL;
    rawLen=0;
    transferedData=NULL;
    transferedLen=0;
    qimg=NULL;
    schedTransfer=false;
    CWRSteps=0;
    flipImg=false;
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
}

void ImageTransfer::setData(unsigned int width, unsigned int height, unsigned int format, unsigned char *inData, unsigned int len) {
    cout << "Img Set data" << endl;
    deleteData();
    imageWidth=width;
    imageHeight=height;

    rawData = new unsigned char[len];
    memcpy(rawData, inData, len);
    rawLen=len;
    rawType=format;
    
    if (format==0) {
        // floating point
        unsigned int N=rawLen/4;
        cout << "Imgsize" << N << " " << width*height << endl;
        float* arr=(float*)rawData;
        values.clear();
        indexForValues.clear();
        
        for (unsigned int n=N; n--; ) {
            float val=arr[n];
            QList<float>::iterator iter=qLowerBound(values.begin(), values.end(), val);
            int idx=iter-values.begin();
            if (idx>=values.size() or values[idx]!=val) {
                // Value is new
                values.insert(idx, val);
                indexForValues.insert(idx,QList<unsigned int>());
            }
            indexForValues[idx].append(n);
        }    
        float norm=1.0/values.last();
        for (unsigned int n=values.size(); n--; ) {
            values[n]*=norm;
        }
        transferedLen=4*N;
    } else if (format==1) {
        // 24bit RGB
        transferedLen=4*len/3;
    }
    
    transferedData = new unsigned char[transferedLen];
    doImgRotation(0, false);
    schedTransfer=true;
}


void ImageTransfer::setTransferCurves(QList<BezierCurve> bc) {
    curves=bc;
    schedTransfer=true;
}

QList<BezierCurve> ImageTransfer::getTransferCurves() {
    return curves;
}

void ImageTransfer::doImgRotation(unsigned int _CWRSteps, bool flip) {
    CWRSteps=(CWRSteps+_CWRSteps)%4;
    flipImg=flipImg xor flip;
    cout << "doImgRot" << CWRSteps << " " << flipImg << " " << imageWidth << " " << imageHeight << endl;

    
    unsigned int N=imageWidth*imageHeight;
    unsigned int w=imageWidth;
    unsigned int h=imageHeight;
    for (unsigned int n=indexForValues.size(); n--; ) {
        for (unsigned int m=indexForValues[n].size(); m--; ) {
            unsigned int idx=indexForValues[n][m];
            unsigned int w=imageWidth;
            unsigned int h=imageHeight;
            unsigned int x=idx%w;
            unsigned int y=idx/w;
            for (unsigned int r=_CWRSteps; r--; ) {
                //y=h-1-y;
                x=w-1-x;
                qSwap(x,y);
                qSwap(w,h);
            }
            if (flip) 
                x=w-1-x;
            indexForValues[n][m]=x+y*w;
        }
    }
    if (qimg!=NULL) {
        delete qimg;
        qimg=NULL;
    }
    if (_CWRSteps%2==1)
        qSwap(imageWidth, imageHeight);
    qimg = new QImage((unsigned char *)transferedData, imageWidth, imageHeight, QImage::Format_RGB32);
    schedTransfer=true;    
}


void ImageTransfer::doFloatTransfer() {
    cout << "float transfer" << endl;
    unsigned int N=imageWidth*imageHeight;

    QList<float> vMap = curves[0].mapSorted(values);
    unsigned int hints[4];
    for (unsigned int i=4; i--; ) hints[i]=0;
    for (unsigned int n=values.size(); n--; ) {
        float vval=vMap[n];
        unsigned int rgbVal=0xFF;
        for (unsigned int i=3; i--; ) {
            rgbVal<<=8;
            rgbVal|=(unsigned int)(255.0*curves[i+1](vval,hints[i+1]));
        }
        for (unsigned int m=indexForValues[n].size(); m--; ) {
            unsigned int idx=indexForValues[n][m];
            ((unsigned int *)transferedData)[idx]=rgbVal;
        }
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
