# Experiment 08D – Hybrid Thatch (nur Long Cottage)

Blender 5.2.2, aus dem Repository-Root:

```sh
blender -b -t 4 -P experiments/cottage_generator_08d/compare.py
python3 experiments/cottage_generator_08d/make_board.py  # Pillow nur für verlustfreie Bildanordnung
```

Das Skript baut genau vier Vergleichszustände aus `long.json`: unveränderte 8B-Baseline, unveränderte 8C-A/B sowie **eine** neue Hybrid-Variante H. A/B und Baseline werden gegen die gespeicherten `.blend`-Collections der Vorphasen nach geometrischen Objekt-Fingerprints geprüft. Für H werden nur Dachobjekte ersetzt: zwei geschlossene Stützschalen, ein seedbasiertes Trauf-Bündelmodul pro Abschnitt und eine Firstabdeckung. Die Nicht-Dachobjekte bleiben bytequantisiert identisch.

`compare.py` erzeugt 28 echte Blender-Bilder: pro Zustand ISO, Front, Seite, Dachdetail, Traufdetail (Cycles, 800×600, 16 Samples), 480×360-ISO (~300 px Gebäudehöhe, Cycles), nur Dach/Silhouette (Workbench, materialfrei). `make_board.py` ordnet die unveränderten ISO-Renderbilder zu `all_four.png` und die ~300-px-Bilder zu `all_four_300.png` an; die **Tafeln selbst sind kein Blender-Render**. Zudem: `Roof_Hybrid_08D.blend`, einzelne gespeicherte Collections, `measurements.json`. Nach einem Lauf muss `08D_PASS` in der Blender-Ausgabe stehen – ein Blender-Python-Traceback kann trotz Prozess-Exitcode 0 auftreten. Die Erzeugungszeit ist nur ein Einzelwert für Python-Mesh-/Materialaufbau, nicht Renderzeit oder FPS; `mesh_raw_payload_bytes` ist eine reine XYZ+Index-Untergrenze, `saved_collection_bytes` misst `.blend`-Plattendaten, nicht Blender-Heap-RAM.
