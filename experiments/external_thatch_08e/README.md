# 08E – 3D Tudor Example Showcase: inventarisiert, nicht integriert

Benutzerbereitgestelltes `Blender 4 Hay Roofs Geometry Node Showcase.blend`: **privat und außerhalb dieses Git-Worktrees** aufbewahren; das Original wurde unverändert gelassen. Prüfsumme und Messwerte: [`inspection.json`](inspection.json). Der Blender-4.1.24-Showcase lädt in Blender 5.2.2, enthält aber **keine** Node-Gruppe und **keinen** Geometry-Nodes-Modifikator. Sein statisches `HayRoof` mit 460.000 Dreiecken ist kein austauschbarer Dachgenerator. Keine EXTERNAL-Cottage und keine externen Bilder erfunden. [Asset-/Lizenzprüfung](../../docs/PHASE8E_EXTERNAL_ASSET_AUDIT.md) · [Kompatibilität](../../docs/PHASE8E_BLENDER_COMPATIBILITY.md) · [visueller Status](../../docs/PHASE8E_VISUAL_COMPARISON.md) · [Resultat](../../docs/PHASE8E_RESULT.md).

Inventar reproduzieren, wenn ein rechtmäßig lokales Showcase verfügbar ist (Blender 5.2.2, keine Speicherung des geöffneten Assets):

```sh
SHOWCASE_BLEND="$HOME/private-assets/3d-tudor/showcase-original.blend"
blender -b "$SHOWCASE_BLEND" -t 4 -P experiments/external_thatch_08e/inspect_showcase.py
```

Das Skript enthält **nur eigene Logik**, schreibt allein selbst erhobene Metadaten in `inspection.json` und druckt `08E_INSPECTION_COMPLETE` (dieser Marker bedeutet **nicht** erfolgreiche Generator-Integration). Externe Originalassets, Filme, Materialien, Nodes oder Screenshots werden nicht committed. Keine eigene Strohdach-Ersatztechnik.
