import Image
import ImageFile
import ImageQt
import os


class FujiBASImageFile(ImageFile.ImageFile):
    format = "BAS"
    format_description = "Fuji BAS Reader Image Plate format"
     
    def _open(self):
        # Check if we already opened inf:
        magic=self.fp.read(14)
        self.fp.seek(0)
        if magic=='BAS_IMAGE_FILE':
            self.infFile=self.fp
            for ext in ('img',  'IMG'):
                try:
                    self.imgFile=open(self.fp.name[:-3]+ext,  'rb')
                    break
                except:
                    pass
        else:
            self.imgFile=self.fp
            for ext in ('inf',  'INF'):
                try:
                    self.infFile=open(self.fp.name[:-3]+ext)
                    magic=self.infFile.read(14)
                    if magic=='BAS_IMAGE_FILE':
                        self.inf.seek(0)
                        break
                except:
                    pass
        # check header
        if magic!='BAS_IMAGE_FILE':
            raise SyntaxError, "not a FujiBAS file"

        if not self.imgFile:
            raise SyntaxError,  "IMG File not found???"
        
        self.fp=self.imgFile
        
        self.header = self.infFile.readlines()
        self.resx=0.1*int(self.header[3])
        self.resy=0.1*int(self.header[4])
        self.bpp=int(self.header[5])
        self.width=int(self.header[6])
        self.height=int(self.header[7])
        self.sensitivity=int(self.header[8])
        self.latitude=int(self.header[9])
        self.date=self.header[10]
        self.gesCounts=int(self.header[11])
        
        # size in pixels (width, height)
        self.size = (self.width,  self.height)
        
        if os.stat(self.imgFile.name)[6]!=self.width*self.height*2:
            raise SyntaxError,  "IMG doesnt have correct size"
        
        
        self.mode = "F"

        # data descriptor
        self.tile = [
            ("raw", (0, 0) + self.size, 0, ('F;16B', 0, 1))
        ]

Image.register_open("BAS", FujiBASImageFile)
Image.register_extension("BAS", ".inf")
Image.register_extension("BAS", ".img") 


