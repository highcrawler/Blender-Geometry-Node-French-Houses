"""Bounded rectangle input adapter; the original GenerateHouse remains untouched."""
import math
import bpy
from .assets import HOUSE_TAG

VERSION_KEY = 'mbg_footprint_version'
SHAPE_KEY = 'mbg_shape'
WIDTH_MIN, WIDTH_MAX = 3.2, 7.0
DEPTH_MIN, DEPTH_MAX = 3.0, 5.0
PRESETS = {'COMPACT': (4.0, 3.2), 'NARROW': (3.2, 5.0), 'WIDE': (7.0, 4.0)}
SHAPES = ('COMPACT', 'NARROW', 'WIDE', 'CUSTOM')
ITEMS = [
    ('COMPACT', 'Compact', 'Kompaktes Wohnhaus: 4,0 m breit, 3,2 m tief', 0),
    ('NARROW', 'Narrow', 'Schmales Stadthaus: 3,2 m breit, 5,0 m tief', 1),
    ('WIDE', 'Wide', 'Breiteres Gebäude: 7,0 m breit, 4,0 m tief', 2),
    ('CUSTOM', 'Custom', 'Individuelle lokale Rechteckmaße', 3),
]


def dimensions(obj):
    if obj and obj.type == 'MESH' and obj.data.vertices:
        pts = [v.co for v in obj.data.vertices]
        return (max(p.y for p in pts)-min(p.y for p in pts),
                max(p.x for p in pts)-min(p.x for p in pts))
    return PRESETS['COMPACT']


def controlled(obj):
    """Read only: no load handler, inferred migration or repair of authored meshes."""
    if not (obj and obj.type == 'MESH' and obj.get(HOUSE_TAG)
            and obj.get(VERSION_KEY) == 1 and not obj.library):
        return False
    mesh = obj.data
    if len(mesh.vertices) != 4 or len(mesh.polygons) != 1 or len(mesh.edges) != 4:
        return False
    width, depth = dimensions(obj)
    if not all(math.isfinite(c) for v in mesh.vertices for c in v.co):
        return False
    if not (WIDTH_MIN-1e-5 <= width <= WIDTH_MAX+1e-5 and DEPTH_MIN-1e-5 <= depth <= DEPTH_MAX+1e-5):
        return False
    expected = {(round(x, 5), round(y, 5), 0.0)
                for x in (-depth/2, depth/2) for y in (-width/2, width/2)}
    actual = {tuple(round(c, 5) for c in v.co) for v in mesh.vertices}
    return actual == expected and mesh.polygons[0].normal.z > .99


def _write(mesh, width, depth, *, rebuild=False):
    coords = [(-depth/2, -width/2, 0), (depth/2, -width/2, 0),
              (-depth/2, width/2, 0), (depth/2, width/2, 0)]
    if rebuild:
        mesh.clear_geometry()
        mesh.from_pydata(coords, [], [(0, 1, 3, 2)])
    else:
        # Preserve vertex order even after a harmless edit-mode reorder.
        for v in mesh.vertices:
            v.co = (math.copysign(depth/2, v.co.x), math.copysign(width/2, v.co.y), 0)
    mesh.update()


def initialize(obj):
    """Called only by New House on its fresh, unshared input mesh."""
    _write(obj.data, *PRESETS['COMPACT'], rebuild=True)
    obj[VERSION_KEY] = 1
    obj[SHAPE_KEY] = 'COMPACT'
    obj.update_tag(refresh={'OBJECT', 'DATA'})


def _resize(obj, width, depth, shape):
    if not controlled(obj):
        return False
    width = max(WIDTH_MIN, min(WIDTH_MAX, float(width)))
    depth = max(DEPTH_MIN, min(DEPTH_MAX, float(depth)))
    if not math.isfinite(width+depth):
        return False
    # Alt-D is allowed, but an explicit edit must never change another house.
    if obj.data.users > 1 or obj.data.library:
        obj.data = obj.data.copy()
    _write(obj.data, width, depth)
    obj[SHAPE_KEY] = shape
    obj.update_tag(refresh={'OBJECT', 'DATA'})
    return True


def set_dimension(obj, axis, value):
    if not controlled(obj) or not math.isfinite(value):
        return
    width, depth = dimensions(obj)
    old = width if axis == 'width' else depth
    if abs(value-old) < 1e-6:
        return
    _resize(obj, value if axis == 'width' else width,
            value if axis == 'depth' else depth, 'CUSTOM')


def shape_index(obj):
    if not controlled(obj):
        return 3
    key = obj.get(SHAPE_KEY, 'CUSTOM')
    if key not in PRESETS:
        return 3
    if max(abs(a-b) for a,b in zip(dimensions(obj), PRESETS[key])) > 1e-5:
        return 3
    return SHAPES.index(key)


def set_shape(obj, index):
    if not controlled(obj) or not 0 <= index < len(SHAPES):
        return
    key = SHAPES[index]
    if key == 'CUSTOM':
        obj[SHAPE_KEY] = key
    else:
        _resize(obj, *PRESETS[key], key)


def activate_rectangle(obj):
    """Explicit, undoable conversion only. Never called on file load/register."""
    width, depth = dimensions(obj)
    width = max(WIDTH_MIN, min(WIDTH_MAX, width))
    depth = max(DEPTH_MIN, min(DEPTH_MAX, depth))
    mesh = bpy.data.meshes.new(obj.name + ' Rectangle Footprint')
    try:
        _write(mesh, width, depth, rebuild=True)
    except Exception:
        bpy.data.meshes.remove(mesh)
        raise
    # The old authored mesh is not edited or deleted; other users retain it.
    obj.data = mesh
    obj[VERSION_KEY] = 1
    obj[SHAPE_KEY] = 'CUSTOM'
    obj.update_tag(refresh={'OBJECT', 'DATA'})
