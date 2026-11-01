"""Read-only mesh counts for HouseOne's existing plant switches; does not save assets."""
import bpy
obj = bpy.data.objects['HouseOne']
mod = next(m for m in obj.modifiers if m.type == 'NODES')
inputs = mod.properties.inputs
assert (inputs.Socket_12.value, inputs.Socket_14.value) == (True, True)
for ivy, high in ((True, True), (True, False), (False, True), (False, False)):
    inputs.Socket_12.value, inputs.Socket_14.value = ivy, high
    obj.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    per_material = {}
    for polygon in mesh.polygons:
        name = mesh.materials[polygon.material_index].name
        per_material[name] = per_material.get(name, 0) + len(polygon.vertices) - 2
    print('TOGGLE_PROBE', ivy, high, len(mesh.vertices), len(mesh.polygons), sum(per_material.values()), per_material)
    evaluated.to_mesh_clear()
