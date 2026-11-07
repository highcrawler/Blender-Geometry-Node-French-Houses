# ART-WOOD-02 – Geometrie eines Hauptbalkens

**Auswahl:** `ART01_MidRail` aus dem gemeinsamen MOD-02-Fachwerk. Anders als der 9-cm-Knieverband aus ART-BEAM-01 verläuft er als **7,30 m** langer, **12 cm** starker, mittiger horizontaler Riegel über die komplette **~300-px-Wandansicht**; größere zusammenhängende Ansichtsfläche, trotzdem bei normaler Spielentfernung nur etwa **5 px Querschnitt**. Anschluss-Endpunktmitten der 9-Fachwerk-Meshes: `(2,607;−3,65;1,1725)` und `(2,607;+3,65;1,1725)` Blender X/Y/Z. Ausgang 8 Vertices/12 Dreiecke, Material `09J_A_weathered_oak_constant`, Roughness 1, Metallic 0. Verifizierte lokale Z-Richtung `(0,+1,0)` in Weltkoordinaten; lokale X `(-1,0,0)` und Y `(0,0,+1)` (numerisches Transformrauschen <10⁻⁶). Lokale ±Z-Endebenen und Transform erhalten ihre Position; bestehende Bauteile und Montage-Pivots bleiben unangetastet.

**B und C identische Zielbalken-Geometrie:** Auf isolierter Kopie nur vier Längskanten 15× unterteilen. Clouds-Displace `0,003 m` (Noise Scale `0,72 m`, Depth 2), Vertex-Gewichtung über je `0,55 m` an Enden auf Null; drei unterschiedlich breite/flache, gezielt verteilte Behauungsfacetten der oberen Kante mit maximal `0,011 m` Tiefe und Ausblendung gegen die Enden; Blender-Bevel-Modifier Width `0,004 m`, Segments 2, Kantenwinkelgrenze `0,5 rad`. Beide Modifier *vor* UV/GLB-Export angewandt; keine bloße Blender-Vorschau. Nach Prüfung vollständig geschlossene, orientierte Geometrie (jede Kante manifold, positives signiertes Volumen). Keine Endflächen-Retreat: lokale Endebenen `±3,6500001 m`; die äußersten Endecken werden durch die Fase leicht reduziert, wie bei einem behauenen Balken. Das beweist nicht Zapfen- oder Kontaktperfektion der bestehenden Box-Joints.

| Isolierte Wand | A Original | B Geometrie | C Geometrie + Textur |
|---|---:|---:|---:|
| Zielbalken Vertices / Δ | 8 / 12 | 236 / 468 | 236 / 468 |
| Gesamtdreiecke / Meshe | 204 / 16 | 660 / 16 | 660 / 16 |
| Materialien / eingebettete Maps | 2 / 0 | 2 / 0 | 3 / 2 |
| GLB-Größe | 21.588 B | 54.020 B | 218.448 B |

Ein Balken kostet somit **+456 Δ (~39× Ausgangswert)** und C etwa **+197 KB GLB** gegenüber A. Das ist ohne sichtbaren Art-Gewinn in Spielentfernung nicht vertretbar. Die 15 anderen nativen GLB-Mesh-Payloads einschließlich Plaster/Fenster/anderem Rahmen bleiben in allen drei Zuständen identisch; A ist byteidentisch zum MOD-02-B-GLB. Godot importiert 204/660/660 Δ und identische Gesamtbounds/Modulpivots. Quelle vor/nach SHA-256 `38acea0fac6720a7b853a2242a59fc3bdc34e0cb552b9f9774bd22e31e6effae`.
