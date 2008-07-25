#include "ImageTools.h"

#include <iostream>
#include <stdio.h>
#include <algorithm>

#ifdef WIN32
#include <winsock2.h>
#else
#include <netinet/in.h>
#endif



ImageTransfer::ImageTransfer(): values(), imgData(),transferedData() {
    for (unsigned int i=4; i--; )
        curves.append(BezierCurve());
    qimg=NULL;
    schedTransfer=false;
    CWRSteps=0;
    flipImg=false;
}

ImageTransfer::~ImageTransfer() {
    deleteData();
}

void ImageTransfer::deleteData() {
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
    rawType=format;
    
    
    if (format==0) {
        // floating point
        unsigned int N=len/4;
        cout << "Imgsize " << N << " " << width*height << endl;
        float* arr=(float*)inData;
        
        values.clear();
        QList<QList<unsigned int> > indexForValues;

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
        
        #ifdef __DEBUG__
        cout << "Values: " << values.size() << endl;
        #endif
        
        float norm=1.0/values.last();
        for (unsigned int n=values.size(); n--; ) {
            values[n]*=norm;
        }
        
        imgData.resize(N);
        for (unsigned int i=indexForValues.size(); i--; ) {
            for (unsigned int j=indexForValues[i].size(); j--; ) {
                imgData[indexForValues[i][j]]=i;
            }
        }
        
        #ifdef __DEBUG__
        cout << "imgData Set: " << endl;
        #endif
        
            
        transferedData.resize(N);
    } else if (format==1) {
        // 24bit RGB
        imgData.resize(len/3);
        for (unsigned int n=imgData.size(); n--; )
            imgData[n]=(inData[3*n+2]<<16) | (inData[3*n+1]<<8) | (inData[3*n]);
        transferedData.resize(len/3);
    }
    
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
    #ifdef __DEBUG__
    cout << "doImgRot " << _CWRSteps << " " << flip << " " << imageWidth << " " << imageHeight << " " << imgData.size() << endl;
    #endif
    
    QVector<unsigned int> tmp(imgData);
    
    unsigned int w=imageWidth;
    unsigned int h=imageHeight;
    unsigned m;
    if (flip) {
        if (_CWRSteps==0) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[w-1-n%w+w*(n/w)]=tmp[n];
        } else if (_CWRSteps==1) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[n/w+h*(n%w)]=tmp[n];
        } else if (_CWRSteps==2) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[n%w+w*(h-1-n/w)]=tmp[n];
        } else if (_CWRSteps==3) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[h-1-n/w+h*(w-1-n%w)]=tmp[n];
        }
    } else {
        if (_CWRSteps==1) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[n/w+h*(w-1-n%w)]=tmp[n];
        } else if (_CWRSteps==2) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[w-1-n%w+w*(h-1-n/w)]=tmp[n];
        } else if (_CWRSteps==3) {
            for (unsigned int n=tmp.size(); n--; ) 
                imgData[h-1-n/w+h*(n%w)]=tmp[n];
        }
    }        
    if (_CWRSteps%2==1)
        qSwap(imageWidth, imageHeight);

    
    if (qimg!=NULL) {
        delete qimg;
        qimg=NULL;
    }
    #ifdef __DEBUG__
    cout << "New QImage" << transferedData.size() << endl;
    #endif
    qimg = new QImage((unsigned char *)transferedData.data(), imageWidth, imageHeight, QImage::Format_RGB32);
    schedTransfer=true;    
}


void ImageTransfer::doFloatTransfer() {
    #ifdef __DEBUG__
    cout << "float transfer: calc Colortable" << endl;
    #endif

    QList<float> vMap = curves[0].mapSorted(values);
    QVector<quint32> colors(vMap.size());

    unsigned int hints[4];
    for (unsigned int i=4; i--; ) hints[i]=0;
    for (unsigned int n=vMap.size(); n--; ) {
        float vval=vMap[n];
        unsigned int rgbVal=0xFF;
        for (unsigned int i=0; i<3; i++) {
            rgbVal<<=8;
            rgbVal|=(unsigned int)(255.0*curves[i+1](vval,hints[i+1]));
        }
        colors[n]=rgbVal;
    }
    #ifdef __DEBUG__
    cout << "float transfer: Transfer Image" << endl;
    #endif
    for (unsigned int n=transferedData.size(); n--; ) {
        transferedData[n]=colors[imgData[n]];
    }
}

void ImageTransfer::doRGBTransfer() {
    cout << "Do RGB Transfer" << endl;
    QList<float> valCurve=curves[0].range(0, 1.0/255, 256);
    QVector<unsigned int> rgbCurve[3];
    for (unsigned int i=3; i--; ) {
        QList<float> tmp=curves[i+1].mapSorted(valCurve);
        rgbCurve[i].resize(256);
        unsigned int shift=16-8*i;
        for (unsigned n=256; n-- ; ) {
            unsigned int val=((unsigned int)(n*tmp[n]))<<shift;
            rgbCurve[i][n]=val;
        }
    }
    union rgbTuple {
        unsigned int val;
        unsigned char argb[4];
    };
    for (unsigned int n=transferedData.size(); n--; ) {
        rgbTuple t;
        t.val=imgData[n];
        unsigned int rgbVal=0xFF000000 | rgbCurve[0][t.argb[0]] | rgbCurve[1][t.argb[1]] | rgbCurve[2][t.argb[2]];
        transferedData[n]=rgbVal;
    }
}

void ImageTransfer::doTransfer() {
    if (rawType==0) {
        doFloatTransfer();
    } else if (rawType==1) {
        doRGBTransfer();
    }
}

QImage* ImageTransfer::qImg() {
    #ifdef __DEBUG__
    cout << "Image Request " << schedTransfer << endl;
    #endif
    if (schedTransfer) {
        doTransfer();
        schedTransfer=false;
    }
    return qimg;
}
