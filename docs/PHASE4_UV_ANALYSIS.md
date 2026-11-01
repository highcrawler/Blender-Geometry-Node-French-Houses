# Phase 4 – UV-Diagnose

Daten: [UV-Messungen](../tests/baking/phase4/uv_measurements.json), [Überlappung/Abstände/Verzerrung](../tests/baking/phase4/uv_overlap.json). Bilder: [Original](../tests/baking/phase4/uv_original.png), [Bake-Layout](../tests/baking/phase4/uv_bake.png). Die Bilder zeigen ausschließlich Putzflächen.

| Messung | Original UVMap | PlasterBake auf Exportkopie |
|---|---:|---:|
| Putz-Polygone / Dreiecke | 1.105 / 2.210 | unverändert |
| Verschiedene UV-Koordinaten, Original | 32 | neues Layout |
| Verschiedene Polygon-UV-Muster | 38 | 1.105 |
| Exakt wiederverwendete Muster | 1.067 | 0 |
| Polygone mit UV-Fläche null | 1.104 | 0 |
| Flächig überlappende Polygonpaare | 0 | 0 |
| UV-Inseln, über gemeinsame Kanten | nicht sinnvoll | 49 |
| Genutzte Atlasfläche | nicht sinnvoll | 43,745 % |
| Kleinste Face-Fläche | 0 Pixel | 5,10 Pixel |
| Kleinster Inselabstand | nicht sinnvoll | 40,959 Pixel |
| Kantenmaßstab max./min., Median / Maximum | nicht sinnvoll | 1,000013 / 1,002908 |

Die Original-UVs sind eindeutig **ungeeignet**: Fast alle Flächen kollabieren zu Linien und teilen wiederholt dieselben Koordinaten. Null flächige Überschneidungen bedeutet hier gerade nicht Bake-Eignung. Es gibt im ursprünglichen ausgewerteten Mesh keine als UV-Seam markierten Kanten.

Nur auf der Exportkopie wird ein zusätzlicher Layer `PlasterBake` angelegt. Smart UV Project betrifft ausschließlich die 1.105 Putzflächen: 66° Winkelgrenze, `FRACTION`-Island-Margin 0,02, Aspect-Korrektur, keine Geometrieänderung und kein Generatorumbau. Die vorhandene UVMap und die übrigen Materialflächen bleiben erhalten. Die neuen UV-Trennungen werden als Corner-Koordinaten gespeichert; manuell gesetzte Mesh-Seams sind dafür nicht erforderlich.

Die Überlappungsprüfung schneidet konvexe UV-Polygone paarweise, prüft zuvor deren Konvexität und ignoriert gemeinsame Kanten ohne Fläche. Inseln werden aus gemeinsamen UV-Kanten gebildet; der Abstand wird zwischen Randsegmenten verschiedener Inseln gemessen (Koordinaten dafür auf sechs Nachkommastellen gerundet). Die Verzerrungskennzahl vergleicht UV-/3D-Kantenlängen innerhalb derselben Fläche; sie ist kein universeller Stretch-Beweis für beliebige Meshes. Hier ist die Abweichung gering. 8 Pixel Bake-Extension pro Seite passen in den gemessenen Mindestabstand von rund 41 Pixeln.

In den getesteten drei Ansichten sind keine offensichtlichen schwarzen UV-Nähte sichtbar. Die kleinen Flächen und nur 1024² bleiben eine Auflösungsgrenze; nicht alle Oberflächen wurden aus jeder Richtung oder über sämtliche Mip-Stufen abgenommen. Die Atlasbelegung ist bewusst konservativ, nicht speicheroptimiert.
