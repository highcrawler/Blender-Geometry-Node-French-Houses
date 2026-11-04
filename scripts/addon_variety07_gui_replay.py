"""Real GUI replay for a fresh addon_variety07_gui.py session at 2560x1440.
The actual fields/buttons are clicked. Only view, fixture visibility and browser
output-path setup use the test API. Not included in the installable extension.
"""
import time
assert (win.width,win.height)==(2560,1440)
steps=[];check={}
def task(fn,delay=.2):steps.append((fn,delay))
def pause(delay):task(lambda:None,delay)
def ui_click(x,y):task(lambda:click(x,y),1)
def ui_number(x,y,value):task(lambda:number(x,y,value),2.5)
def shot(name):pause(1.5);task(lambda:capture(name))

# Setup already selected Compact; tab position is the standard 2560x1440 layout.
task(lambda:win.event_simulate(type='ESC',value='PRESS'))
task(lambda:win.event_simulate(type='ESC',value='RELEASE'))
ui_click(2090,310)
for name in ('Compact','Narrow','Wide'):
    task(lambda name=name:select_house(name))
    shot('blender_'+name.lower())
task(show_all);shot('blender_three_presets')
for name in ('Compact','Narrow','Wide'):
    task(lambda name=name:select_house(name,front=True))
    shot('blender_'+name.lower()+'_front')

def hide_originals():
    for obj in houses.values():obj.hide_set(True)
    view(bpy.context.scene.cursor.location+Vector((0,0,4)),22)
task(hide_originals)
ui_click(1950,173)
def remember_new():
    obj=bpy.context.active_object
    assert F.controlled(obj) and obj.mbg_settings.shape=='COMPACT'
    check['new']=obj;check['new_values']=signature(obj)['values']
task(remember_new);shot('blender_new_house')
ui_click(1990,256);shot('blender_shape_menu');ui_click(1990,300)
shot('blender_new_house_preset_narrow')
def check_new():
    obj=check['new']
    assert obj.mbg_settings.shape=='NARROW' and abs(obj.mbg_settings.width-3.2)<1e-5 and obj.mbg_settings.depth==5
    assert signature(obj)['values']==check['new_values']
    mesh=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
    if mesh.users==0:bpy.data.meshes.remove(mesh)
    select_house('Narrow');check['before']=snapshot_all()
task(check_new);shot('blender_width_before')
ui_number(1995,300,'4.4');shot('blender_width_after')
ui_number(1995,322,'4.5');shot('blender_depth_after')
ui_number(1995,385,'83');ui_number(1995,412,'3');shot('blender_custom_settings')
def check_custom():
    obj=houses['Narrow'];after=snapshot_all()
    assert after['Compact']==check['before']['Compact'] and after['Wide']==check['before']['Wide']
    assert obj.mbg_settings.shape=='CUSTOM' and abs(obj.mbg_settings.width-4.4)<1e-5 and obj.mbg_settings.depth==4.5
    assert obj.mbg_settings.seed==83 and obj.mbg_settings.floors==3 and tuple(obj.scale)==(1,1,1)
    check['export_before']=signature(obj)
task(check_custom)
ui_click(1950,713);shot('blender_export_dialog')
def browser_target():
    name='gui_replay_'+str(time.time_ns())+'.glb'
    check['output']=OUT/'runtime'/name
    for area in bpy.context.screen.areas:
        if area.type=='FILE_BROWSER':
            area.spaces.active.params.filename=name
            area.spaces.active.params.directory=(str(OUT/'runtime')+'/').encode()
task(browser_target,1)
ui_click(2480,1398);pause(3)
def finish():
    obj=houses['Narrow']
    assert signature(obj)==check['export_before']
    assert hashlib.sha256(saved_path.read_bytes()).hexdigest()==saved_sha
    gltf,read=namespace['helpers']['decode_glb'](check['output'])
    triangles=sum(len(read(p['indices']))//3 for p in gltf['meshes'][0]['primitives'])
    assert len(gltf['meshes'])==1 and triangles==check['export_before']['triangles']
    (OUT/'gui_result.json').write_text(json.dumps(dict(result='PASS',real_gui=True,input_method='Window.event_simulate',
        new_house_button=True,preset_dropdown=True,preset_keeps_generator_values=True,width_field_live=True,
        depth_field_live=True,custom_state_visible=True,seed_field=True,floors_field=True,
        other_two_houses_identical=True,no_object_scaling=True,original_blend_file_unchanged=True,
        export_button_and_file_dialog=True,gui_export_triangles=triangles,custom_width=obj.mbg_settings.width,
        custom_depth=obj.mbg_settings.depth,saved_file_sha256=saved_sha),indent=2))
    capture('blender_after_gui_export')
task(finish)
def advance():
    if not steps:
        (OUT/'runtime/gui_replay_done.txt').write_text('PASS')
        return None
    fn,delay=steps.pop(0)
    try:fn()
    except Exception:
        import traceback
        (OUT/'runtime/gui_replay_done.txt').write_text(traceback.format_exc())
        return None
    return delay
bpy.app.timers.register(advance,first_interval=1)
