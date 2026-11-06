# Phase 9G reproduction (Blender 5.2.2 LTS)

From the repository root:

```sh
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend \
  -P experiments/cottage_geometry_collector_09g/verify.py
blender -b -t 4 experiments/wooden_roof_system_09f/three_owned_cottages.blend \
  -P experiments/wooden_roof_system_09f/reopen.py
```

The first command prints `09G_PASS` and writes [`collection_results.json`](collection_results.json), containing A/B/C per-object matrices, slots, material IDs, polygon and triangle counts, pivot matrices and negative/read-only outcomes. Blender pointer IDs are diagnostics **for that invocation only**; before/after SHA equality is also only meaningful within one process. The script loads the saved 9F scene, verifies it before/after collection and uses disposable temporary scenes for failures. It does not save a `.blend` or create GLBs. The second command independently reopens and checks all 9F saved mesh fingerprints, shader slots, parent/collection links and root transforms; its output remains the frozen 9F `reopen_result.json` (identical content). The original 9F golden meshes and scripts are not changed. No add-on or export writer is loaded.
