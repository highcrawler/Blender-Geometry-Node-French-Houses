"""Coordinate-specific real-GUI acceptance replay, Blender 5.2, 2560x1440.
Execute after addon_gui_session.py in its test inbox (see installation docs).
Only this test harness uses event_simulate; the extension does not.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector
ROOT = Path.cwd()
OUT = ROOT/'tests/addon/phase5'
MODULE = 'bl_ext.mbg_test.medieval_building_generator'
window = bpy.context.window
assert (window.width, window.height) == (2560,1440)
tasks = []
records = []


def task(fn, delay=0.15):
    tasks.append((fn, delay))


def event(**kwargs):
    task(lambda: window.event_simulate(**kwargs))


def click(x, top):
    y = 1440-top
    event(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    event(type='LEFTMOUSE', value='PRESS', x=x, y=y)
    event(type='LEFTMOUSE', value='RELEASE', x=x, y=y)


def text(x, top, value):
    y = 1440-top
    event(type='MOUSEMOVE', value='NOTHING', x=x,y=y)
    event(type='LEFTMOUSE', value='PRESS', x=x,y=y,ctrl=True)
    event(type='LEFTMOUSE', value='RELEASE', x=x,y=y)
    event(type='A', value='PRESS', ctrl=True)
    event(type='A', value='RELEASE')
    keys = dict(zip('0123456789.', ('ZERO','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE','PERIOD')))
    for char in value:
        event(type=keys.get(char,char.upper()), value='PRESS', unicode=char)
    event(type='RET', value='PRESS')
    event(type='RET', value='RELEASE')


def capture(name):
    task(lambda: None, 3)
    def save():
        bpy.ops.screen.screenshot(filepath=str(OUT/(name+'.png')))
        houses = {}
        for obj in bpy.context.scene.objects:
            if obj.get('mbg_house_version'):
                p = obj.mbg_settings
                houses[obj.name] = dict(seed=p.seed, floors=p.floors, curvature=p.curvature,
                    roof=list(p.roof_color), paint=list(p.paint_color), beam=list(p.beam_color),
                    ivy=p.ivy, high_poly=p.high_poly)
        records.append(dict(screenshot=name+'.png',houses=houses,
                            active=bpy.context.active_object.name if bpy.context.active_object else None))
        (OUT/'gui_actions.json').write_text(json.dumps(records,indent=2))
    task(save)


def setup():
    bpy.context.preferences.addons[MODULE].preferences.source_file = str(ROOT/'GeometryNodesFrenchHous.blend')
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.scene.cursor.location = (0,0,0)
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space = area.spaces.active
            space.show_region_ui = True
            space.shading.type = 'MATERIAL'
            space.overlay.show_overlays = False
            space.region_3d.view_rotation = Vector((1.3,-1.7,1)).to_track_quat('Z','Y')
            space.region_3d.view_location = (0,0,4)
            space.region_3d.view_distance = 19


task(setup,1)
event(type='ESC',value='PRESS')
event(type='ESC',value='RELEASE')
# Tab position depends on Blender's active category; session has already opened it.
capture('gui_empty')
click(1950,173)
capture('gui_house_seed29')
text(1995,256,'83')
capture('gui_house_seed83')
text(1995,284,'3')
capture('gui_floors3')
text(1995,312,'0.5')
capture('gui_curvature05')
for top, hex_top, value, name in [(375,345,'2468BE','gui_roof_blue'),
                                  (403,374,'C99A52','gui_paint_ochre'),
                                  (431,402,'283A24','gui_beams_green')]:
    click(1990,top)
    task(lambda:None,1)
    text(2025,hex_top,value)
    click(1800,600)
    capture(name)
click(1942,494)
capture('gui_ivy_off')
click(1942,522)
capture('gui_plants_off')
for x, seed in [(11,'17'),(22,'56')]:
    task(lambda x=x:setattr(bpy.context.scene.cursor,'location',(x,0,0)))
    click(1950,173)
    task(lambda:None,3)
    text(1995,256,seed)


def frame_three():
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=(11,0,4)
            area.spaces.active.region_3d.view_distance=44

task(frame_three)
capture('gui_three_houses')
click(2260,123)  # Outliner, second house.
text(1995,256,'99')
capture('gui_house2_changed')
task(lambda:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'runtime/gui_three_houses.blend')))


def cycle():
    import addon_utils
    addon_utils.disable(MODULE,default_set=True)
    addon_utils.enable(MODULE,default_set=True)

task(cycle)
capture('gui_reenabled')
click(1950,173)  # Preference is reset on disabling: controlled error.
capture('gui_missing_source')
event(type='ESC',value='PRESS')
event(type='ESC',value='RELEASE')
task(lambda:bpy.ops.mesh.primitive_cube_add(location=(35,0,0)))
capture('gui_foreign_selection')


def finish():
    bpy.data.objects.remove(bpy.context.active_object,do_unlink=True)
    for obj in bpy.context.selected_objects:obj.select_set(False)
    bpy.context.view_layer.objects.active=None
    bpy.context.preferences.addons[MODULE].preferences.source_file=str(ROOT/'GeometryNodesFrenchHous.blend')
    bpy.ops.wm.save_userpref()

task(finish)
capture('gui_no_selection')


def assert_replay():
    states = {r['screenshot']:r for r in records}
    def first(stage):return states[stage+'.png']['houses']['Medieval House']
    assert first('gui_house_seed29')['seed'] == 29
    assert first('gui_house_seed83')['seed'] == 83
    assert first('gui_floors3')['floors'] == 3
    assert abs(first('gui_curvature05')['curvature'] - 0.5) < 1e-5
    for stage, previous, field in [('gui_roof_blue','gui_curvature05','roof'),
                                  ('gui_paint_ochre','gui_roof_blue','paint'),
                                  ('gui_beams_green','gui_paint_ochre','beam')]:
        assert first(stage)[field] != first(previous)[field]
    assert not first('gui_ivy_off')['ivy']
    assert not first('gui_plants_off')['high_poly']
    before = states['gui_three_houses.png']['houses']
    after = states['gui_house2_changed.png']['houses']
    assert len(before) == 3
    assert before['Medieval House'] == after['Medieval House']
    assert before['Medieval House.002'] == after['Medieval House.002']
    assert before['Medieval House.001']['seed'] == 17
    assert after['Medieval House.001']['seed'] == 99
    assert after == states['gui_reenabled.png']['houses']
    assert states['gui_no_selection.png']['active'] is None
    assert states['gui_foreign_selection.png']['active'] not in after
    (OUT/'gui_result.json').write_text(json.dumps({'result':'PASS','real_gui':True,
        'input_method':'Window.event_simulate','screenshots':len(records),
        'all_ui_fields_and_independence_asserted':True},indent=2))

task(assert_replay)


def advance():
    if not tasks:
        (OUT/'runtime/gui_acceptance_done.txt').write_text('PASS: real GUI replay completed')
        return None
    fn, delay = tasks.pop(0)
    try:
        fn()
    except Exception:
        import traceback
        (OUT/'runtime/gui_acceptance_done.txt').write_text(traceback.format_exc())
        return None
    return delay

bpy.app.timers.register(advance,first_interval=1)
