"""Real Blender GUI test setup, 0.3.0 installed; no production handlers/inbox."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd();OUT=ROOT/'tests/addon/phase7';M='bl_ext.mbg_variety_test.medieval_building_generator'
namespace={}
code=(ROOT/'scripts/test_addon_variety07.py').read_text()
exec(compile(code[:code.index('bpy.context.preferences.addons[M]')],'variety_test_helpers','exec'),namespace)
signature=namespace['signature'];F=namespace['F'];E=namespace['E']
houses={name:bpy.data.objects[name] for name in ('Compact','Narrow','Wide')}
bpy.context.preferences.addons[M].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
bpy.context.preferences.view.filebrowser_display_type='SCREEN'
win=bpy.context.window
saved_path=Path(bpy.data.filepath)
saved_sha=hashlib.sha256(saved_path.read_bytes()).hexdigest()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.show_region_ui=True;space.shading.type='MATERIAL'
        space.overlay.show_overlays=False
        space.region_3d.view_perspective='ORTHO'


def view(center, distance=22, front=False):
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            region=area.spaces.active.region_3d
            region.view_location=center;region.view_distance=distance
            region.view_rotation=Vector((1,0,.12) if front else (1.3,-1.7,1)).to_track_quat('Z','Y')


def select_house(name,front=False):
    for obj in bpy.context.scene.objects:
        obj.select_set(False);obj.hide_set(obj.name!=name)
    obj=houses[name];obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
    view(obj.location+Vector((0,0,4)),22,front)


def show_all():
    for obj in bpy.context.scene.objects:obj.hide_set(obj.name not in houses)
    view(Vector((12,0,4)),44)


def snapshot_all():
    hidden={o.name:o.hide_get() for o in bpy.context.scene.objects}
    for obj in houses.values():obj.hide_set(False)
    result={name:signature(obj) for name,obj in houses.items()}
    for name,hidden_value in hidden.items():bpy.data.objects[name].hide_set(hidden_value)
    return result


def capture(name):bpy.ops.screen.screenshot(filepath=str(OUT/(name+'.png')))

def sequence(events):
    def advance():
        if not events:return None
        win.event_simulate(**events.pop(0))
        return .13 if events else None
    bpy.app.timers.register(advance,first_interval=.1)

def click(x,top):
    sequence([dict(type='MOUSEMOVE',value='NOTHING',x=x,y=win.height-top),
              dict(type='LEFTMOUSE',value='PRESS',x=x,y=win.height-top),
              dict(type='LEFTMOUSE',value='RELEASE',x=x,y=win.height-top)])

def number(x,top,text):
    y=win.height-top
    events=[dict(type='MOUSEMOVE',value='NOTHING',x=x,y=y),dict(type='LEFTMOUSE',value='PRESS',x=x,y=y,ctrl=True),
            dict(type='LEFTMOUSE',value='RELEASE',x=x,y=y),dict(type='A',value='PRESS',ctrl=True),dict(type='A',value='RELEASE')]
    keys=dict(zip('0123456789.',('ZERO','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','PERIOD')))
    events += [dict(type=keys[c],value='PRESS',unicode=c) for c in text]
    events += [dict(type='RET',value='PRESS'),dict(type='RET',value='RELEASE')]
    sequence(events)

select_house('Compact')
baseline=snapshot_all()

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
