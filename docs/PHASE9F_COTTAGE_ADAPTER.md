# Phase 9F – first caller: existing Cottage

The small [`experiments/wooden_roof_system_09f/cottage_adapter.py`](../experiments/wooden_roof_system_09f/cottage_adapter.py) imports the **unchanged** historical `Cottage, generate` and the new `roof.wooden_rect`. `build_cottage(p, name, appearance, location=(0,0,0), yaw=0)` validates inputs and creates the old Cottage at **zero offset** with `refine_eave=False`. It removes only its historical `role='roof'` thatch objects and unused roof materials; walls, timber, door, base, their meshes and material slots remain untouched. The existing generated collection becomes the house-exclusive collection. A new `EMPTY` at local `(0,0,0)` is linked to it, the new roof module builds its own child collection, and the original body objects are parented to the same root. **Only then** is the root moved/rotated. Thus body and roof share the original ground-centered local coordinates; no legacy per-object offset is applied a second time. Failed adapter construction cleans only the newly created house, never another owner's objects/materials.

The resulting Blender ownership is:

```text
Building collection (one house, linked to scene)
  Building_Root (EMPTY, ground pivot, transform owner)
    original Cottage body MESH objects (in building collection)
    Wooden_Roof child collection: exactly 5 roof MESH objects
      2 decks + 1 shingle field + 2 ridge caps (all parented to root)
```

A Collection is not itself a transform/parent; each mesh is explicitly parented to its own building root, and Blender object/collection pointers, not names, identify its owner. `CottageBuild` exposes root, house collection, original body object tuple and `RoofResult`. All 16 Cottage body SHA-256 fingerprints equal their Phase-9D reference values, including at the identity root. Roof parts are owned by the same root but no object/mesh/material is linked into a different house's collection.

[Saved three-house scene](../experiments/wooden_roof_system_09f/three_owned_cottages.blend) · [Blender overview](../experiments/wooden_roof_system_09f/screenshots/three_owned_cottages.png) · [owner measurements](../experiments/wooden_roof_system_09f/ownership.json). A is Long/CLEAN at `(0,0,0)`/yaw 0, B is Compact/AGED at `(35,12,0)`/yaw 0, C is Long/AGED seed 29 at `(-15,8,0)`/yaw 0.45 radians. A seed-29 identity-root probe and C produce identical roof **and body** local hashes. B's root position and one roof material were temporarily changed while all material shaders, meshes and transforms of A/C stayed identical; B was restored before saving. Generating B before A also preserves the same historical hashes. The saved `.blend` was reopened in Blender 5.2.2 and independently verified for all roots, positions, yaw, parent/collection links, private mesh/material IDs, shaders, face-slot assignments and mesh hashes: [reopen evidence](../experiments/wooden_roof_system_09f/reopen_result.json).

The Phase-6 selected-house GLB exporter currently demands an IRCSS/GN active object and `parent.original` instance ownership; these plain Cottage mesh collections **cannot yet** be fed to that exporter. The per-house root and owned child collection make a separately specified, later single-house export adapter feasible while preserving the ground pivot; no GLB/export code is added here.
