"""Medieval Building Generator — UI for the unmodified IRCSS GenerateHouse."""
import bpy
from . import properties, operators, ui

CLASSES = (properties.MBGPreferences, properties.MBGHouseSettings,
           operators.MBG_OT_create_house, ui.MBG_PT_buildings)


def register():
    for cls in CLASSES:
        if not cls.is_registered:
            bpy.utils.register_class(cls)
    if not hasattr(bpy.types.Object, 'mbg_settings'):
        bpy.types.Object.mbg_settings = bpy.props.PointerProperty(type=properties.MBGHouseSettings)


def unregister():
    if hasattr(bpy.types.Object, 'mbg_settings'):
        del bpy.types.Object.mbg_settings
    for cls in reversed(CLASSES):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
