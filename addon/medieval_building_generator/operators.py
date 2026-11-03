import os
import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
from .exporter import ExportError, export_house, filename_for, valid_house
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


class MBG_OT_export_house(bpy.types.Operator, ExportHelper):
    bl_idname = 'mbg.export_house'
    bl_label = 'Export Selected House (.glb)'
    bl_description = 'Nur das aktive Haus vollständig und am Grundrissboden zentriert exportieren'
    filename_ext = '.glb'
    filter_glob: StringProperty(default='*.glb', options={'HIDDEN'})
    check_existing: BoolProperty(default=True, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if not valid_house(context, context.active_object):
            cls.poll_message_set('Bitte ein gültiges Add-on-Haus im Object Mode aktiv auswählen.')
            return False
        return True

    def invoke(self, context, event):
        self._target = context.active_object
        self.filepath = os.path.join(bpy.path.abspath('//'), filename_for(self._target))
        self._from_filebrowser = True
        return ExportHelper.invoke(self, context, event)

    def draw(self, context):
        if getattr(self, '_overwrite_dialog', False):
            self.layout.label(text='Vorhandene GLB-Datei wirklich ersetzen?', icon='ERROR')
            self.layout.label(text=os.path.basename(self.filepath))
        # File browser itself has no batch/material/LOD/exporter options.

    def execute(self, context):
        obj = getattr(self, '_target', context.active_object)
        if obj != context.active_object:
            self.report({'ERROR'}, 'Das aktive Haus wurde während der Dateiauswahl geändert. Bitte erneut starten.')
            return {'CANCELLED'}
        if (os.path.exists(bpy.path.abspath(self.filepath))
                and getattr(self, '_from_filebrowser', False)
                and not getattr(self, '_overwrite_dialog', False)):
            # check_existing only warns in some file-selector paths. Never
            # equate opening a file browser with permission to overwrite.
            self._overwrite_dialog = True
            return context.window_manager.invoke_props_dialog(
                self, width=420, title='GLB überschreiben?', confirm_text='Überschreiben')
        try:
            result = export_house(context, obj, self.filepath,
                                  overwrite=getattr(self, '_overwrite_dialog', False))
        except ExportError as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        if result['pivot_method'] != 'input_footprint':
            self.report({'WARNING'}, 'Pivot aus tragenden Basisflächen angenähert; Eingabegrundriss war nicht eindeutig.')
        if result['fallback_materials']:
            self.report({'WARNING'}, 'Unbekannte Materialien wurden braun angenähert: ' + ', '.join(result['fallback_materials']))
        self.report({'INFO'}, f"Haus exportiert: {result['path']} ({result['triangles']:,} Dreiecke). PBR-Farbannäherung, kein Baking.")
        return {'FINISHED'}
