"""Headless parameter and deterministic replay checks; no source blend is loaded."""
import bpy, sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cottage import Cottage, generate

def signature(coll):
    bpy.context.view_layer.update()
    h=hashlib.sha256()
    for obj in coll.objects:
        for v in obj.data.vertices:
            h.update(repr(tuple(round(x,6) for x in obj.matrix_world @ v.co)).encode())
    return h.hexdigest()

base=Cottage()
a,_=generate(base,'reference')
b,_=generate(base,'again')
assert signature(a)==signature(b),'Seed replay differs'
base_hash=signature(a)
for label,kwargs in [('width',{'width':6}),('depth',{'depth':5}),('wall',{'wall_height':2.8}),
                     ('pitch',{'roof_pitch':55}),('seed',{'seed':2})]:
    obj,_=generate(Cottage(**kwargs),label)
    assert signature(obj)!=base_hash, label
    print('COTTAGE_PARAMETER_PASS',label)
for bad in (Cottage(width=0),Cottage(depth=1),Cottage(wall_height=4),Cottage(roof_pitch=85),Cottage(seed=-1)):
    try: generate(bad,'invalid')
    except ValueError: pass
    else: raise AssertionError('Invalid parameters accepted')
print('COTTAGE_TEST_PASS replay + five inputs + five invalid cases')
