# Phase 6 – Godot 4.7: Import und grafische Abnahme

**PASS für die beiden geprüften Hausvarianten.** Getestet: Godot `4.7.stable.official.5b4e0cb0f`, Linux, grafischer Compatibility/OpenGL-Lauf. Keine Änderungen an externen Spielprojekten; ausschließlich das vorhandene unabhängige `godot-test/` im Repository wurde um neue Testdateien ergänzt. Die bestehende Hauptszene und Projekteinstellungen bleiben unverändert.

## Importierte Artefakte

| Variante | GLB | Bytes | Basis-Dreiecke | Meshes / Material-Surfaces |
|---|---|---:|---:|---:|
| Haus 3, Seed 17, 2 Stockwerke | [house3.glb](../tests/addon/phase6/house3.glb) | 5.137.440 | 106.735 | 1 / 12 |
| Haus 5, Seed 102, 3 Stockwerke | [house5.glb](../tests/addon/phase6/house5.glb) | 16.230.960 | 378.786 | 1 / 12 |

Linux-Testprojekt: `godot-test/assets/MBG_Phase6_House3.glb` und `MBG_Phase6_House5.glb` sind **relative Symlinks** auf diese beiden Dateien. Damit liegen die eigentlichen Testartefakte unter `tests/addon/phase6/` ohne doppelte Binärablage. Nach Clone müssen Symlinks unterstützt werden; andernfalls die beiden Dateien an die entsprechenden Assetpfade kopieren. Das installierbare Blender-Add-on benötigt diese Testprojekt-Verknüpfungen nicht.

Blenders GLB-Dateien sind eigenständig: **keine Bilder, keine Textur-URIs, keine externen Shader**. Die beiden Dateien wurden mit Godots normalem Editor-Importprozess importiert, nicht lediglich als Rohbinärdaten geparst. Die `.import`-Metadaten werden mitgeführt; `.godot/`-Caches nicht.

## Gespeicherte Testszene

[`godot-test/scenes/addon_export06.tscn`](../godot-test/scenes/addon_export06.tscn) enthält zwei unabhängige importierte PackedScenes:

- `House3`: Position **(0, 0, 0)**.
- `House5`: Position **(12, 0, −2)**.
- Boden auf Y=0, schmale orange Pivotkreuze und beschriftete Ursprünge.
- Neutrales Licht, Kamera und Environment nur für die Testszene.

Keine Collisions, neuen Shader, Batch-/LOD- oder Exportoptionen entwickelt. Die Add-on-GLBs enthalten keine eigenen LODs; Godots normale Importpipeline bleibt davon unabhängig.

## Laufzeitprüfungen

[`addon_export06_capture.gd`](../godot-test/scripts/addon_export06_capture.gd) lädt die gespeicherte Szene, traversiert nur die zwei Haus-Teilbäume und prüft:

- genau ein Mesh je Haus, jeweils zwölf tatsächlich verwendete PBR-Surfaces;
- exakte Basis-Dreieckszahlen wie der unabhängige Blender-/GLB-Audit;
- keine Texturabhängigkeiten, nichtleere `BaseMaterial3D`-Zuweisungen;
- Hausroots an den vorgegebenen unabhängigen Positionen, Skalierung **(1,1,1)**;
- Mesh-Kindtransformation **Identität**, also keine versteckte ursprüngliche Welttranslation;
- tragender `GroundFloorWalls`-Körper beginnt exakt bei **Y=0**;
- dessen X-/Z-Bounds-Mitte maximal 0,01 BU vom Ursprung entfernt (gemessen weniger als 0,003 BU).

Gemessener tragender Körper in lokalen Godot-Koordinaten:

```text
Haus 3: Position (-1.693097, 0, -3.073490), Größe (3.383923, 7.001570, 6.151427)
Haus 5: Position (-1.693096, 0, -3.073491), Größe (3.383923, 9.952726, 6.151427)
```

Das zusätzliche Geschoss ist als Höhenunterschied sichtbar. Steine/Pflanzen reichen teilweise unter Y=0; der Pivot folgt absichtlich der tragenden Grundfläche statt der tiefsten Dekoration.

Anschließend wird **nur Haus 5 nach (14, 0, −4)** verschoben. Haus 3 bleibt nach Laufzeitassertion bei (0,0,0). Beide sind getrennt platzierbar, keine gemeinsame Gebäudemeshdatei oder geerbte Bibliotheksweltposition.

## Echte grafische Screenshots

Aus einer tatsächlichen Godot-Rendering-Sitzung via `RenderingServer.frame_post_draw` und Viewport-Image, nicht aus Headless-Mockups:

1. [Zwei importierte Hausvarianten mit Boden-Pivots](../tests/addon/phase6/godot_two_houses.png).
2. [Nur Haus 5 unabhängig verschoben](../tests/addon/phase6/godot_house5_moved.png).

Die Häuser sind aufrecht und tragen ihre unterschiedlichen Dach-/Putz-/Balkenfarben, Fachwerk, Fenster, Gauben, Steinflächen und Pflanzen. **Keine vollständige Blender-Materialtreue:** prozedurale Oberflächenvariation, Bump und echtes Glas fehlen bewusst. Der PBR-Status ist in [Architektur](PHASE6_EXPORT_ARCHITECTURE.md) beschrieben.

## Protokolle

- [`godot_import.log`](../tests/addon/phase6/godot_import.log): Standard-Import der referenzierten GLBs, keine relevanten Importfehler.
- [`godot_capture.log`](../tests/addon/phase6/godot_capture.log): tatsächlicher grafischer Lauf, Engine-/Treiberangabe, `PHASE6_GODOT_PASS`, keine Script-/Laufzeitfehler.
- [`godot_measurements.json`](../tests/addon/phase6/godot_measurements.json): Mesh-/Surface-/Dreieckszahlen, Materialnamen und Albedo, Bounds, Positionen, Skalierungen, Pivotassertionen.

Die Daten prüfen die vollständige importierte Basisgeometrie. Es wurde kein Performance- oder Lasttest mit 50 Häusern durchgeführt.

## Reproduktion

Nach Erzeugung der Exportartefakte oder direkt mit den beiden versionierten Referenz-GLBs aus Repository-Wurzel:

```bash
mkdir -p tests/addon/phase6/runtime/godot/{config,data,cache}
export XDG_CONFIG_HOME="$PWD/tests/addon/phase6/runtime/godot/config"
export XDG_DATA_HOME="$PWD/tests/addon/phase6/runtime/godot/data"
export XDG_CACHE_HOME="$PWD/tests/addon/phase6/runtime/godot/cache"
godot --headless --path godot-test --editor --import --quit
godot --path godot-test --rendering-driver opengl3 \
  --script res://scripts/addon_export06_capture.gd -- --output "$PWD/tests/addon/phase6"
```

Ein Display und funktionierendes grafisches Rendering sind für den zweiten Aufruf erforderlich. Ein erfolgreicher Headless-Import allein wäre keine grafische Abnahme.
