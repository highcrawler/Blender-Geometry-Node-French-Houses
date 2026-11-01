import bpy, json
n=bpy.data.node_groups['GenerateHouse']
for f in n.nodes:
    if f.type=='FRAME':
        print('FRAME',repr(f.label),repr(f.name),sum(x.parent==f for x in n.nodes))
for node in n.nodes:
    if node.type=='GROUP' and node.node_tree and ('Roof' in node.node_tree.name or 'Seed' in node.node_tree.name):
        print('GROUP_USE',node.node_tree.name,node.label)
for o in bpy.data.objects:
    if o.name in ('HouseOne','HouseTWo','HouseThree'):
        mod=o.modifiers[0]
        try: print('VALUES',o.name,[(i.name, str(mod.get(i.identifier, 'default'))) for i in n.interface.items_tree if i.item_type=='SOCKET' and i.in_out=='INPUT'])
        except Exception as e: print('VALUES_ERROR',str(e))
