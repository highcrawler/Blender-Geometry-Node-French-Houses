# Phase 8E – Blender-5.2.2-Kompatibilitätsprotokoll

**Status: BLOCKED / NOT TESTED.** Das System liegt nicht als rechtmäßig zugängliche lokale Datei vor; damit wurde **keine** externe `.blend` in Blender geöffnet, keine fremde Node-Gruppe ausgeführt und keine Material- oder GeoNodes-Kompatibilität nachgewiesen. Blender auf dem Rechner meldet **5.2.2 LTS**. Die [Herstellerseite](https://superhivemarket.com/products/blender-4-hay-roof-geometry-node) führt nur Blender **4.0, 3.6, 3.5** auf. Daraus ist weder Inkompatibilität noch Kompatibilität mit 5.2.2 abzuleiten.

| Prüfung | Tatsächlicher Befund |
|---|---|
| Laden ohne relevante Fehler / Blender-Versionsheader | Kein externes `.blend` vorhanden; nicht testbar. |
| Node-Gruppen, Node-Typen, fehlende/veraltete Nodes | Nicht testbar. Die Produktwerbung ist kein Node-Tree-Inventar. |
| Ausgewertete Geometry Nodes, Instanzen, echte Triangles | Nicht testbar; **keine erfundene Zahl**. |
| Materialslots, Bildtexturen, externe Pfade, Packed Assets | Nicht testbar. Die zwei beworbenen PBR-Materialien sind für das kostenlose Paket nicht belegt. |
| Tatsächliche Seed-/Viewport-/Render-Dichte-/Längen-/Gravitationsparameter | Nicht testbar; eine Werbeliste belegt keine konkreten Socketnamen und keine Implementierung. |
| Arbeitsspeicher, Dateigröße, Evaluationszeit | Ohne Asset und Ausführung nicht messbar. |

**Lokales Verfahren, erst nach einem rechtmäßigen Bezug:** unverändertes Originalarchiv außerhalb des Git-Worktrees aufbewahren, SHA-256, Bezugsdatum, Version und beigefügte Lizenz privat dokumentieren; eine **Kopie** in einem separaten nicht versionierten Testordner mit `blender -b <kopie.blend>` öffnen. Per `bpy.data.node_groups` echte Interface-Sockets und Node-Typen inventarisieren; `bpy.data.materials`, `bpy.data.images` und `bpy.data.libraries` auf fehlende Dateien/Links untersuchen. Für einen vom Produkt bereitgestellten Beispielmodifikator `bpy.context.evaluated_depsgraph_get()` und `evaluated_get(...).to_mesh()` nutzen, Anzahl tatsächlicher Dreiecke mit `calc_loop_triangles()` zählen, Evaluationsdauer (mehrere kontrollierte Wiederholungen mit Warm-up) messen und `to_mesh_clear()` aufrufen. Instanzanzahl separat über Depsgraph-Instanzen erfassen; **vor/nach Realisierung nicht verwechseln**. Die konkreten verfügbaren Parameternamen dokumentieren, erst dann denselben Seed und **eine** ggf. reduzierte Dichte prüfen. Nichts am Original überschreiben und keine externen Node-Gruppen/Materialien committen.

## Geplanter, nicht ausgeführter Cottage-Adapter

Referenz bleibt die vorhandene Phase-8D-[Long-Cottage-Konfiguration](../experiments/cottage_generator_08d/long.json): **5,1 × 7,3 m**, Wandhöhe **2,3 m**, **40°**, Seed **23**. Bestehende [8D-Komparatorszene](../experiments/cottage_generator_08d/compare.py) generiert unveränderte Nicht-Dach-Meshes und das H-Dach. Der gedachte Adapter würde *nur in einer separat gespeicherten lokalen Testkopie* die beiden Dachflächen als Eingabemesh isolieren (keine Änderung an Wand, Grundriss, Tür oder Archiven), eine lizenzierte Node-Gruppe lokal referenzieren, ihre tatsächlichen Socket-/Attributanforderungen ermitteln und erst dann Länge/Dichte/Strichrichtung zur Traufe setzen. Orientierung, Objektmaßstab, Normalen, UVs und eventuell benötigte benannte Attribute sind **unbekannt**, nicht als implementiert ausgegeben. Ein benutzerinstalliertes Assetpaket wäre technisch möglich, seine Integration und Lizenz wären gesondert zu klären. **Kein Adapter implementiert**, weil das notwendige externe Node-Asset fehlt; kein neuer Ersatzgenerator.

**Wiederanlaufkriterium:** Ein nachweislich rechtmäßig bezogenes kostenloses Showcase-Original, das mindestens einen funktionsfähigen GeoNodes-Modifikator/Node-Tree und die zugehörigen Nutzungsbedingungen enthält. Falls es nur Marketing-/Render-Beispiele enthält, bleibt der Integrationstest blockiert; daraus folgt nicht, dass die Bezahlversion kaputt ist.
