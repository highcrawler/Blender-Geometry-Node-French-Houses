# Phase 6 – Auswahlisolation, vollständige Geometrie und Boden-Pivot

## Identität statt Namen oder globaler Auswahl

Ein gültiges Exportziel ist **das aktive** Mesh mit dem Phase-5-Marker `mbg_house_version`, kompatiblem GN-Modifier und einem auf sich selbst zeigenden `Object`-Eingang. Umbenennen ist erlaubt. Mehrfachauswahl spielt keine Rolle: Im Test sind **alle fünf Häuser und ein fremder Würfel gleichzeitig ausgewählt**.

Quellinstanzen werden zuerst nach `is_instance`, `show_self` und **`inst.parent.original == active_house`** gefiltert. Nur danach werden Meshdaten/Transformationen erfasst. `persistent_id` dokumentiert einzelne verschachtelte Vorkommen. Geteilte Meshdaten sind keine Eigentümerschaft: Zwei Häuser können dieselben Pflanzenobjekte referenzieren, aber ihre jeweiligen Instanzvorkommen besitzen unterschiedliche Eltern. Es gibt keine pauschale Übernahme aller sichtbaren DG-Instanzen der Szene.

Die Exportkopie realisiert ausschließlich den Geometrieausgang des gewählten Hauses. Für jede Ausgabe wird zur Laufzeit die Dreiecksverteilung pro Originalmaterial mit **direktem Mesh plus zugehörigen Instanzblättern** verglichen. Andere Häuser werden weder realisiert noch als Exportobjekte ausgewählt. Ein vom erwarteten Eigentümerschaftsmodell abweichender Generator führt zum Abbruch, nicht zum stillen Verlust seiner Instanzen.

## Unabhängiger Nachweis über neue Phase-5-Häuser

[`test_addon_export06.py`](../scripts/test_addon_export06.py) erzeugt die Häuser wirklich über `mbg.create_house`. Das ursprüngliche `HouseOne` wird nicht als fest codiertes Exportziel verwendet.

| Haus | Weltposition in Blender | Seed | Stockwerke | Direkte Dreiecke | Sichtbare eigene Instanzen | Vollständige Dreiecke |
|---|---|---:|---:|---:|---:|---:|
| 1 | (0, 0, 0) | 29 | 2 | 57.566 | 3.056 | 187.021 |
| 2 | (20, 0, 0) | 83 | 3 | 57.004 | 3.067 | 338.825 nach Transformtest |
| 3 | (40, 15, 0) | 17 | 2 | 49.282 | 1.480 | 106.735 |
| 4 | (−30, 10, 0) | 56 | 1 | nicht als Exportziel benötigt | nicht separat exportiert | nicht behauptet |
| 5 | (15, −25, 0) | 102 | 3 | 67.821 | 2.284 | 378.786 |

Unterschiedliche Dach-/Putz-/Balkenfarben werden tatsächlich gesetzt und pro GLB geprüft. Haus 2 erhält zusätzlich Yaw **0,47 rad** und Skalierung **(−1,2; 0,8; 1,1)**. Es bleibt an seiner Weltposition; Spiegelung und nichtuniforme Skalierung werden ausschließlich in dessen Exportmesh eingebacken.

Für Haus 3, danach 1 und 5, zusätzlich Einzeltest und transformiertes Haus 2:

1. Direkte Polygone und gefilterte Instanzpolygone mit tatsächlichen Weltmatrizen erfassen.
2. Mit eingefrorener, bereits zentrierter Realize-Kopie **bijektiv** vergleichen: gleiches Material und gleiche Eckpunkte, KD-Suche über Polygonzentren, Toleranz 0,0002 BU; keine mehrfach verwendeten Zielpolygone.
3. Unabhängig GLB-Binärdaten decodieren, glTF-Achsen zurückrechnen und pro Material sämtliche verwendeten Positionen beidseitig abgleichen; zusätzlich identische Materialdreieckszahlen.
4. Genau ein GLB-Mesh, keine Node-Translation/Rotation/Skalierung, endliche Einheitsnormalen und drei echte Hausfarbwerte prüfen.

Ergebnis: **0 fehlende oder zusätzliche Polygone** in allen verglichenen Varianten. Maximale Eckfehler der Hauptziele: Haus 1 **5,34e−7**, Haus 3 **3,97e−6**, Haus 5 **2,62e−6 BU**. Die GLB-Positionsfehler liegen ebenfalls unter 4e−6 BU. Das ist deutlich stärker als ein gleicher Dreieckszähler allein.

Evidenz: [`integration.json`](../tests/addon/phase6/integration.json), `*_ownership.json` im selben Ordner. Diese enthalten Eigentümername und Persistent-ID **nur der zugehörigen Vorkommen**; die Umbenennung des Zielobjekts im späteren Test ändert seine technische Identität nicht.

## Pivot-Regel

Primär werden die an Flächen beteiligten **Eingabegrundrissvertices** verwendet, keine ausgewerteten Dach-/Pflanzen-Bounds:

```text
p.x = (min(input.x) + max(input.x)) / 2
p.y = (min(input.y) + max(input.y)) / 2
p.z = min(input.z)
```

Das ist der Mittelpunkt der Grundriss-Ausdehnung, nicht ein flächengewichteter Schwerpunkt. Für das leicht unregelmäßige, nicht exakt ebene HouseOne-Starterquad:

```text
p_local = (0.2602571845, -0.0453312397, -0.0308764577)
```

Dieselbe lokale Eingabe wird pro Phase-5-Haus unabhängig kopiert. Die eingestellte Zahl der Stockwerke, RoofCurvature, Efeu und Blumenkästen können diesen Pivot nicht verschieben.

Für Quellweltmatrix `M` und bereits eingefrorenen lokalen Vertex `v` gilt:

```text
pivot_world = M @ p_local
v_export = M @ v - pivot_world
```

Damit werden **alle Welttranslationsanteile einschließlich Welt-Z** entfernt, Rotation und Skalierung bleiben als Orientierung/Größe erhalten. Kein neues GN-Auswerten nach dem Zentrieren. Lokales +X ist weiterhin die IRCSS-Vorderseite, gegebenenfalls entsprechend der bewussten Quellrotation gedreht. GlTF/Godot-Achsen: `(x, y, z)Blender → (x, z, -y)`; +Z-oben wird +Y-oben. Standard: **1 Blender Unit → 1 Godot Unit**, keine neue Einheitenoption.

Beispiel Haus 3:

```text
Originalobjekt: (40, 15, 0), unverändert nach Export
pivot_world: (40.2602577, 14.9546690, -0.03087646)
GLB-Meshnode: Identität, keine Weltposition im Node
tragende Wand-Unterkante in glTF/Godot: Y = 0
```

Bei geneigten Häusern bleibt die bewusste Quellneigung erhalten; der Export richtet nicht heimlich ein absichtlich gekipptes Gebäude wieder auf. Aufrechte Häuser mit Z-Rotation bleiben aufrecht.

## Begrenzter Fallback

Fehlen eindeutige flächige Eingabedaten oder ist ihre Höhenstreuung größer als 10 % der kleineren XY-Ausdehnung, wird **nicht** auf die Gesamt-Bounding-Box ausgewichen. Stattdessen: ausgewertete direkte Flächen des bekannten tragenden Materials `GroundFloorWalls`, unteres Band von maximal 1 % der Körperhöhe (mindestens 0,001 BU), daraus XY-Ausdehnungsmitte und niedrigstes Z. Keine Dach-/Pflanzenmaterialien.

Dieser Fallback ist eine dokumentierte Annäherung für die bekannten IRCSS-Basisflächen. Er wurde als Kontrollpfad mit erzwungen nicht verfügbarem Primärgrundriss an Haus 3 geprüft: gleicher Pivot und identische exportierte Geometrie. Das ist **kein** Nachweis für beliebige komplexe/mehrstöckige Eingabetopologien. Unbrauchbare oder unbekannte tragende Flächen führen zu einem verständlichen Abbruch; keine erfundene Zentrierung. Der Operator meldet den Einsatz des Fallbacks als Warnung.

## Boden versus Dekoration

Unabhängiger Godot-Nachweis: `GroundFloorWalls` beginnt bei Haus 3 und 5 exakt auf **Y=0**, seine X-/Z-Ausdehnungsmitte liegt jeweils weniger als 0,003 BU vom Pivot entfernt. Die Gesamtmesh-Bounds gehen durch Steine/Pflanzen bis ungefähr −0,22 BU unter den Boden. Das ist **kein** Pivotfehler und wird nicht durch Hochheben des gesamten Hauses auf die tiefste Dekoration kompensiert. Genau diese Unabhängigkeit vom Dekor ist beabsichtigt.

## Unverändertheit

Alle fünf Weltpositionen, Rotationen, Skalen, Seeds, Geschosse, Farben, Modifier, Originalshader, Assettransformationen, Auswahl und aktives Objekt werden nach Erfolg und nach Fehlern verglichen. Es bleiben keine `MBG_TEMP`-IDs zurück. Die gespeicherte `.blend` wird nie vom Exporter gespeichert; Hashgleichheit wird im separaten Prozess und in der GUI geprüft.
