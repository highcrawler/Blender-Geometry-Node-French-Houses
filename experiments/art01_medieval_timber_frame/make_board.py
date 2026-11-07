"""Six paired comparisons made only from captured Blender/Godot image files."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;shots=P/'screenshots'
tile=(640,360);bar=44
rows=(('godot','side','Godot 4.7 · Seitenwand'),('godot','iso','Godot 4.7 · Isometrie'),('godot','detail','Godot 4.7 · Anschlüsse'),('godot','distance300','Godot 4.7 · ~300 px Gebäude'),('blender','side','Blender Cycles · Seitenwand'),('blender','iso','Blender Cycles · Isometrie'))
board=Image.new('RGB',(2*tile[0],len(rows)*(tile[1]+bar)),'#21282b');draw=ImageDraw.Draw(board)
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except OSError:font=ImageFont.load_default()
for r,(engine,view,label) in enumerate(rows):
 for col,(variant,vlabel) in enumerate((('A','A – unveränderte 9K-Referenz'),('B','B – eine Fachwerk-Seitenwand'))):
  f=shots/f'{engine}_{variant}_{view}.png';image=Image.open(f).convert('RGB');assert image.size==(1280,720),f
  x=col*tile[0];y=r*(tile[1]+bar);draw.text((x+10,y+10),f'{label} | {vlabel}',font=font,fill='white');board.paste(image.resize(tile,Image.Resampling.LANCZOS),(x,y+bar))
board.save(shots/'comparison_board.png');print('ART01_BOARD',shots/'comparison_board.png')
