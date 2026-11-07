"""Arrange genuine captures at equal scale; no visual edits to the source images."""
from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).resolve().parent/'screenshots'
board=Image.new('RGB',(1280,1200),(32,33,36));draw=ImageDraw.Draw(board)
for row,view in enumerate(('normal','distance300','detail')):
    for col,variant in enumerate(('reference','candidate')):
        image=Image.open(p/f'{variant}_{view}.png').convert('RGB')
        assert image.size==(1280,720)
        thumb=image.resize((640,360),Image.Resampling.LANCZOS)
        board.paste(thumb,(col*640,row*400+26))
        draw.text((col*640+12,row*400+5),f'{variant} / {view}',fill='white')
board.save(p/'comparison_board.png')
print('09K_BOARD',p/'comparison_board.png')
