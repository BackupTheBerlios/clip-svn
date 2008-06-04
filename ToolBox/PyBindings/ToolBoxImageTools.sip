

class ImageTransfer {

%TypeHeaderCode
    #include <ImageTools.h>
    #include <string>
%End

 
    public:
        ImageTransfer();
        ~ImageTransfer();
        
        void setData(unsigned int width, unsigned int height, unsigned int type, unsigned char *data /Array/, unsigned int len /ArraySize/);
        void setTransferCurve(int type, std::vector<double> upper, std::vector<double> D);
  
        QImage* qImg();
};


