"""Real GUI acceptance replay. Requires addon_export06_gui.py, 2560x1440.
File-browser destination is set via its API as fixture; actual buttons, cancel and
explicit overwrite confirmation are exercised with Blender GUI events.
"""
import hashlib
win=bpy.context.window
assert (win.width,win.height)==(2560,1440)
steps=[]

def step(fn,delay=.2):steps.append((fn,delay))
def pause(seconds):step(lambda:None,seconds)
def key(kind):
    step(lambda:win.event_simulate(type=kind,value='PRESS'))
    step(lambda:win.event_simulate(type=kind,value='RELEASE'))
def ui_click(x,y):
    step(lambda:click(win,x,y),1)
def screenshot(name):step(lambda:capture(name))
def source_unchanged():
    assert state()==initial
    assert hashlib.sha256((OUT/'runtime/library.blend').read_bytes()).hexdigest()==source_sha

def destination():
    for area in bpy.context.screen.areas:
        if area.type=='FILE_BROWSER':
            assert area.spaces.active.params.filename=='Renamed_Castle_03.glb'
            area.spaces.active.params.directory=(str(OUT)+'/').encode()

def confirm_exported():
    source_unchanged()
    blob=(OUT/'Renamed_Castle_03.glb').read_bytes()
    assert hashlib.sha256(blob).hexdigest()==json.loads((OUT/'integration.json').read_text())['exports']['house3']['glb_sha256']

def sentinel():
    (OUT/'runtime/Renamed_Castle_03.glb').write_bytes(b'SENTINEL: explicit overwrite confirmation required')

def still_sentinel():
    source_unchanged()
    assert (OUT/'runtime/Renamed_Castle_03.glb').read_bytes()==b'SENTINEL: explicit overwrite confirmation required'

# Initial scene uses deliberately six selected objects (five houses plus a cube).
key('ESC')
ui_click(2090,310)
pause(2)
screenshot('blender_export_panel')
ui_click(1950,585)
screenshot('blender_file_dialog')
ui_click(2350,1398)  # cancel file browser
step(source_unchanged)
ui_click(1950,585)
step(destination,1)
screenshot('blender_file_destination')
ui_click(2480,1398)
pause(3)
step(confirm_exported)
screenshot('blender_after_export')
step(sentinel)
ui_click(1950,585)  # initial runtime directory contains the sentinel
ui_click(2480,1398)
pause(1)
screenshot('blender_overwrite_confirmation')
step(still_sentinel)
key('ESC')  # Cancel the explicit overwrite popup
pause(1)
step(still_sentinel)
ui_click(1950,585)
ui_click(2480,1398)
pause(1)
step(still_sentinel)
key('RET')  # Explicitly accept the overwrite popup
pause(3)

def finish():
    source_unchanged()
    expected=json.loads((OUT/'integration.json').read_text())['exports']['house3']['glb_sha256']
    actual=hashlib.sha256((OUT/'runtime/Renamed_Castle_03.glb').read_bytes()).hexdigest()
    assert actual==expected
    result=dict(result='PASS',real_gui=True,method='Window.event_simulate',
        file_dialog=True,sanitized_filename='Renamed_Castle_03.glb',cancel_unchanged=True,
        explicit_overwrite_popup=True,overwrite_cancel_preserved_sentinel=True,
        overwrite_confirmed=True,original_scene_unchanged=True,saved_blend_sha256=source_sha,
        exported_sha256=actual,selected_objects=len(initial['selected']),active=initial['active'])
    (OUT/'gui_result.json').write_text(json.dumps(result,indent=2))
    capture('blender_final')
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=(12,-3,4)
            area.spaces.active.region_3d.view_distance=130

step(finish,3)
screenshot('blender_five_houses_unchanged')

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
