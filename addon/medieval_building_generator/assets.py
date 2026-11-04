"""Append only HouseOne and Blender-resolved dependencies, never the demo scene."""
from pathlib import Path
import bpy

TEMPLATE_TAG = 'mbg_template_source'
HOUSE_TAG = 'mbg_house_version'
REQUIRED = {
    'Object': 'NodeSocketObject', 'Seed': 'NodeSocketInt',
    'NumberFloor': 'NodeSocketInt', 'RoofCurvature': 'NodeSocketFloat',
    'RoofColor': 'NodeSocketColor', 'PaintColor': 'NodeSocketColor',
    'BeamCollor': 'NodeSocketColor', 'SpawnIVY': 'NodeSocketBool',
    'High Polz Plants': 'NodeSocketBool',
}


class AssetError(RuntimeError):
    pass


def generator_modifier(obj):
    if obj:
        for modifier in obj.modifiers:
            if modifier.type == 'NODES' and modifier.node_group:
                # Identification is based on the interface, not a renamed group name.
                names = {s.name for s in modifier.node_group.interface.items_tree
                         if s.item_type == 'SOCKET' and s.in_out == 'INPUT'}
                if REQUIRED.keys() <= names:
                    return modifier
    return None


def socket(modifier, name):
    matches = [s for s in modifier.node_group.interface.items_tree
               if s.item_type == 'SOCKET' and s.in_out == 'INPUT' and s.name == name]
    if len(matches) != 1:
        raise AssetError(f'GenerateHouse: Eingang {name!r} fehlt oder ist mehrdeutig.')
    item = matches[0]
    if item.socket_type != REQUIRED[name]:
        raise AssetError(f'GenerateHouse: Unerwarteter Typ für {name}.')
    try:
        value = getattr(modifier.properties.inputs, item.identifier)
        value.value
        return value
    except AttributeError as exc:
        raise AssetError('Blender-5.2-RNA-Eingabeschnittstelle nicht verfügbar.') from exc


def validate(template):
    modifier = generator_modifier(template)
    if not modifier or not modifier.node_group.name.startswith('GenerateHouse'):
        raise AssetError('HouseOne besitzt keinen kompatiblen GenerateHouse-Modifier.')
    for name in REQUIRED:
        socket(modifier, name)
    if template.type != 'MESH':
        raise AssetError('HouseOne muss ein Mesh-Grundriss sein.')
    return modifier


def load_template(source):
    path = Path(bpy.path.abspath(source)).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() != '.blend':
        raise AssetError('Bitte eine vorhandene IRCSS-Quelldatei (.blend) auswählen.')
    # A source must never be overwritten by a subsequent normal Save operation.
    if bpy.data.filepath and Path(bpy.data.filepath).resolve() == path:
        raise AssetError('Bitte eine neue Szene öffnen, nicht in der IRCSS-Quelldatei arbeiten.')
    key = str(path)
    for obj in bpy.data.objects:
        if obj.get(TEMPLATE_TAG) == key:
            validate(obj)
            return obj
    before = {name: set(getattr(bpy.data, name)) for name in
              ('objects', 'collections', 'meshes', 'node_groups', 'materials', 'images', 'curves')}
    try:
        with bpy.data.libraries.load(str(path), link=False) as (available, requested):
            if 'GenerateHouse' not in available.node_groups:
                raise AssetError('Quelldatei enthält die Node-Gruppe GenerateHouse nicht.')
            if 'HouseOne' not in available.objects:
                raise AssetError('Quelldatei enthält die benötigte HouseOne-Grundrissvorlage nicht.')
            requested.objects = ['HouseOne']
        template = requested.objects[0]
        validate(template)
        template[TEMPLATE_TAG] = key
        template.use_fake_user = True
        # Dependencies stay local and unlinked from the scene. Blender resolves
        # Collection/Object Info references without displaying their source assets.
        for name in ('images',):
            for image in set(getattr(bpy.data, name)) - before[name]:
                if image.source == 'FILE' and not image.packed_file:
                    image.pack()
        return template
    except Exception as exc:
        # Only remove data introduced by this failed append; never user data.
        added = [data for name, old in before.items()
                 for data in set(getattr(bpy.data, name)) - old]
        if added:
            bpy.data.batch_remove(added)
        if isinstance(exc, AssetError):
            raise
        raise AssetError(f'IRCSS-Assets konnten nicht geladen werden: {exc}') from exc


def create_house(context, source):
    template = load_template(source)
    obj = template.copy()
    obj.data = bpy.data.meshes.new('Medieval Rectangle Footprint')
    obj.use_fake_user = False
    if TEMPLATE_TAG in obj:
        del obj[TEMPLATE_TAG]
    obj[HOUSE_TAG] = 1
    obj.name = 'Medieval House'
    obj.data.name = obj.name + ' Footprint'
    context.collection.objects.link(obj)
    obj.location = context.scene.cursor.location
    # The original Object input points to HouseOne: essential for position seeds.
    socket(validate(obj), 'Object').value = obj
    from .footprints import initialize
    initialize(obj)
    for selected in context.selected_objects:
        selected.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj
    obj.update_tag()
    return obj
