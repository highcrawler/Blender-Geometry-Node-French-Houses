"""Arrange existing unedited Cycles images side by side; Pillow is not the renderer."""
from pathlib import Path
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parent/'screenshots'
for suffix, dims, name in (('iso', (800, 600), 'before_after.png'),
                           ('iso_300', (480, 360), 'before_after_300.png'),
                           ('front', (800, 600), 'before_after_front.png'),
                           ('detail', (800, 600), 'before_after_detail.png'),
                           ('eave', (800, 600), 'before_after_eave.png')):
    a, b = [Image.open(root/f'{label}_{suffix}.png').convert('RGB')
            for label in ('baseline', 'cc0')]
    assert a.size == b.size == dims
    board = Image.new('RGB', (2*dims[0], dims[1]+42), (40, 41, 44))
    board.paste(a, (0, 42))
    board.paste(b, (dims[0], 42))
    draw = ImageDraw.Draw(board)
    draw.text((20, 12), 'PHASE 8D H - BASELINE', fill=(240, 235, 220))
    draw.text((dims[0]+20, 12), 'POLY HAVEN - CC0 MATERIAL', fill=(240, 235, 220))
    board.save(root/name)
    print('08F_BOARD_PASS', name)
