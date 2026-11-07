"""Board uses only genuine matching engine screenshots, never composites geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent/'screenshots';TILE=(640,360);BAR=42
try:F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except OSError:F=ImageFont.load_default()
views=(('godot_distance300','Godot ~300px wall'),('godot_side','Godot side'),('godot_detail','Godot detail'),('godot_macro','Godot macro'),('godot_isolated','Godot isolated'),
       ('blender_distance300','Blender ~300px wall'),('blender_side','Blender side'),('blender_joint','Blender detail'),('blender_macro','Blender macro'),('blender_isolated','Blender isolated'))
result=Image.new('RGB',(3*TILE[0],len(views)*(TILE[1]+BAR)),'#202829');draw=ImageDraw.Draw(result)
for i,(view,caption) in enumerate(views):
 for j,(variant,label) in enumerate((('A','Original'),('B','Hand-worked mesh'),('C','Aged oak atlas'))):
  name=view.replace('godot','godot_'+variant).replace('blender','blender_'+variant)
  with Image.open(P/f'{name}.png') as img:
   assert img.size==(1280,720)
   tile=img.convert('RGB').resize(TILE,Image.Resampling.LANCZOS)
  x=j*TILE[0];y=i*(TILE[1]+BAR);draw.text((x+8,y+8),caption+' | '+variant+' '+label,font=F,fill='#f5eee0');result.paste(tile,(x,y+BAR))
result.save(P/'comparison_board.png');print('WOOD02_BOARD',result.size)
