"""Compose real Blender and Godot captures without altering their source images."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent;shots=p/'screenshots';tile=(640,360);header=58;w=3*tile[0];h=3*(tile[1]+header)
out=Image.new('RGB',(w,h),'#242d30');d=ImageDraw.Draw(out)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
except OSError:font=ImageFont.load_default()
for row,(prefix,view,title) in enumerate((('godot','detail','Godot 4.7 – Detail'),('godot','distance300','Godot 4.7 – ~300 px Gebäudehöhe'),('blender','detail','Blender 5.2.2 Cycles – Detail'))):
 for col,(v,label) in enumerate((('A','A – konstant'),('B','B – Rough Wood PBR'),('C','C – gebackene Maserung'))):
  image=Image.open(shots/f'{prefix}_{v}_{view}.png').convert('RGB');assert image.size in ((1280,720),(960,540))
  x=col*tile[0];y=row*(tile[1]+header);d.text((x+12,y+15),f'{title} | {label}',font=font,fill='#f5f5ef');out.paste(image.resize(tile,Image.Resampling.LANCZOS),(x,y+header))
out.save(shots/'comparison_board.png');print('WOOD01_BOARD',shots/'comparison_board.png')
