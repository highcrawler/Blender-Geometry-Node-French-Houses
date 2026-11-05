"""Arrange three actual Blender Cycles PNGs without changing exposure, camera or lighting.
Run: python3 experiments/cottage_generator_08c/make_board.py (requires Pillow).
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent/'screenshots'
labels=('BASELINE','VARIANT_A','VARIANT_B')
images=[Image.open(root/(label.lower()+'_iso.png')).convert('RGB') for label in labels]
assert len({im.size for im in images})==1 and images[0].size==(800,600)
board=Image.new('RGB',(800*3,648),(42,43,46))
d=ImageDraw.Draw(board)
for i,(label,im) in enumerate(zip(labels,images)):
    board.paste(im,(i*800,48))
    d.text((i*800+24,14),label,fill=(240,235,219))
board.save(root/'all_three.png',pnginfo=None)
print('08C_BOARD_PASS',root/'all_three.png')
