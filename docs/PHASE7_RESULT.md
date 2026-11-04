# Phase 7 – Ergebnis: PASS mit ausgewiesenen Grenzen

**Branch:** `feature/blender-addon-building-variety-07` auf konsolidiertem `main` (`66d90c8a68764e5edc90b96e04011fc1f090527f`). Phase 7 bleibt auf dem Feature-Branch. **Extension 0.3.0:** [installierbares ZIP](../tests/addon/phase7/medieval_building_generator-0.3.0.zip). Originaldatei `GeometryNodesFrenchHous.blend` SHA-256 `f44b4be96176204ada3fd768327e2a86129f536c6412129eca0478c72b3d5ae5`; keine Nodeänderungen. Die separat vorhandenen, nicht zu Phase 7 gehörenden lokalen Experimente bleiben unverändert.

## Lieferumfang

- [Grundriss-Audit](PHASE7_FOOTPRINT_AUDIT.md), [Preset-/UI-Design](PHASE7_PRESET_DESIGN.md), [Godot-Validierung](PHASE7_GODOT_VALIDATION.md).
- `footprints.py`: validierter Vierpunkt-Rechteckadapter mit Presets Compact 4,0×3,2, Narrow 3,2×5,0, Wide 7,0×4,0; Custom-Breite 3,2–7,0, -Tiefe 3,0–5,0 m. Eigene Meshdaten für neue Häuser; Copy-on-Write bei Add-on-Maßänderung nach Alt-D.
- Ergänzte N-Panel-Bedienung, Dimensions-/Preset-Properties, ausdrücklicher Bestätigungsdialog für bestehende 0.2-Häuser. Keine automatische Migration; alte Exporte bleiben möglich.
- Minimale Exportkopie-Korrektur für negativ skalierte, rotierte, statische Häuser: vorhandene, exakt kopierte Transformationskanäle nicht erneut via `matrix_world` dekomponieren. Phase-6-Exporter und Originalhaus ansonsten unverändert.
- Drei eigenständige Referenz-GLBs und Godot-Testszene, messender Godot-Durchlauf und echte Screenshots.

## Abnahmebelege

| Prüfbereich | Ergebnis / Beleg |
|---|---|
| Blender Integration 5.2.2 | [`integration.log`](../tests/addon/phase7/integration.log), [`integration.json`](../tests/addon/phase7/integration.json): `PHASE7_INTEGRATION_PASS`, alle drei Hausgeometrien und Material-/Polygonbijektionen, Reglerisolation, Shift-D und Alt-D, ungültige Auswahl, Wertebegrenzung, Registerzyklus, Rotation und negative nichtuniforme Scale. |
| GLB-Dreierprobe | Compact **86.975** Dreiecke/4.390.676 B, Narrow **90.875**/4.808.056 B, Wide **181.248**/7.917.600 B, jeweils 12 Materialien und 0 fehlende oder zusätzliche Polygone gegenüber der unabhängig realisierten Blender-Quelle. |
| Speichern/Neu laden | [`reload.log`](../tests/addon/phase7/reload.log) `PHASE7_RELOAD_PASS`; lokal gemessene und ausgewertete Werte bleiben erhalten, anschließender Export besteht. |
| 0.2-Kompatibilität | [`legacy.log`](../tests/addon/phase7/legacy.log) `PHASE7_LEGACY_PASS`; Laden ohne Migration oder Vertexänderung, alter Export-Hash wie mit 0.2, explizite Konvertierung nur nach Bestätigung, altes Mesh und anderes Haus bewahrt. |
| Export-Regression | [`export_regression.log`](../tests/addon/phase7/export_regression.log): vier ursprüngliche Phase-6-Häuser, darunter gedreht/negativ skaliert; Polygonbijektion und Dreieck-/Materialzahlen stimmen. Alle vier Referenz-GLBs bleiben bytegleich. Die Phase-6-`library.blend`-Fixture für diesen Vergleich stammt aus dem isolierten Konsolidierungslauf (`tests/consolidation/runtime/sandbox/tests/addon/phase6/runtime/library.blend`); sie ist ein regenerierbares, nicht eingechecktes Testartefakt. [`transform_diagnostic.json`](../tests/addon/phase7/transform_diagnostic.json) erklärt die korrigierte Matrix-Rundung. |
| Echte Blender-GUI | [`gui_result.json`](../tests/addon/phase7/gui_result.json) und lokalem Replay-Status `tests/addon/phase7/runtime/gui_replay_done.txt` (temporär, nicht versioniert): per `Window.event_simulate` Neues Haus, Presetauswahl, getrennte Breiten-/Tiefenänderung, Seed/Stockwerke, Exportbutton und Dateidialog. [Drei Häuser](../tests/addon/phase7/blender_three_presets.png), [Breite vorher](../tests/addon/phase7/blender_width_before.png)/[nachher](../tests/addon/phase7/blender_width_after.png), [Exportdialog](../tests/addon/phase7/blender_export_dialog.png). Die beiden nicht bearbeiteten Häuser und die gespeicherte Ausgangsszene bleiben identisch. |
| Godot 4.7 | [`godot_capture.log`](../tests/addon/phase7/godot_capture.log) `PHASE7_GODOT_PASS`; drei importierte GLBs mit passenden 4,0×3,2 / 3,2×5,0 / 7,0×4,0 m-Bodenflächen, je 12 Materialflächen, Pivot auf Bodenniveau, separate Platzierung und sichtbare Formen. [Dreieransicht](../tests/addon/phase7/godot_three_presets.png), [Fronten](../tests/addon/phase7/godot_three_fronts.png), [Einzelversatz](../tests/addon/phase7/godot_narrow_moved.png). |
| ZIP | [`build.log`](../tests/addon/phase7/build.log), [`validate.log`](../tests/addon/phase7/validate.log), [`install.log`](../tests/addon/phase7/install.log): 0.3.0 gebaut, TOML validiert und in isoliertem Blender-Profil installiert. |

## Nicht freigegeben

Beliebige L-/U-/schiefe Grundrisse, Werte außerhalb des beschränkten Bereichs, garantierte Performance bei großen Hausmengen sowie ein komplett manifold/degeneratfreier IRCSS-Ausgabemesh. Das Original hatte bereits 3.582 Nullflächen unter 23.061 direkten Polygonen; Details und höhere Performancekosten sind im [Audit](PHASE7_FOOTPRINT_AUDIT.md) beschrieben. Auch ein manuell verändertes, geteiltes Alt-D-Mesh wird nicht heimlich repariert. Diese Einschränkungen schmälern **nicht** die konkret nachgewiesene volle GLB-/Godot-Funktion der drei getesteten Presets.
