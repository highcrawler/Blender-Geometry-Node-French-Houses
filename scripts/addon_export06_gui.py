"""Real Blender GUI test session, installed 0.2.0, saved five-house library."""
import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd(); OUT=ROOT/'tests/addon/phase6'
MODULE='bl_ext.mbg_export_test.medieval_building_generator'
bpy.context.preferences.addons[MODULE].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active
        space.show_region_ui=True
        space.shading.type='MATERIAL'
        space.overlay.show_overlays=False
        space.region_3d.view_rotation=Vector((1.3,-1.7,1)).to_track_quat('Z','Y')
        space.region_3d.view_location=(40,15,4)
        space.region_3d.view_distance=22
# Keep file browser in the main window to make coordinate-specific replay explicit.
bpy.context.preferences.view.filebrowser_display_type='SCREEN'
helpers={}
code=(ROOT/'scripts/test_addon_export06.py').read_text()
exec(compile(code[:code.index('# Source is never opened')],'export06_helpers','exec'),helpers)
state=helpers['state']
initial=state()
source_sha=__import__('hashlib').sha256((OUT/'runtime/library.blend').read_bytes()).hexdigest()

def click(window,x,top):
    events=[dict(type='MOUSEMOVE',value='NOTHING',x=x,y=window.height-top),
            dict(type='LEFTMOUSE',value='PRESS',x=x,y=window.height-top),
            dict(type='LEFTMOUSE',value='RELEASE',x=x,y=window.height-top)]
    def advance():
        if not events:return None
        window.event_simulate(**events.pop(0))
        return .15 if events else None
    bpy.app.timers.register(advance,first_interval=.1)

def capture(name):
    bpy.ops.screen.screenshot(filepath=str(OUT/(name+'.png')))

def inbox():
    path=OUT/'runtime/gui_command.py'
    if path.exists():
        code=path.read_text();path.unlink()
        try:
            exec(compile(code,str(path),'exec'),globals())
            (OUT/'runtime/gui_done.txt').write_text('OK')
        except Exception:
            import traceback
            (OUT/'runtime/gui_done.txt').write_text(traceback.format_exc())
    return .5
bpy.app.timers.register(inbox,first_interval=1)
