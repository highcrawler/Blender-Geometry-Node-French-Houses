"""Deterministic warm oak atlas: sparse interrupted longitudinal checks, not stripes.

Procedurally rasterized maps are already GLB-compatible: no shader bake is needed.
Pure Python/Pillow, one isolated beam, no external asset/texture source.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random,math,json
P=Path(__file__).resolve().parent;OUT=P/'textures';OUT.mkdir(exist_ok=True)
W,H=1024,512;SEED=715021;random_gen=random.Random(SEED)
color=Image.new('RGB',(W,H));pixels=color.load();height=Image.new('L',(W,H),128);hp=height.load()
# Broad, low-contrast, warm patina follows longitudinal wood grain. Four bands
# represent the four long sides; unique grain phases avoid mirror duplication.
for band in range(4):
 y0=band*128;phases=[random_gen.uniform(0,math.tau) for _ in range(8)]
 knots=[random_gen.uniform(-1,1) for _ in range(17)]
 for y in range(y0,y0+128):
  local=y-y0
  for x in range(W):
   s=x/64;i=min(int(s),15);t=s-i
   slow=knots[i]*(1-t)+knots[i+1]*t
   fibre=math.sin(local*.23+2.8*math.sin(x*.014+phases[2])+phases[3])
   fibre_fade=max(0.,.42+.48*math.sin(x*.025+phases[6]))
   knotscale=math.sin(x*.021+phases[4])*.46 + math.sin(x*.006+phases[5])*.5
   shade=15*slow+2.1*fibre*fibre_fade+6*knotscale
   # muted aging: face remains warm even in pale sections
   pixels[x,y]=(int(max(35,min(230,123+shade))),int(max(28,min(205,94+shade*.81))),int(max(20,min(180,68+shade*.68))))
   hp[x,y]=int(128+max(-8,min(8,2*fibre*fibre_fade)))
# Uneven hewing: a handful of tapered chipped tool marks; sparse, not wallpaper.
draw=ImageDraw.Draw(color);hd=ImageDraw.Draw(height)
hewn=[]
for band in range(4):
 for _ in range(10 if band==1 else 6):
  x=random_gen.randrange(30,950);y=band*128+random_gen.randrange(9,119)
  run=random_gen.randrange(26,84);width=random_gen.randrange(2,5)
  shade=random_gen.choice([(149,116,79),(154,120,85),(100,75,53)])
  poly=[(x,y),(min(W-4,x+run),y+random_gen.randrange(-3,4)),(min(W-4,x+run-14),y+width),(x+9,y+width)]
  draw.polygon(poly,fill=shade);hd.polygon(poly,fill=138)
  hewn.append((band,x,y,run))
# Real seasoning checks follow grain. 3 interrupted chains on broad front,
# 1 on the adjacent side, almost none on remaining sides. Never span full beam.
cracks=[]
# The outward +world-X face is local -X = atlas band 1. Favor that face.
for band,count in ((0,1),(1,2),(2,1),(3,0)):
 for k in range(count):
  start=random_gen.randrange(85,710);end=min(920,start+random_gen.randrange(135,240))
  yy=band*128+random_gen.randrange(29,98);phase=random_gen.uniform(0,6)
  segments=[];cursor=start
  while cursor<end:
   seglen=random_gen.randrange(20,61);limit=min(cursor+seglen,end)
   points=[]
   for x in range(cursor,limit+1,5):
    y=int(yy+2.5*math.sin(x*.021+phase)+1.2*math.sin(x*.061+phase*2))
    points.append((x,y))
   if len(points)>1:
    # dark inset with a tiny upper lip; ends stop irregularly.
    draw.line([(x,y+2) for x,y in points],fill=(159,122,83),width=2)
    draw.line(points,fill=(54,36,24),width=random_gen.choice((3,4,5,5)))
    hd.line(points,fill=43,width=4)
    segments.append([cursor,limit])
   cursor=limit+random_gen.randrange(18,48)
  cracks.append({'face_band':band,'from_px':start,'to_px':end,'segments':segments,'center_y_px':yy})
# One clearly readable split on the outward face, still only intermittent
# and travelling with the grain rather than repeating every atlas row.
principal=[]
for start,end in ((162,292),(449,508),(737,848)):
 points=[(x,int(191+7.5*math.sin(x*.034)+2.5*math.sin(x*.14))) for x in range(start,end+1,4)]
 draw.line([(x,y+4) for x,y in points],fill=(149,112,75),width=3)
 for i in range(len(points)-1):
  width=max(3,round(7+2*math.sin(i*.53+start)))
  draw.line(points[i:i+2],fill=(51,33,24),width=width)
  hd.line(points[i:i+2],fill=40,width=width)
 principal.append([start,end])
cracks.append({'face_band':1,'from_px':162,'to_px':848,'segments':principal,'center_y_px':191,'principal':True})
# Tangent normals derived from smoothed height: dark cracks are *inward*, not
# raised black paint. Clamp gradient for controlled non-plastic relief.
hsm=height.filter(ImageFilter.GaussianBlur(.85));src=hsm.load()
normal=Image.new('RGB',(W,H));dst=normal.load()
for y in range(H):
 for x in range(W):
  lx=src[max(0,x-1),y];rx=src[min(W-1,x+1),y]
  by=src[x,max(0,y-1)];ty=src[x,min(H-1,y+1)]
  nx=max(-.48,min(.48,(lx-rx)*.014));ny=max(-.48,min(.48,(by-ty)*.014));nz=1.
  inv=1/math.sqrt(nx*nx+ny*ny+1)
  dst[x,y]=(round(128+127*nx*inv),round(128+127*ny*inv),round(128+127*inv))
color_path=OUT/'natural_oak_color_1024x512.png';normal_path=OUT/'natural_oak_normal_1024x512.png'
color.save(color_path,optimize=True);normal.save(normal_path,optimize=True)
report={'seed':SEED,'resolution':[W,H],'mapping':'longitudinal local +Z -> U across 1024px; four faces each 128px in V',
        'oak_role_rgb_8bit':[123,94,68],'hewing_marks':len(hewn),'crack_chains':cracks,
        'color_bytes':color_path.stat().st_size,'normal_bytes':normal_path.stat().st_size,
        'rasterizer':'Pillow; no Blender shader bake or third-party textures'}
(P/'texture_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('WOOD02_TEXTURES',report['color_bytes'],report['normal_bytes'],len(cracks),'chains')
