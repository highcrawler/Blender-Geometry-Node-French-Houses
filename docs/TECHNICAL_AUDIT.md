# Technisches Audit – IRCSS-Hausgenerator

## Provenienz und Umfang

- Upstream: https://github.com/IRCSS/Blender-Geometry-Node-French-Houses, Commit `b49b3c1dca15a57f3696e23c6f3ba8badf1fa6a3` (`main`).
- Fork: https://github.com/highcrawler/Blender-Geometry-Node-French-Houses; Entwicklungsbranch `experiment/building-generator-audit`. `origin` ist ausschließlich der Fork; `upstream` nur zum Nachführen.
- Originaldateien `LICENSE`, `README.md`, `GeometryNodesFrenchHous.blend`, `Demo-MagicSchoolV2.blend` und `documentation/` unverändert. `LICENSE` ist MIT, Copyright (c) 2025 Shahriar Shahrabi; Lizenztext und Urheberhinweis bleiben maßgeblich.
- Blender 5.2.2 LTS (`d13f752e3b9c`), Linux, Headless-Test. README nennt Blender 5.0 als ursprüngliche Testversion. Diese Prüfung beweist Öffnen, Auswertung, Speichern, Workbench-Render und Export ausgewählter Häuser, nicht die vollständige Funktionsprüfung aller 110 Gruppen.

## Projektstruktur

`GeometryNodesFrenchHous.blend` ist die aktuelle Asset-Quelle, `Demo-MagicSchoolV2.blend` die ältere Demo (laut README). `documentation/` enthält GIF-Beispiele. `scripts/` enthält ausschließlich Audit-/Testskripte. `tests/variants/` enthält editierbare Szenen, Screenshots, GLB und Messdaten. `godot-test/` ist ein unabhängiges Import-Prüfprojekt. `docs/blender_inventory.json` enthält das reproduzierbare Inventar der Quelldatei.

## Datensicht und Abhängigkeiten

Das Blender-API-Inventar (`blender -b GeometryNodesFrenchHous.blend -t 4 -P scripts/inspect_blend.py`) meldet **110 Geometry-Node-Gruppen**, **77 Objekte mit GN-Modifikator**, **56 Materialien** und **keine ungeladenen externen Bilddateien**. Drei gefundene FILE-Bilder haben ursprüngliche absolute Windows-Pfade, sind aber gepackt; ein Viewer-Renderbild ist kein externes Asset. Die Quellen sind Asset-Bibliothek und Szene zugleich, keine Python-Addon-Architektur.

`GenerateHouse` besitzt **1023 Nodes / 1075 Links**, darunter 131 Frames, 37 Random-Value-, 17 Set-Material-, 11 Instance-on-Points- und 10 Realize-Instances-Nodes. Direkte Untergruppen: `CreateDiagonalBeams`, `Curve Info`, `Generate Windows`, `GetPositionBasedSeed`, `Is Edge Manifold`, `Switch On Roof Type`, `WindowBeams`. `HousesOnCurves` (166 Nodes) verwendet `GenerateHouse` plus `Color in Range`, `Float in Range`, `Int in Range` für die Reihenhausverteilung. Die Gruppen `Generate Windows` (188 Nodes) und `WindowBeams` (63 Nodes) teilen Fenster- und Balkenlogik; `Switch On Roof Type` besitzt 3 Nodes. Daneben existieren unabhängige Gruppen für Türbögen, Türprofile, Dachfenster, Tür-/Fenster-Alkoven und weitere Stadtbauteile. Nicht alle Gruppen werden von `GenerateHouse` verwendet.

### Hausablauf (aus GN-Frame-Beschriftungen und Node-Typen)

1. **Grundriss:** Eingangsmesh ist ein ungefähr X-symmetrischer Grundriss; laut README zeigt lokales +X nach vorne/zur Tür. Ein einfaches viereckiges Mesh oder ein zehnpunktiger Grundriss ergibt verschiedene Silhouetten. Der Grundriss wird über Extrude-Mesh/Positionsoperationen in Sockel, Geschosse und Dachbasis zerlegt. Mesh-Form und Objekt-Transformation sind getrennte Steuerflächen; das README warnt davor, für die Rotation/Skalierung die Objekttransformation anzuwenden.
2. **Geschosse/Fassade:** Frame-Texte bezeichnen Grundgeschoss, Vorziehen des Obergeschosses, Zwischenstockwerke, Fensterpositionen, Wandselektion und tragende Balken. Es gibt eine Repeat-Zone für Geschossoperationen, Kurven-/Profilgeometrie für Fachwerk und `CreateDiagonalBeams` für Streben. Untere Steinwand und gestrichene obere Wand werden als getrennte Materialflächen zugewiesen. Der Überhang ist gestalterisch gewollt und muss bei neuen Parametern geprüft werden.
3. **Dach:** gesonderte Dachbasis, Firsthöhe, überstehende Seiten und Stirnseiten, Unterteilung und irreguläre Dachziegel; Dachfenster, Schornsteine und Dachmaterial kommen in späteren Strängen. `RoofCurvature`, `RoofGeometryType` sowie `DisableRoofExrudeFront/Back` sind Schnittstellen. Eine umfassende Dachtyp-Matrix wurde nicht getestet; Varianten in diesem Audit nutzen unterschiedliche Proportionen und bestehende Dachausprägungen, keinen neu implementierten Dachgenerator.
4. **Fenster/Tür:** Kandidatenpunkte auf Fassaden, Ecken- und Abstandsfilter, zufällige Auswahl, besondere Fenster am Dach, Balken um Öffnungen; Türpunkte auf der Vorderseite, Auswahl eines Punkts, Boolescher Durchbruch und Türbalken. `Generate Windows` erzeugt Fensterdetails. Eine architektonische Mindestabstands-Garantie für beliebige Grundrisse ist damit nicht belegt.
5. **Material/Zufall:** direkte Schnittstellen `Seed`, `RoofColor`, `PaintColor`, `BeamCollor`; `GetPositionBasedSeed` und zufällige Werte für Geschoss-/Fenster-/Stein- und Dachdetails. Die Farb- und Seed-Schnittstellen sind vorhanden, aber Seed-Reproduzierbarkeit über mehrere Blender-Versionen wurde nicht statistisch validiert. Ursprungsmaterialien können Blender-spezifische Shader-/Attributlogik enthalten; glTF übernimmt diese nicht automatisch vollständig.

`GenerateHouse`-Eingänge im gespeicherten Asset: `Input` (Geometry), `Object`, `Seed` (0), `NumberFloor` (1), `RoofCurvature` (1.3), `RoofColor`, `PaintColor`, `BeamCollor` (Schreibweise original), `DisableRoofExrudeBack`, `DisableRoofExrudeFront`, `SpawnIVY` (false), `RoofGeometryType` (Menü, Vorgabe `Real Geometry `), `High Polz Plants` (true). Diese Defaults sind Node-Group-Defaults; Objekt-Overrides müssen separat ermittelt werden. Bei `HouseOne`, `HouseTWo` und `HouseThree` ist `GenerateHouse` derselbe Modifikator.

## Befunde und Grenzen

- Die gesamte Gruppe ist groß und eng gekoppelt; geplante Module sollten zunächst an Gruppeneingängen/Untergruppen andocken, nicht die 1023 Nodes ersetzen.
- Reale Häuser erreichen 45.926–93.818 Dreiecke **pro Haus** (Details und Pflanzen enthalten); für viele Godot-Häuser sind LOD-/Detailstufen nötig.
- Drei editierbare Varianten sind Kopien der gesamten Quellszene mit jeweils isoliertem sichtbaren Haus; weitere Original-Objekte bleiben für mögliche GN-Referenzen enthalten. Sie sind deshalb etwa 9 MB groß und nicht schon bereinigte Produktionsassets.
- Die drei Bilder sind **graue Workbench-Geometrieprüfungen**, keine Material-/Farb-Freigabe. Sichtbar sind Dachgauben, Fachwerk und Fenster; Überhang und Fassadendetails bedürfen bei weiteren Grundrissänderungen visueller QA.
- Keine Aussagen über Performance auf schwachen GPUs, sämtliche Assetgruppen, semantisch historische Korrektheit oder Kollisions-/Begehbarkeitsqualität aus diesem kleinen Test ableiten.
