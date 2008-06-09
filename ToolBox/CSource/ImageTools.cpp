#include "ImageTools.h"

#include <iostream>
#include <stdio.h>
#include <algorithm>

#ifdef WIN32
#include <winsock2.h>
#else
#include <netinet/in.h>
#endif

ParamSet::ParamSet() : D(4) {
    upper=0.0;
}

float ParamSet::calc(float x) {
    float v=((D[3]*x+D[2])*x+D[1])*x+D[0];
    if (v>1.0)
        return 1.0;
    if (v<0.0)
        return 0.0;
    return v;
}

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

ImageTransfer::ImageTransfer(): sortedIdx(),curves(4) {
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


void ImageTransfer::setTransferCurve(int channel, std::vector<double> upper, std::vector<double> D) {
#ifdef __DEBUG__
    cout << "setTransferCurve #" << channel << endl;
#endif
    curves[channel].clear();
#ifdef __DEBUG__
    cout << "No of Params:" << upper.size() << endl;
#endif    
    for (unsigned int i=0; i<upper.size(); i++) {
        ParamSet p;
        p.upper=upper[i];
#ifdef __DEBUG__
    cout << "upper limit" << upper[i] << endl;
#endif
        for (unsigned int j=0; j<4; j++) {
#ifdef __DEBUG__
    cout << "   Param #" << j << "=" << D[4*i+j] << endl;
#endif            
            p.D[j]=D[4*i+j];
        }
        curves[channel].push_back(p);
    }
    schedTransfer=true;
}
 
void ImageTransfer::doFloatTransfer() {
#ifdef __DEBUG__
    cout << "start FloatTransfer" << endl;
#endif

    unsigned int N=rawLen/4;
    float* arr=(float*)rawData;
    
    unsigned int n=0;
    unsigned int cPos[3];
    for (unsigned int i=3; i--; )
        cPos[i]=0;
    unsigned char rgb[3];
    for (unsigned int i=0; i<curves[0].size(); i++) {
        ParamSet p=curves[0][i];
        while (n<N and arr[sortedIdx[n]]<p.upper) {
            float val=arr[sortedIdx[n]];
            float nval=p.calc(val);
            for (unsigned int j=3; j--; ) {
                unsigned int s=curves[j+1].size();
                while (cPos[j]+1<s and nval>curves[j+1][cPos[j]].upper)
                    cPos[j]++;
                while (cPos[j]>0 and nval<curves[j+1][cPos[j]-1].upper)
                    cPos[j]--;
                rgb[2-j]=(unsigned char)(255.0*curves[j+1][cPos[j]].calc(nval));
            }
#ifdef __DEBUG__
            //cout << "inVal " << val << " -> (" << (int)rgb[0] << "," << (int)rgb[1] << "," << (int)rgb[2] << ")" << endl;
#endif

            while (n<N and val==arr[sortedIdx[n]]) {
                for (unsigned int i=3; i--; ) 
                    transferedData[4*sortedIdx[n]+i]=rgb[i];
                n++;
            }
        }
    }
}

void ImageTransfer::doRGBTransfer() {
    vector< vector<unsigned int> > Cmaps(3);
    unsigned int vPos=0;
    unsigned int cPos[3];

    for (unsigned int i=3; i--; ) {
        cPos[i]=0;    
        Cmaps[i].resize(256);
    }
    
    for (unsigned int i=256; i--; ) {
        float val=(float)i/255.0;
        while ((val>curves[0][vPos].upper) and (vPos+1<curves[0].size()))
            vPos++;
        
        float nval=curves[0][vPos].calc(val);
        
        for (unsigned int j=3; j--; ) {
            unsigned int s=curves[j+1].size();
            while (cPos[j]+1<s and nval>curves[j+1][cPos[j]].upper)
                cPos[j]++;
            while (cPos[j]>0 and nval<curves[j+1][cPos[j]-1].upper)
                cPos[j]--;
            Cmaps[j][i]=(unsigned char)(255.0*curves[j+1][cPos[j]].calc(nval));
        }
    }
        
    unsigned int N=rawLen/3;
    
    for (unsigned int i=N; i--; ) {
        for (unsigned int j=3; j--; ) {
            transferedData[4*i+2-j]=Cmaps[j][rawData[3*i+j]];
        }
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
    if (schedTransfer) {
        doTransfer();
        schedTransfer=false;
    }
    return qimg;
}
