import bpy
from .assets import HOUSE_TAG, AssetError, generator_modifier, socket
from .properties import preferences
from .exporter import valid_house
from . import footprints


class MBG_PT_buildings(bpy.types.Panel):
    bl_label = 'Medieval Building Generator'
    bl_idname = 'MBG_PT_buildings'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Medieval Buildings'

    def draw(self, context):
        layout = self.layout
        prefs = preferences(context)
        layout.label(text='Gebäude', icon='HOME')
        if prefs:
            layout.prop(prefs, 'source_file', text='Quelle')
        layout.operator('mbg.create_house', icon='ADD')
        obj = context.active_object
        if not obj or not obj.get(HOUSE_TAG):
            layout.label(text='Ein erzeugtes Haus auswählen.', icon='INFO')
            return
        layout.label(text=obj.name, icon='OUTLINER_OB_MESH')
        modifier = generator_modifier(obj)
        if not modifier:
            layout.label(text='GenerateHouse-Modifier fehlt.', icon='ERROR')
            return
        layout.use_property_split = True
        layout.use_property_decorate = False
        shape = layout.box()
        shape.label(text='Building Shape')
        controls = shape.column()
        controls.enabled = valid_house(context, obj) and footprints.controlled(obj)
        controls.prop(obj.mbg_settings, 'shape')
        controls.label(text='Building Dimensions')
        controls.prop(obj.mbg_settings, 'width')
        controls.prop(obj.mbg_settings, 'depth')
        if not footprints.controlled(obj):
            shape.label(text='Bestehender Grundriss bleibt unverändert.', icon='INFO')
            shape.operator('mbg.activate_rectangle')
        if any(abs(v-1) > 1e-5 for v in obj.scale):
            shape.label(text='Lokale Maße; Objektskalierung wirkt zusätzlich.', icon='INFO')
        sections = (
            ('Building Settings', (('Seed', 'seed'), ('NumberFloor', 'floors'),
                                ('RoofCurvature', 'curvature'))),
            ('Appearance', (('RoofColor', 'roof_color'), ('PaintColor', 'paint_color'),
                                ('BeamCollor', 'beam_color'))),
            ('Details', (('SpawnIVY', 'ivy'), ('High Polz Plants', 'high_poly'))),
        )
        for title, fields in sections:
            box = layout.box()
            box.label(text=title)
            for name, prop in fields:
                try:
                    socket(modifier, name)  # Validate before drawing the proxy.
                    box.prop(obj.mbg_settings, prop)
                except AssetError as exc:
                    box.label(text=str(exc), icon='ERROR')
        box = layout.box()
        box.label(text='Export', icon='EXPORT')
        row = box.row()
        row.enabled = valid_house(context, obj)
        row.operator('mbg.export_house', icon='EXPORT')
