"""One genuine through-hole WALL_WINDOW; local contract matches WALL_PLAIN."""
from dataclasses import dataclass
from wall_plain import WallPlain

TYPE_ID = 'WALL_WINDOW'


@dataclass(frozen=True)
class WallWindow:
    height: float
    thickness: float
    sill_v: float  # local vertical distance to lower edge of the hole; derived from rail
    width_ratio: float = .32
    height_ratio: float = .34
    infill_material: str = '09I_A_clay_constant'
    oak_material: str = '09J_A_weathered_oak_constant'

    def opening(self, width):
        opening_w = width * self.width_ratio
        opening_h = self.height * self.height_ratio
        l = (width - opening_w) / 2
        r = l + opening_w
        b = self.sill_v
        t = b + opening_h
        if not (width > 0 and self.thickness > 0 and self.height > 0 and
                l > .12 and width-r > .12 and b > .15 and t < self.height-.15):
            raise ValueError('window does not fit within upper infill')
        return (l, r, b, t)

    def geometry(self, width, cap_left=True, cap_right=True):
        """Closed rectangular annulus, with real plaster jamb/reveal faces."""
        l, r, b, t = self.opening(width)
        half = self.thickness / 2
        # 4 outer corners BL,BR,TR,TL and 4 inner corners, first front then back.
        points = [(0,0),(width,0),(width,self.height),(0,self.height),
                  (l,b),(r,b),(r,t),(l,t)]
        verts = [(u,v,n) for n in (half,-half) for u,v in points]
        ring = [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        faces = []
        for a,c,d,e in ring:
            faces.extend(((a,c,d),(a,d,e)))           # front, +normal
            faces.extend(((a+8,d+8,c+8),(a+8,e+8,d+8))) # back, -normal
        faces.extend([(8,9,1,0),(11,3,2,10)])          # bottom and top
        if cap_left:faces.append((8,0,3,11))
        if cap_right:faces.append((9,10,2,1))
        faces.extend([(12,15,7,4),(13,5,6,14),
                      (12,4,5,13),(15,14,6,7)])         # 4 inside reveal faces
        assert sum(len(f)-2 for f in faces)==(32 if cap_left and cap_right else 28 if not cap_left and not cap_right else 30)
        return verts,faces

    def member_specs(self, width):
        """Four individually replaceable solid-oak pieces in local u,v,n coordinates."""
        l,r,b,t=self.opening(width)
        return [
            # 3 mm into the aperture avoids coplanar timber/plaster reveal faces.
            {'role':'left_jamb','a':(l-.0375+.003,b,.065),'b':(l-.0375+.003,t,.065),'thickness':.075},
            {'role':'right_jamb','a':(r+.0375-.003,b,.065),'b':(r+.0375-.003,t,.065),'thickness':.075},
            {'role':'head','a':(l-.075,t+.045-.003,.065),'b':(r+.075,t+.045-.003,.065),'thickness':.09},
            {'role':'sill','a':(l-.11,b-.05+.003,.075),'b':(r+.11,b-.05+.003,.075),'thickness':.10},
        ]

    def contract(self,module_id,width,world_mount,mesh_name,cap_left,cap_right):
        base=WallPlain(self.height,self.thickness,self.infill_material)
        result=base.contract(module_id,width,world_mount,mesh_name,cap_left,cap_right)
        result['type']=TYPE_ID
        result['materials']={'infill':self.infill_material,'frame_parts':self.oak_material}
        l,r,b,t=self.opening(width)
        result['opening_local']={'left':l,'right':r,'bottom':b,'top':t,'width':r-l,'height':t-b,
                                 'through_normal_from':-self.thickness/2,'through_normal_to':self.thickness/2}
        result['part_roles']=[item['role'] for item in self.member_specs(width)]
        return result
