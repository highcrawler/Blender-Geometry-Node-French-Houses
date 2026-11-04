import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty
from .assets import generator_modifier, socket
from . import footprints


def binding(name, default):
    def get(self):
        modifier = generator_modifier(self.id_data)
        return socket(modifier, name).value if modifier else default

    def set(self, value):
        obj = self.id_data
        modifier = generator_modifier(obj)
        if modifier:
            socket(modifier, name).value = value
            # Blender 5.2 RNA writes do not themselves invalidate the object.
            obj.update_tag(refresh={'OBJECT', 'DATA'})
    return {'get': get, 'set': set}


class MBGHouseSettings(bpy.types.PropertyGroup):
    shape: EnumProperty(name='Preset', items=footprints.ITEMS,
        get=lambda self: footprints.shape_index(self.id_data),
        set=lambda self, value: footprints.set_shape(self.id_data, value))
    width: FloatProperty(name='Hausbreite (m)', unit='LENGTH', precision=2,
        description='Lokaler Grundriss entlang Y, Front in +X; keine Objektskalierung',
        min=footprints.WIDTH_MIN, max=footprints.WIDTH_MAX,
        get=lambda self: footprints.dimensions(self.id_data)[0],
        set=lambda self, value: footprints.set_dimension(self.id_data, 'width', value))
    depth: FloatProperty(name='Haustiefe (m)', unit='LENGTH', precision=2,
        description='Lokaler Grundriss entlang X, 1 Blender Unit = 1 Meter bei Objektskalierung 1',
        min=footprints.DEPTH_MIN, max=footprints.DEPTH_MAX,
        get=lambda self: footprints.dimensions(self.id_data)[1],
        set=lambda self, value: footprints.set_dimension(self.id_data, 'depth', value))
    seed: IntProperty(name='Seed', min=0, max=1000000, **binding('Seed', 29))
    floors: IntProperty(name='Stockwerke', min=1, max=8, **binding('NumberFloor', 2))
    curvature: FloatProperty(name='Dachkrümmung', min=0, max=3, **binding('RoofCurvature', 1.66))
    roof_color: FloatVectorProperty(name='Dachfarbe', size=4, subtype='COLOR', min=0, max=1,
                                    **binding('RoofColor', (0.48, 0.055, 0.11, 1)))
    paint_color: FloatVectorProperty(name='Putzfarbe', size=4, subtype='COLOR', min=0, max=1,
                                     **binding('PaintColor', (1, 1, 1, 1)))
    beam_color: FloatVectorProperty(name='Balkenfarbe', size=4, subtype='COLOR', min=0, max=1,
                                    **binding('BeamCollor', (0.27, 0.21, 0.22, 1)))
    ivy: BoolProperty(name='Efeu', **binding('SpawnIVY', True))
    high_poly: BoolProperty(name='High-Poly-Pflanzen', **binding('High Polz Plants', True))


class MBGPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    source_file: StringProperty(
        name='IRCSS-Quelldatei', subtype='FILE_PATH',
        description='Unveränderte GeometryNodesFrenchHous.blend mit GenerateHouse und HouseOne',
        default='',
    )

    def draw(self, context):
        self.layout.prop(self, 'source_file')
        self.layout.label(text='Benötigt Blender 5.2; die Quelldatei wird nur gelesen.')


def preferences(context):
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon else None
