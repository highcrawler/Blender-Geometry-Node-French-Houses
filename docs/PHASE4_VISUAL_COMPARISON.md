# Phase 4 – tatsächlicher Bildvergleich

Alle Bilder sind echte Blender-Cycles-Renderings beziehungsweise Screenshots eines grafischen Godot-OpenGL-Prozesses. Kein Headless-Bildvergleich, keine generierten Illustrationen. Die Vergleichstafeln werden mit Pillow aus diesen PNGs zusammengesetzt.

| Ansicht | Originalshader auf Exportmesh | Phase 3 | Phase 4 Blender | Phase 4 Godot |
|---|---|---|---|---|
| Iso | [Bild](../tests/baking/phase4/blender_original_iso.png) | [Bild](../tests/baking/phase4/blender_phase3_iso.png) | [Bild](../tests/baking/phase4/blender_phase4_iso.png) | [Bild](../tests/baking/phase4/godot_pbr_iso.png) |
| Front | [Bild](../tests/baking/phase4/blender_original_front.png) | [Bild](../tests/baking/phase4/blender_phase3_front.png) | [Bild](../tests/baking/phase4/blender_phase4_front.png) | [Bild](../tests/baking/phase4/godot_pbr_front.png) |
| Fassade | [Bild](../tests/baking/phase4/blender_original_facade.png) | [Bild](../tests/baking/phase4/blender_phase3_facade.png) | [Bild](../tests/baking/phase4/blender_phase4_facade.png) | [Bild](../tests/baking/phase4/godot_pbr_facade.png) |

Direkte Vierertafeln, Reihenfolge wie oben: [Iso](../tests/baking/phase4/comparison_iso.png), [Front](../tests/baking/phase4/comparison_front.png), [Nahaufnahme](../tests/baking/phase4/comparison_facade.png).

## Vergleichsbedingungen

Blender verwendet dasselbe ausgewertete Mesh mit unveränderten lokalen Positionen und Materialindizes, 960×720, Cycles CPU, 16 Samples, Denoising, Seed 0, AgX. Kamera/Licht entsprechen Phase 3: Iso `(12,-15,12) → (0,0,3.7)`, Front `(16,0,5.2) → (0,0,3.7)`, Fassade `(11,-5,4.8) → (0,-0.4,4.2)`; ortho_scale 15/12/6. Area-Licht 1800 W/9 m bei `(2,-3,12)`, Weltstärke 0,8. Drei Materialzustände: originale Shader, fünf Phase-3-Konstanten, dieselben Konstanten mit gebackenem Putz.

Godot verwendet dieselben entsprechend transformierten Kamerapositionen und Blickziele, Sun 0,65 und Ambient 0,35 wie Phase 3. Für identischen Bildausschnitt wird Godots vertikale Kameragröße mit 720/960 aus Blenders horizontaler ortho_scale berechnet. Dieser Ausschnitt ist genauer abgeglichen als die früheren Phase-3-Godot-Bilder. Lichtmodell und Tonemapping bleiben verschieden; pixelgleiche Helligkeit wird nicht behauptet.

## Putz unabhängig vom übrigen Haus

- **Schadensposition/Form:** Der große freigelegte Ziegelbereich über beide Stockwerke, die schmale linke Schadensstelle und kleinere Flecken erscheinen in Blender-Bake und Godot an denselben Stellen wie im Originalshader auf dem Exportmesh. Es wurde keine Ersatzmaske entworfen.
- **Farbdetails:** Grauer Putz, fleckige Variation, braune Mauerwerksbereiche und wechselnde Ziegelfarben sind vorhanden. Phase 3 zeigt dort nur eine helle homogene Fläche. Der visuelle Gewinn ist deutlich.
- **Verlust:** Die Nahaufnahme zeigt weichere Details und fehlendes Fugen-/Kantenrelief. Ein Teil dieses Reliefs kam aus `Normal`/Bump, nicht aus Base Color. Der 1024²-Atlas begrenzt zusätzlich die Detailauflösung. Kein Normal-Bake in dieser Phase.
- **Nähte:** In den drei getesteten Ansichten keine auffälligen schwarzen UV-Nähte oder verschobenen Farbstreifen. Keine Garantie für jede verdeckte Fläche, jede Entfernung und alle Mip-Stufen.
- **Farbraum:** PNG als sRGB, im GLB ausschließlich als Base-Color-Textur, Godot-Albedo-Multiplikator Weiß. Godot importiert die Textur mit Mipmaps, ohne Normal-Map-Behandlung oder manuelle Farbänderung. Der dunklere Putz gegenüber Phase 3 entspricht dem originalen Shader inklusive Faktor 0,25. Unterschiede in Beleuchtung bleiben sichtbar; kein Hinweis auf einen groben sRGB-/Linear-Fehler. Kein nachträgliches Angleichen der Materialfarbe.
- **Gesamthaus:** Dach, Holz und Naturstein sind weiterhin die einfachen Phase-3-Materialien. Insbesondere helles Holz bleibt vom Original verschieden und darf die Bewertung des Putz-Bakes nicht ersetzen.

## Grenze zum vollständigen GN-Original

Zusätzliche Kontrollbilder: [GN Iso](../tests/baking/phase4/blender_gn_control_iso.png), [GN Front](../tests/baking/phase4/blender_gn_control_front.png), [GN Fassade](../tests/baking/phase4/blender_gn_control_facade.png). Diese enthalten GN-Instanzdetails, die bereits dem Phase-3-Mesh fehlen. Auch die Schadensverteilung ist gegenüber der ausgewerteten Meshkopie nicht identisch abgesichert. Daher kein PASS für eine vollständige Übertragung des ursprünglichen GN-Hauses. Details in [Baking-Audit](PHASE4_BAKING_AUDIT.md).

Godot-Beleg: [godot_capture.log](../tests/baking/phase4/godot_capture.log), echte NVIDIA/OpenGL-3-Ausgabe, ein Mesh, fünf Surfaces, 50.944 Dreiecke, Putz-Albedo 1024². Der Headless-Editor-Import meldete Sandbox-Fehler beim Editor-Konfigurationsspeichern und lokalen Socket; der Assetimport und anschließende grafische Lauf funktionierten. Keine material- oder texturspezifische Importwarnung im protokollierten Lauf. Blender meldet API-Deprecations und einen Audiozugriffsfehler beim Prozessende; die geprüften Render-/Bake-/GLB-Ergebnisse wurden zuvor erfolgreich geschrieben.
