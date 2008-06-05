import re

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

allPointGrps=[cubicPoint, hexagonalPoint, trigonalPoint, tetragonalPoint, orthorhombicPoint, monoclinicPoint, triclinicPoint]

centerSymbols = ['P', 'A', 'B', 'C', 'I', 'F', 'R']

class SpaceGroup:
  def __init__(self):
    self.symbol=None
    pass
  
  def parseGroupSymbol(self, s):
    pointGrp=None
    cSym=None
    
    s=s.replace(' ','').capitalize()
    pGrp=s[1:]  
    
    for grps in allPointGrps:
      for k in grps:
        if re.match('^'+grps[k]+'$', pGrp, re.VERBOSE):
          pointGrp=k
          break
    for cs in centerSymbols:
      if s[0]==cs:
        cSym=cs
        break
    if cSym and pointGrp:
      self.pointGrp=pointGrp
      self.system=pointGroups[self.pointGrp]
      self.symbol=s
      self.centering=cSym
      return True
    self.pointGrp=None
    self.system=None
    self.symbol=s
    self.centering=None
    
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
    if self.system==triclinic:
      symConst=[0,0,0,0,0,0]
    elif self.system==monoclinic:
      symConst=[0,0,0,90,0,90]
    elif self.system==orthorhombic:
      symConst=[0,0,0,90,90,90]
    elif self.system==tetragonal:
      symConst=[0,-1,0,90,90,90]
    elif self.system==trigonal:
      symConst=[0,-1,-1,0,-4,-4]
    elif self.system==cubic:
      symConst=[0,-1,-1,90,90,90]
    else:
      symConst=[0,0,0,0,0,0]
    return symConst
