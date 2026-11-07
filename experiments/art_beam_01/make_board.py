"""Label only genuine matching Blender/Godot captures."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent/'screenshots';TILE=(640,360);BAR=42
try:F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except OSError:F=ImageFont.load_default()
views=(('godot_distance300','Godot ~300 px'),('godot_side','Godot side'),('godot_detail','Godot joint/detail'),
       ('blender_distance300','Blender ~300 px'),('blender_side','Blender side'),('blender_joint','Blender joint'),('blender_isolated','Blender isolated beam'))
board=Image.new('RGB',(3*TILE[0],len(views)*(TILE[1]+BAR)),'#202829');draw=ImageDraw.Draw(board)
for i,(view,caption) in enumerate(views):
 for j,(variant,label) in enumerate((('A','Original'),('B','Bevel + Clouds'),('C','B + baked weather/cracks'))):
  path=P/(view.replace('godot','godot_'+variant).replace('blender','blender_'+variant)+'.png')
  with Image.open(path) as img:
   assert img.size==(1280,720),path
   tile=img.convert('RGB').resize(TILE,Image.Resampling.LANCZOS)
  x=j*TILE[0];y=i*(TILE[1]+BAR);draw.text((x+8,y+8),caption+' | '+variant+' '+label,font=F,fill='#f7f0e1');board.paste(tile,(x,y+BAR))
board.save(P/'comparison_board.png');print('ART_BEAM_BOARD',board.size)
