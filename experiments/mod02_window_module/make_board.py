"""Label and arrange only captured Blender/Godot PNGs; never synthesize geometry."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent/'screenshots';tile=(640,360);bar=44
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except OSError:font=ImageFont.load_default()

def board(rows,name):
 cols=max(map(len,rows));out=Image.new('RGB',(cols*tile[0],len(rows)*(tile[1]+bar)),'#1d2425');draw=ImageDraw.Draw(out)
 for i,row in enumerate(rows):
  for j,(shot,label) in enumerate(row):
   src=P/(shot+'.png')
   with Image.open(src) as image:
    assert image.size==(1280,720),src
    x=j*tile[0];y=i*(tile[1]+bar);draw.text((x+8,y+9),label,fill='#f4ede0',font=font)
    out.paste(image.convert('RGB').resize(tile,Image.Resampling.LANCZOS),(x,y+bar))
 out.save(P/name);print('MOD02_BOARD',P/name,out.size)

board([[('godot_A_'+view,'Godot 4.7 A | drei geschlossene Module'),('godot_B_'+view,'Godot 4.7 B | echtes Fenster')]
       for view in ('side','iso','distance300')]+[
       [('A_side','Blender 5.2 A | Referenz'),('B_side','Blender 5.2 B | Fenster')],
       [('godot_B_window_front','B | Fenster frontal'),('godot_C_single_front','C | WALL_WINDOW allein')],
       [('godot_B_window_oblique','B | Blick schraeg durch Loch'),('godot_C_single_oblique','C | Eigenes Modul/Pivot')],
       [('godot_B_reveal_detail','B | innere Laibung / Fensterbank'),('godot_C_single_back','C | Durchbruch von hinten')]],
      'comparison_board.png')
board([[('B_window_front','Blender B | Vorderseite'),('B_window_oblique','Blender B | Schraege'),('B_reveal_detail','Blender B | Laibung')],
       [('C_single_front','Blender C | einzelnes Modul'),('C_single_oblique','Blender C | eigene Teile'),('C_single_back','Blender C | Rueckseite')],
       [('A_side','A | drei WALL_PLAIN'),('B_side','B | mittleres WALL_WINDOW'),('A_restored','nach Wechsel wieder A')]],
      'module_proof_board.png')
