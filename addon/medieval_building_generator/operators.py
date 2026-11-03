import bpy
from .assets import AssetError, create_house
from .properties import preferences


class MBG_OT_create_house(bpy.types.Operator):
    bl_idname = 'mbg.create_house'
    bl_label = '+ Neues Haus erstellen'
    bl_description = 'Eigenständiges Haus aus der IRCSS-Grundrissvorlage erstellen'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        prefs = preferences(context)
        if not prefs or not prefs.source_file:
            self.report({'ERROR'}, 'Bitte zuerst die IRCSS-Quelldatei in den Add-on-Einstellungen auswählen.')
            return {'CANCELLED'}
        try:
            obj = create_house(context, prefs.source_file)
        except AssetError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f'{obj.name} erstellt. Einstellungen im Medieval-Buildings-Panel.')
        return {'FINISHED'}
