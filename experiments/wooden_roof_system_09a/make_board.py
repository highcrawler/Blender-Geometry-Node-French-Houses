"""Assemble Blender renders; retain native pixels in the 480x360 test row."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
views = ('iso', 'front', 'side', 'detail', 'ridge_eave', 'iso_300')
board = Image.new('RGB', (1020, 2070), (38, 39, 40))
draw = ImageDraw.Draw(board)
for row, view in enumerate(views):
    y = 24 + row * 330 if row < 5 else 1680
    for col, state in enumerate(('clean', 'aged')):
        image = Image.open(root / 'screenshots' / f'{state}_{view}.png').convert('RGB')
        if row < 5:
            image.thumbnail((480, 300))
        # Native 480x360 iso_300 images are pasted without scaling.
        x = 15 + col * 505
        board.paste(image, (x, y))
        draw.text((x, y - 16), f'{state.upper()} / {view}', fill=(240, 235, 215))
board.save(root / 'comparison_clean_vs_aged.jpg', quality=92)
