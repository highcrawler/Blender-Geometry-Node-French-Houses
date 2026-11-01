# Phase 3 – echter Bildvergleich

Alle Bilder sind echte Anwendungs-Renderings (Blender Cycles CPU, 16 Samples/AgX bzw. Godot GUI OpenGL 3), 960×720, kein illustratives Mockup. Die Blender-Bilder verwenden auf **demselben ausgewerteten Mesh** die Originalshader bzw. die PBR-Exportmaterialien bei identischer Beleuchtung und orthografischer Kamera: iso `(12,-15,12) → (0,0,3.7)`, front `(16,0,5.2) → (0,0,3.7)`, facade `(11,-5,4.8) → (0,-0.4,4.2)`, vertikale Skalen 15/12/6. Godot transformiert die Blender-Kamera in sein Achsensystem: iso `(12,12,15) → (0,3.7,0)` usw. Godot nutzt anders als Cycles eine Echtzeit-OpenGL-Beleuchtung; direkte Pixel- oder Belichtungsgleichheit ist **nicht** gegeben. Phase-3-Godotlicht: `sun.light_energy=0.65`, `ambient_light_energy=0.35`, statt Phase-2-Szene 1.8/0.8. Hintergrund/Kamera/Geometrie unverändert. Die helleren PBR-Albedos waren unter 1.8/0.8 sichtbar überbelichtet; das Testlicht wurde deshalb für die Materialprüfung gedimmt, nicht das GLB heimlich umgefärbt.

| Ansicht | Blender original | Blender PBR-Exportkopie | Godot importiertes PBR-GLB |
|---|---|---|---|
| Iso | [Original](../tests/materials/phase3/blender_original_iso.png) | [PBR](../tests/materials/phase3/blender_pbr_iso.png) | [Godot](../tests/materials/phase3/godot_pbr_iso.png) |
| Front | [Original](../tests/materials/phase3/blender_original_front.png) | [PBR](../tests/materials/phase3/blender_pbr_front.png) | [Godot](../tests/materials/phase3/godot_pbr_front.png) |
| Fassade | [Original](../tests/materials/phase3/blender_original_facade.png) | [PBR](../tests/materials/phase3/blender_pbr_facade.png) | [Godot](../tests/materials/phase3/godot_pbr_facade.png) |

Direkte Dreier-Tafeln: [Iso](../tests/materials/phase3/comparison_iso.png), [Front](../tests/materials/phase3/comparison_front.png), [Fassade](../tests/materials/phase3/comparison_facade.png). Bildtafeln wurden aus den oben verlinkten PNGs zusammengesetzt, nicht gerendert.

| Bereich | Blender-Original | Blender-PBR-Kopie | Godot-PBR-GLB |
|---|---|---|---|
| Dach | Altrosa/rot, einzelne Ziegel unterschiedlich schattiert und texturiert | sattes, relativ einheitliches Pink/Rot | sichtbar rot-pink, ähnlicher Grundton; stärkere Helligkeit |
| Fachwerk | dunkelbraune Balken, dunkle Tür/Fensterhölzer | helles grau-bräunliches Holz ohne Maserung | grau-braun, vom weißen Putz abgesetzt, deutlich zu hell gegen Original |
| Putz | grauweiß, deutliche fleckige Abplatzungen/Ziegel darunter | überwiegend heller Warmweißton, keine Shader-Abplatzungen | heller Warmweißton, keine Abplatzungen |
| Naturstein | unregelmäßige graue/beige Steine mit Noise/Normalvariation | beige Grundfläche und hellere Steinformen, ohne Shaderrauschen | beige Grundfläche und hellere Steinformen sichtbar, weniger plastisch |
| Fenster/Türen | dunkel und strukturiert; Verglasung nicht belastbar nachgewiesen | dieselben Geometrien, hellgrau-braun, homogen | Formen vorhanden; Tür deutlich heller, keine nachgewiesene Verglasung |

**Im GLB statt nur im Viewport:** [`HouseOne_PBR.json`](../tests/materials/phase3/HouseOne_PBR.json) protokolliert fünf unterschiedliche `baseColorFactor`-Werte (u.a. Dach `[0.4792,0.0553,0.1106,1]`, Balken `[0.2706,0.2141,0.2204,1]`, Putz `[0.9444,0.8715,0.8403,1]`, Stein `[0.5088,0.4585,0.3752,1]`) und fünf materialgebundene Primitives. `baseColorTexture`/Images gibt es absichtlich nicht. [`phase3_godot.log`](../tests/materials/phase3_godot.log) weist die importierten fünf Godot-`BaseMaterial3D`-Farben samt Roughness/Metallic sowie ein Mesh, fünf Surfaces, 50.944 Triangles nach. GLB-Faktoren sind lineare Farben; Godots protokollierte `albedo_color`-Darstellung ist nicht numerisch identisch zum linearen Faktor.

**Bewertung der Ähnlichkeit getrennt vom technischen Gate:** Farbzuweisung und Hauslesbarkeit funktionieren; Originallook nur **teilweise** erhalten (insbesondere Balken/Tür, Putzabplatzungen, Stein- und Dachvariation). Verschiedene Render-/Tonemapping-Umgebungen verhindern einen pixelgenauen Farbvergleich. Kein Hinweis auf neue fehlende Geometrie; keine Aussage zu nicht sichtbarer Glastransparenz.
