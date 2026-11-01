# Phase 4 – Ergebnis

**RESULT: PARTIAL**

Der originale Putzshader auf der unveränderten Phase-3-Exportgeometrie wurde erfolgreich als Base Color gebacken und in Blender sowie Godot angezeigt. Die originale prozedurale Farb-/Schadenslogik bleibt erhalten. Ein PASS für volle GN-Originaltreue wäre jedoch zu weitgehend: Der bestehende Mesh-Export übernimmt nicht sämtliche GN-Instanzen; die Übereinstimmung der Generated-Koordinaten mit dem vollständigen GN-Original ist nicht gesichert. Hinzu kommen sichtbar weicheres Feindetail und das bei einem reinen Farbbake erwartbar fehlende Normalenrelief.

| Metrik | Phase 3 | Phase 4 |
|---|---:|---:|
| Dreiecke | 50.944 | 50.944 |
| Mesh-Vertices / Faces | 27.919 / 20.003 | 27.919 / 20.003 |
| GLB-Größe | 2.424.884 Bytes | 3.803.968 Bytes |
| Materialien | 5 | 5 |
| Bildtexturen | 0 | 1 eingebettetes PNG |
| Texturauflösung | – | 1024 × 1024, sRGB |
| PNG-Größe | – | 98.405 Bytes |
| Visuelle Putzqualität | Ohne Schäden | Schäden, Flecken, Ziegelfarben; weniger Relief |
| Sichtbare UV-Nähte | – | keine auffälligen in den drei Ansichten |

Mehrbedarf GLB: **1.379.084 Bytes (+56,87 %)**. Dieser umfasst die Textur, zusätzliche UV-Daten und daraus folgende Exportvertex-Aufteilungen; nicht nur das 98-KB-PNG. Keine zusätzlichen Normal-/Roughness-Maps. Der neue UV-Layer bleibt neben dem Original-Layer erhalten. Keine FPS- oder Laufzeitperformance-Aussage.

## Technischer Nachweis

[measurements.json](../tests/baking/phase4/measurements.json) enthält Bake-/Exportdauer, Hashes, GLB-JSON und Texturreferenz. Der dokumentierte Renderlauf benötigt etwa 6,83/6,85 Sekunden für die beiden Bakes und 0,40 Sekunden für den Export (ohne Vergleichsrenderings). Zwei Bakes sowie ein weiterer Blender-Prozess lieferten dasselbe PNG, SHA-256 `1fef33e7b37104a491fe53584ff1e1b2284d0e169c3334e8d455a14d6bb7e2fd`. Dies ist ein Wiederholungsnachweis dieser Version/CPU-Konfiguration, keine Garantie für alle Blender-Versionen.

GLB: fünf Primitives, fünf Materialien, genau ein Image und eine Texture. `UpperFloorsPaint_Phase4.pbrMetallicRoughness.baseColorTexture = {index: 0, texCoord: 1}`; `TEXCOORD_1` ist vorhanden und für Putz innerhalb 0…1. Der über Texture → Image → BufferView aus dem BIN-Chunk extrahierte PNG-Bytestrom ist identisch zum gespeicherten Bake. Godot erkennt ihn als Albedo-Textur 1024². Das zusätzliche PNG im Godot-Assetordner wurde vom GLB-Importer extrahiert, nicht als zweite Textur exportiert.

[GLB-Geometrievergleich](../tests/baking/phase4/glb_geometry_comparison.json): identische Dreieckszahlen je Material, beidseitiger Vergleich der dekodierten Vertexpositionen einschließlich Objekttranslation, maximale Abweichung unter 0,0000003 Blender-Einheiten. Triangle-Corner-Reihenfolge kann nach UV-Splits/Tessellation abweichen; kein Anspruch auf identische Indexbytes. Der Positions-/Polygon-/Materialindex-Hash des Blender-Meshes ist vor und nach der Bearbeitung exakt gleich. Die vier übrigen glTF-PBR-Materialparameter sind exakt mit Phase 3 identisch. Source-SHA unverändert; keine Änderung an `GenerateHouse`, früheren Ergebnissen oder `main`.

## Reproduktion aus der Repository-Wurzel

```bash
blender -b --factory-startup GeometryNodesFrenchHous.blend -t 4 -P scripts/phase4_audit.py
blender -b --factory-startup -t 4 -P scripts/bake_houseone_plaster.py -- --render --repeat
python3 scripts/phase4_uv_check.py
python3 scripts/phase4_validate_glb.py
cp tests/baking/phase4/HouseOne_Phase4.glb godot-test/assets/HouseOne_Phase4.glb
godot --headless --path godot-test --editor --import --quit
godot --path godot-test --rendering-driver opengl3 --script res://scripts/phase4_capture.gd -- --output "$PWD/tests/baking/phase4"
python3 scripts/phase4_images.py
```

Hier wurde für Blender der direkte lokale Binary-Pfad `/snap/blender/current/blender` verwendet; der Snap-Launcher war in der Sandbox blockiert. Godot-Screenshots benötigen die grafische Sitzung. Python-Bildtafeln benötigen Pillow, keine NumPy-Abhängigkeit. Ohne `--render` erzeugt das Skript nur Bake, GLB und Messdaten; `--repeat` wiederholt denselben Bake, keine zweite Variante. Die Skripte sind der reproduzierbare Ersatz für eine zusätzliche große `.blend`-Testdatei.

## Speicherprüfung und Wartbarkeit

Keine `.gitattributes`-/LFS-Zuweisung vorhanden (`git check-attr filter`: unspecified; `git lfs ls-files`: leer). Vor Commit geprüft: größtes neues Einzelartefakt GLB 3,80 MB, Vergleichstafeln jeweils unter 1,9 MB; Phase-4-Testordner etwa 19 MB. Native Git-Ablage entsprechend den früheren Phasen, keine neue LFS-Migration. Godot-Importcache `.godot` bleibt ignoriert. Keine Blender-Backups, Crashdumps oder temporären Sinks versioniert. Die zwei alten unversionierten Phase-2-Probes bleiben außerhalb des Commits.

**Lohnt sich Texture Baking?** Ja, für gezielt ausgewählte Fassaden: deutlicher Gewinn gegenüber einfarbigem Putz, geringer PNG-Bedarf und auf diesem Haus reproduzierbar. Der Aufwand steckt vor allem in Koordinatentreue, UV-Prüfung und verlässlicher Exportauswahl. Die getrennte Exportkopie hält den Generator wartbar. Übertragbarkeit auf andere Gebäudetypen ist noch nicht nachgewiesen: andere Abmessungen, Attribute, Instanzen und UV-Belegungen müssen geprüft werden. Das Skript ist absichtlich kein allgemeines Baking-System.

**Genau ein nächster Entwicklungsschritt:** Die Generated-Koordinaten des originalen HouseOne-GN-Putzes auf einer isolierten Exportkopie explizit erfassen/fixieren und die Schadenspositionen gegen das vollständige GN-Original verifizieren. Erst dieser begrenzte Nachweis schließt die verbliebene Lücke der Originaltreue; keine neue Generatorfunktion und kein Merge nach `main`.
