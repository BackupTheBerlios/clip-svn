import re
from ToolBox import Mat3D, Vec3D
import math


    

class SpaceGroup:
    triclinic=1
    monoclinic=2
    orthorhombic=3
    trigonal=4
    hexagonal=5
    tetragonal=6
    cubic=7
    
    systems=[cubic, tetragonal, hexagonal, trigonal, orthorhombic, monoclinic, triclinic]
    
    
    triclinicPoint={'1': '(1)', 
                    '-1': '(-1)'}
    
    monoclinicPoint={'2': '(21?)', 
                     'm': '([mabc])', 
                     '2/m': '(21?)/([mnabcd])'}
    
    orthorhombicPoint={'222': '(21?)(21?)(21?)',
                      'mm2':r'''(?=
                                   [mnbcd][mnacd]21?
                                   |
                                   [mnbcd]21?[mnabd]
                                   |
                                   21?[mnacd][mnabd])
                                   ([mnabcd]|21?)([mnabcd]|21?)([mnabcd]|21?)''',
                      'mmm': '([mnbcd])([mnacd])([mnabd])'}
    tetragonalPoint={'4': '(4[123]?)',
                     '-4': '(-4)',
                     '4/m':'(4[123]?/[mnab])',
                     '422':'(4[123]?)(21?)(21?)',
                     '4mm':'(-?4[123]?)([mnabcd])([mnabcd])',
                     '-42m':'(-4)(?=21?[mnabcd]|[mnabcd]21?)(21?|[mnabcd])(21?|[mnabcd])',
                     '4/mmm':'(4[123]?/[mnab])([mnabcd])([mnabcd])'}
    
    trigonalPoint={'3': '(3[12]?)',
                   '-3':'(-3)',
                   '32':'(3[12]?)(?=21|12)(.)(.)',
                   '3m':'(-?3)(?=[mnabcd]1?|1[mnabcd])(.)(.?)'}
    hexagonalPoint={'6':'(6[12345]?)',
                    '-6':'(-6)',
                    '6/m':'(63?/m)',
                    '622':'(6[12345]?)(2)(2)',
                    '6mm':'(63?)([mc])([mc])',
                    '-6m2':'(-6)(?=2[mc]|[mc]2)(.)(.)',
                    '6/mmm':'(63?/[mc])([mc])([mc])'}
            
    
    
    cubicPoint={'23':'(21?)(-?3)',
                'm3':'([mnabcd])(-?3)',
                '432':'(4[123]?)(-?3)(2)',
                '43m': '(-?4[123]?)(-?3)([mnabcd])',
                'm3m': '([mnabcd])(-?3)([mnabcd])'}
    
    pointGroups={ '1'     : triclinic,
                  '-1'    : triclinic,
                  '2'     : monoclinic,
                  'm'     : monoclinic,
                  '2/m'   : monoclinic,
                  '222'   : orthorhombic,
                  'mm2'   : orthorhombic,
                  'mmm'   : orthorhombic,
                  '3'     : trigonal,
                  '-3'    : trigonal,
                  '32'    : trigonal,
                  '3m'    : trigonal,
                  '-32/m' : trigonal,
                  '6'     : hexagonal,
                  '-6'    : hexagonal,
                  '6/m'   : hexagonal,
                  '622'   : hexagonal,
                  '6mm'   : hexagonal,
                  '-6m2'  : hexagonal,
                  '6/mmm' : hexagonal,
                  '4'     : tetragonal,
                  '-4'    : tetragonal,
                  '4/m'   : tetragonal,
                  '422'   : tetragonal,
                  '4mm'   : tetragonal,
                  '-42m'  : tetragonal,
                  '4/mmm' : tetragonal,
                  '23'    : cubic,
                  'm3'    : cubic,
                  '432'   : cubic,
                  '43m'   : cubic,
                  'm3m'   : cubic }
                  
    
    inv=Mat3D((-1, 0, 0, 0, -1, 0, 0, 0, -1))
    mx =Mat3D((-1, 0, 0, 0,  1, 0, 0, 0,  1))
    my =Mat3D(( 1, 0, 0, 0, -1, 0, 0, 0,  1))
    mz =Mat3D(( 1, 0, 0, 0,  1, 0, 0, 0, -1))
    r2x=Mat3D(( 1, 0, 0, 0, -1, 0, 0, 0, -1))
    r2y=Mat3D((-1, 0, 0, 0,  1, 0, 0, 0, -1))
    r2z=Mat3D((-1, 0, 0, 0, -1, 0, 0, 0,  1))
    r4z=Mat3D(Vec3D(0, 0, 1), math.pi/2)
    r6z=Mat3D(Vec3D(0, 0, 1), math.pi/3)
    r3cub=Mat3D(Vec3D(1, 1, 1).normalized(), 2.0*math.pi/3)
    pointGroupGenerators=  {  '1'     : [],
                              '-1'    : [inv],
                              '2'     : [r2y],
                              'm'     : [my],
                              '2/m'   : [my, r2y],
                              '222'   : [r2x, r2y, r2z],
                              'mm2'   : [mx, my, r2z],
                              'mmm'   : [mx, my, mz],
                              '3'     : [],
                              '-3'    : [],
                              '32'    : [],
                              '3m'    : [],
                              '-32/m' : [],
                              '6'     : [r6z],
                              '-6'    : [r6z, inv],
                              '6/m'   : [r6z, mz],
                              '622'   : [r6z, mz],
                              '6mm'   : [r6z, mz],
                              '-6m2'  : [r6z, mz],
                              '6/mmm' : [r6z, mz],
                              '4'     : [r4z],
                              '-4'    : [r4z, inv],
                              '4/m'   : [r4z, mz],
                              '422'   : [r4z, r2x],
                              '4mm'   : [r4z, mx],
                              '-42m'  : [r4z, inv, r2x],
                              '4/mmm' : [r4z, mx, mz],
                              '23'    : [r2x, r3cub],
                              'm3'    : [mx, r3cub],
                              '432'   : [r4z, r3cub],
                              '43m'   : [r4z, r3cub],
                              'm3m'   : [inv, r4z, mx, r3cub]}
    
    allPointGrps=[cubicPoint, hexagonalPoint, trigonalPoint, tetragonalPoint, orthorhombicPoint, monoclinicPoint, triclinicPoint]
    
    centerSymbols = ['P', 'A', 'B', 'C', 'I', 'F', 'R']


    def __init__(self):
        self.symbol=None
        pass
  
    def parseGroupSymbol(self, s):
        pointGrp=None
        cSym=None

        self.pointGrp=None
        self.system=None
        self.symbol=s
        self.centering=None


        s=str(s)
        s=s.replace(' ','').capitalize()
        
        if len(s)<1:
            return False
        
        pGrp=s[1:]  
        
        for grps in self.allPointGrps:
          for k in grps:
            if re.match('^'+grps[k]+'$', pGrp, re.VERBOSE):
              pointGrp=k
              break
        if (s[0] in self.centerSymbols) and pointGrp:
          self.pointGrp=pointGrp
          self.system=self.pointGroups[self.pointGrp]
          self.symbol=s
          self.centering=s[0]
          return True
        return False
    
    def contrainCellToSymmetry(self, cell):
        constrain=self.getCellConstrain()
        for i in range(6):
            if constrain[i]<0:
                cell[i]=cell[-constrain[i]-1]
            elif constrain[i]>0:
                cell[i]=constrain[i]
        return cell
    
    def getCellConstrain(self):    
        if self.system==self.triclinic:
          symConst=[0,0,0,0,0,0]
        elif self.system==self.monoclinic:
          symConst=[0,0,0,90,0,90]
        elif self.system==self.orthorhombic:
          symConst=[0,0,0,90,90,90]
        elif self.system==self.tetragonal:
          symConst=[0,-1,0,90,90,90]
        elif self.system==self.trigonal:
          symConst=[0,-1,-1,0,-4,-4]
        elif self.system==self.cubic:
          symConst=[0,-1,-1,90,90,90]
        else:
          symConst=[0,0,0,0,0,0]
        return symConst
    
    def addGenerator(self, Set, m):
        run=True
        notChecked=Set
        while run:
            new=[]
            for e in notChecked:
                c=e*m
                for t in Set:
                    if (c-t).sqSum()<1e-5:
                        break
                else:
                    new.append(c)
            notChecked=new
            Set+=new
            run=len(new)>0
        return Set
            
    def getPointGroup(self):
        G=[Mat3D()]
        if self.pointGrp in self.pointGroupGenerators:
            for g in self.pointGroupGenerators[self.pointGrp]:
                self.addGenerator(G, g)
        return G
        
    def getLaueGroup(self):
        G=self.getPointGroup()
        self.addGenerator(G, self.inv)
        return G
