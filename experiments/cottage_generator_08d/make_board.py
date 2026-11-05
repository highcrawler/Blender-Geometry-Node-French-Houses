"""Losslessly arrange actual identically lit Blender frames. Needs Pillow, not for rendering."""
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent/'screenshots'
labels=('BASELINE','VARIANT_A','VARIANT_B','VARIANT_H')
for suffix,size,output in (('iso',(800,600),'all_four.png'),
                           ('iso_300',(480,360),'all_four_300.png')):
    images=[Image.open(root/(label.lower()+'_'+suffix+'.png')).convert('RGB') for label in labels]
    assert all(im.size==size for im in images)
    w,h=size
    board=Image.new('RGB',(w*len(labels),h+48),(42,43,46))
    drawer=ImageDraw.Draw(board)
    for i,(label,im) in enumerate(zip(labels,images)):
        board.paste(im,(i*w,48))
        drawer.text((i*w+20,14),label,fill=(240,235,219))
    board.save(root/output)
    print('08D_BOARD_PASS',root/output)
