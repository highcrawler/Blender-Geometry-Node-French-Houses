# Experiment 08B – Traufkante

Blender **5.2.2**; vom Repository-Root aus:

```sh
blender -b -t 2 -P experiments/cottage_generator_08a/test_parameters.py
blender -b -t 2 -P experiments/cottage_generator_08b/build_compare.py
```

`build_compare.py` prüft zunächst, dass `refine_eave=False` den **exakten** Phase-8A-Weltgeometrie-SHA-256-Wert jeder Variante reproduziert. Danach werden die drei 8B-Hütten mit identischen Parametern/Seeds erzeugt, geprüft und im selben Blender-Lauf aus denselben Kameras vor/nach gerendert. Ausgaben: `measurements.json`, `Cottage_Thatch_08B.blend` und echte Blender-Workbench-Bilder in `screenshots/` (ISO-Paare, Silhouetten-Paare ohne Materialien, Nahaufnahmen und alle drei neuen Häuser zusammen). Die `.blend` enthält sowohl Baseline- als auch neue Collections; kein externes Asset, kein Add-on- oder IRCSS-Library-Import. **Nicht** den alten 8A-Render als 8B-Render ausgeben: beide Zustände werden neu gerendert. Das alte 8A-Buildskript erzwingt auf diesem Branch `refine_eave=False`, sodass seine historischen Referenzdateien beim erneuten Lauf erhalten bleiben.
