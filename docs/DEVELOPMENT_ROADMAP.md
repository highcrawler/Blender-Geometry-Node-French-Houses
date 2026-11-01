# Entwicklungs-Roadmap (Analyse, keine Implementierung)

Grundsatz: bestehende `GenerateHouse`-Geometrie und MIT-Lizenz erhalten; kleine Schnittstellen-/Exportmodule statt Neubau. Jeder Meilenstein muss mehrere Seeds, einfache/komplexe Grundrisse und Godot-GLB-Import gegenprüfen.

| Priorität | Maßnahme | Technischer Ansatz | Akzeptanzkriterium |
|---|---|---|---|
| P0 | Reproduzierbare Testmatrix | Gespeicherte Grundrisse, dokumentierte Modifier-Werte/Seeds, PNG- und GLB-Vergleich | Drei Varianten automatisiert erzeugbar; gleiche Version/Seed stabil; keine schwebenden Bauteile |
| P0 | Game-Engine-Materialtreue | Shader-/Attribut-Inventar, UV-Prüfung, gegebenenfalls PBR-Textur-Bake und Godot-Rendervergleich | Fassade, Holz und Dach in Godot plausibel; keine fehlenden Texturen |
| P0 | Export-Qualitätsgate | Bestehende Depsgraph-Bake als Grundlage, Origin/Boden, Normalen, Materialslots, Polycount, Bounding Box, Import-Smoke-Test | GLB neu importierbar, alle Details erhalten und Ground-Level numerisch geprüft |
| P1 | Detail- und LOD-Budget | Pflanzen und Dachziegel als getrennte Detailregler; Varianten mit weniger Geometrie | Definierte Dreieckbudgets je Distanzstufe und gemessene Renderkosten |
| P1 | Parametrische Hausgrößen | Vorhandene Grundriss-Meshes und `NumberFloor` als kontrollierte Schnittstelle mit Grenzwerten | Keine unnatürliche Streckung, Fenster-/Türkollision oder losgelöste Balken bei Testmatrix |
| P1 | Kontrollierbare Dachformen | `RoofCurvature`, `RoofGeometryType`, Überhang-Schalter und `Switch On Roof Type` kartieren | Mindestens zwei dokumentierte Dachvarianten mit identischem Grundriss |
| P1 | Seed und Farb-Presets | `Seed`, `GetPositionBasedSeed`, drei Farbsockets + dokumentierte Profile | Serien wiederholbar; unterschiedliche Stilprofile bei gleicher Geometrie |
| P2 | Modulares Fachwerk | `CreateDiagonalBeams`, `WindowBeams` mit stabilen Eingängen isolieren | Austauschbares Muster ohne Beschädigung bestehender Häuser |
| P2 | Historische Baustile/Serien | Presets für Grundriss, Balken-/Dachform, Farben; `HousesOnCurves` als optionale Serie | Wiedererkennbare Reihe ohne identische Häuser oder erhebliche Überschneidungen |
| P2 | Batch-Export | Geprüftes Einzelhaus-Skript auf Seed-/Preset-Matrix erweitern | Manifest mit Version, Parametern, Mesh-Budget und Importresultat pro Asset |

**Empfehlung nächste Phase:** P0 Materialtreue plus visuelle Godot-Gegenprobe und reproduzierbare Seed-Matrix. Der vorhandene glTF-Import ist technisch erfolgreich, aber die GLB enthält keine Texturen; das ist das größte Qualitätsrisiko vor einer Gebäudebibliothek. Keine zusätzlichen Modelle, kein vollständiger Node-Neubau in dieser Phase.
