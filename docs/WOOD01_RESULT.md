# WOOD-01 – Medieval Weathered Beam Material Test

**TECHNICAL RESULT: PASS.** **ARTISTIC RESULT: A BEST.** **INTEGRATION RESULT: NOT READY.**

Ausgangsbranch `experiment/stone-door-export-09k`, Commit `a4a59f3`; neuer Branch `experiment/medieval-wood-beam-01` **ohne Merge** im einzigen Checkout. Ursprünglich sauberer Git-Status. Keine gesicherten Altdateien restauriert, keine Generator-/Roof-/Exporteränderung. Ausschließlich `experiments/wood_beam_material_01/` und `docs/WOOD01_*.md` gehören zum Ergebnis.

- **A Baseline:** byteidentisches 9K-GLB mit konstantem Weathered Oak, 783.288 Bytes.
- **B Rough Wood:** originale 1K-Diffuse/Normal-GL/Rough-Maps von [Poly Haven](https://polyhaven.com/a/rough_wood) (CC0, Rob Tuytel), isoliert auf 16 Kopien echter Fachwerkbalken (senkrecht, waagerecht, diagonal). GLB 3.964.744 Bytes. Godot importiert alle drei Maps korrekt, aber Foto-Plankenfugen und Querstoß plus graue Farbe passen nicht zum Massivbalken/warmen Cottage.
- **C Minimal Procedural:** `UV → Wave Bands(X) → ColorRamp → Emission`, per Blender Cycles **512×512 EMIT gebacken**, PNG in neue Principled-Albedo und per nativem GLB-Exporter importiert. GLB 1.021.584 Bytes. Entlang lokaler Balkenachse korrekt ausgerichtet, aber in Spielentfernung fast unsichtbar; Streifen im Detail zu gleichförmig. Kein Normal-/Roughness-Bake.

Die [UV- und Texturprüfung](WOOD01_UV_TEXTURE_AUDIT.md) misst für jeden der 16 Balken lokale Länge, Welt-Längsrichtung und UV-V-Span: keine verkehrte Ausrichtung auf senkrechten, waagerechten oder diagonalen Seitenflächen; Längsmaßstab 1,5 m/Repeat, jedoch ungleichmäßige Querdichte, Wiederholungen und problematische Kappen/Seams. [Blender-/Godot-Vergleichsbilder](WOOD01_GODOT_VISUAL_TEST.md) inklusive [Tafel](../experiments/wood_beam_material_01/screenshots/comparison_board.png) belegen den fehlenden Gewinn bei ~300 Pixeln Cottagehöhe.

[Automatische Prüfung](../experiments/wood_beam_material_01/validation.json): Original-9F-Blend vor/nach SHA-256 gleich; A byteidentisch zum 9K-GLB; geometrische Dreiecks-Payloads/Materialzuordnung/Transforms in A/B/C gleich (UV-Naht-Vertexduplikate erlaubt). Godot **37 Meshes / 39 Surfaces / 14.054 Dreiecke**, Boden-Pivot `(0,0,0)`, gleiche Bounds, 16 B/C-Beam-Surfaces mit 192 Dreiecken; ursprüngliches Clay/Oak (restliche 72 Dreiecke)/Stone/Door/Dach unangetastet. **Nur isolierte A-Kopien**; keine automatische Integration.

**Einschränkungen:** Ein Poly-Haven-Material in genau einem UV-Zuschnitt und ein einfacher Wave-Bake, nur ein Long CLEAN Cottage und eine Beleuchtungs-/Distanzkonfiguration. Godot-Kompressions-/VRAM-Kosten sind nicht profilierte Runtime-Messwerte. B/C benötigen Art- und UV-Neuauflage, bevor man sie als Produktionskandidat bezeichnen darf. **Genau ein nächster kleiner Schritt:** Auf *einem* isolierten diagonalen Balken eine kleine fugenfreie, wärmer abgestimmte Textur-/UV-Teilstrecke bei gleicher Godot-~300px-Kamera prüfen; keine Gebäudeintegration ohne sichtbaren Gewinn.
