"""Test-only GUI setup and command inbox, never part of the extension."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT = Path.cwd()
OUT = ROOT/'tests/addon/phase5'
MODULE = 'bl_ext.mbg_test.medieval_building_generator'
bpy.context.preferences.addons[MODULE].preferences.source_file = str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        space.show_region_ui = True
        space.shading.type = 'MATERIAL'
        space.overlay.show_overlays = False
        space.region_3d.view_rotation = Vector((1.3,-1.7,1.0)).to_track_quat('Z','Y')
        space.region_3d.view_location = (0,0,4)
        space.region_3d.view_distance = 19
        for region in area.regions:
            if region.type == 'UI':
                try: region.active_panel_category = 'Medieval Buildings'
                except Exception: pass
bpy.ops.wm.save_userpref()

def inbox():
    path = OUT/'runtime/gui_command.py'
    if path.exists():
        code = path.read_text()
        path.unlink()
        try:
            exec(compile(code, str(path), 'exec'), globals())
            (OUT/'runtime/gui_done.txt').write_text('OK')
        except Exception:
            import traceback
            (OUT/'runtime/gui_done.txt').write_text(traceback.format_exc())
    return 0.5
bpy.app.timers.register(inbox, first_interval=1)
