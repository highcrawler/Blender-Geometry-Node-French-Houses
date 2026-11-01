"""Create labeled, side-by-side evidence and pixel differences; requires Pillow."""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

root = Path('tests/materials')
for view in ('iso', 'front', 'facade'):
    for label, first, second in (
        ('blender_vs_godot', root / 'blender' / f'baseline_{view}.png', root / 'godot' / f'baseline_{view}.png'),
        ('baseline_vs_reduced_blender', root / 'blender' / f'baseline_{view}.png', root / 'blender' / f'reduced_{view}.png'),
        ('baseline_vs_reduced_godot', root / 'godot' / f'baseline_{view}.png', root / 'godot' / f'reduced_{view}.png'),
    ):
        a, b = Image.open(first).convert('RGB'), Image.open(second).convert('RGB')
        assert a.size == b.size == (960, 720)
        out = Image.new('RGB', (1920, 748), (40, 40, 40))
        out.paste(a, (0, 28))
        out.paste(b, (960, 28))
        draw = ImageDraw.Draw(out)
        draw.text((12, 6), str(first.relative_to(root)), fill='white')
        draw.text((972, 6), str(second.relative_to(root)), fill='white')
        out.save(root / f'{label}_{view}.png')
        if label == 'baseline_vs_reduced_blender':
            diff = ImageChops.difference(a, b)
            print(view, 'Blender changed-pixel bounding box', diff.getbbox())
