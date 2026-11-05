# Phase 8F – Ergebnis

**TECHNICAL RESULT: PASS** · **VISUAL RESULT: WORSE** (eigene kritische Beurteilung, **keine** künstlerische Freigabe durch den Benutzer).

Branch `experiment/cottage-cc0-thatch-08f`, abzweigend von `experiment/procedural-cottage-thatch-08d` / `e6ec104`; Blender **5.2.2 LTS**. [Material-/Lizenz-/UV- und GLB-Protokoll](PHASE8F_CC0_MATERIAL.md) · [kritische Bildbewertung](PHASE8F_VISUAL_COMPARISON.md) · [direkte ISO-Tafel](../experiments/cottage_generator_08f/screenshots/before_after.png) · **[entscheidende ~300-px-Tafel](../experiments/cottage_generator_08f/screenshots/before_after_300.png)**.

**Verwendetes Material:** [Poly Haven – Thatch Roof Angled](https://polyhaven.com/a/thatch_roof_angled), [CC0](https://polyhaven.com/license), offizielle 2K-Dateien: Diffuse/JPEG (sRGB), Normal OpenGL/PNG (Non-Color), Roughness/PNG (Non-Color). Keine Registrierung, kein Checkout, keine Geometrieänderung, keine weiteren Material-Noise-Effekte. Version des Assets bezeichnet durch den offiziellen Downloadpfad `thatch_roof_angled`/`2k` und die dokumentierten SHA-256-Hashes der drei Dateien; kein separat ausgewiesenes Versionslabel behauptet.

| Messwert | 8D H BASELINE | 8F CC0 |
|---|---:|---:|
| Dach-Dreiecke | **5.872** | **5.872** |
| Gesamt-Dreiecke | **6.234** | **6.234** |
| Dachobjekte / Gebäude-Materialien | 5 / 5 | 5 / 5 |
| Neue UV-Loop-Koordinaten | nein | 11.728, 0 kollabierte Flächen |
| Externe 2K-Texturen | 0 | 3 |
| Komprimierte Texturen auf Platte | 0 | **33.645.367 B** |
| Einmalige Generierung (ohne Shader-/Renderbenchmark) | 28,97 ms | 31,05 ms |

Zusätzlich: gespeichertes zweifaches Test-`.blend` **242.689 B** (referenziert externe, hier CC0-versionierte Bilder); isolierter Dach-GLB-Test außerhalb Git **30.813.760 B**, 5.872 Dreiecke, 1 Material, 3 eingebettete Images. Alle drei relativen `.blend`-Bildpfade wurden nach dem Speichern wieder in Blender geöffnet und auf Existenz geprüft. Die unveränderte 8D-H-Geometrie ist gegen die archivierte Collection und die beiden neuen Testzustände per Mesh-Fingerprint geprüft. 10 echte Blender-Renderings und fünf unbearbeitete Nebeneinander-Tafeln wurden erzeugt. Die fünf neuen BASELINE-Bilder sind pixelgenau gleich den entsprechenden 8D-H-Originalbildern. [Messdatei](../experiments/cottage_generator_08f/measurements.json).

**Gängige glTF-PBR-Übertragung:** Ein isolierter Blender-GLB-Export der CC0-Dachobjekte gelang mit UVs (`TEXCOORD_0`), Base Color, Normal und gepackter Metallic/Roughness-Textur, Metallic 0. **Kein Godot-Sichttest und keine allgemeine Pipeline**. 30,8 MB allein für ein 5,9k-Dreieck-Dach sind für ein mehrfach benutztes Spielasset zu groß, sofern Texturen nicht später reduziert/geteilt/komprimiert werden; GPU-RAM, Framerate und Übertragungsoptik wurden **nicht** gemessen. Texture-Only löst keine fehlerhafte Traufkontur oder nicht ganz natürliches Bündelvolumen.

**Antwort:** Die hochwertige CC0-Textur verbessert die **Nahsicht-Faserdetails**, löst aber unser **Strohdach-Darstellungsproblem aus mittlerer Entfernung nicht besser** als die selbst entwickelten Shader. Ihr originalbelassenes, dunkles Grau kollidiert mit der warmen, stilisierten Cottage-Palette; die Hauptfläche bleibt auf ~300 px trotz Detail relativ flach. Kein automatischer neuer Standard und **keine weitere unaufgeforderte Variante**.

**Empfehlung:** Strohdach-Experimente hier **stoppen**, bis der Benutzer eine neue gestalterische Entscheidung trifft. Kein Merge nach `main`.
