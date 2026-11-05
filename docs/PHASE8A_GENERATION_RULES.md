# Phase 8A – Erzeugungsregeln

## Eingaben

`Cottage(width=5.0, depth=4.0, wall_height=2.4, roof_pitch=48.0, seed=1)`; Meter und Grad. Grenzen: Width 3–8, Depth 2.8–9, Wall Height 2–3, Roof Pitch 35–60, Seed 0–2³¹−1. Ungültige Eingaben lösen `ValueError` aus. Jeder Aufruf erzeugt eine eigene Collection; kein globaler Haus-Mesh-Scale. `random.Random(seed)` wird nur lokal verwendet, nicht der globale RNG. Gleiche Eingaben und Generatorversion ergeben dieselben Geometriekoordinaten und Materialfarben. Die zufälligen Strohvariationen bleiben klein und ändern keine Strukturentscheidungen.

## Bauregeln

Grundriss x ∈ [−w/2,w/2], y ∈ [−d/2,d/2]. Sockeloberkante z=.24; Lehmwand von z=.25 bis h. Vorderwand: links/rechts der 0.92 m breiten Tür je `(w−0.92)/2` Wand; darüber Querfeld bis zur Traufe. Rück- und Seitenwände eigene Flächen, je Vorder-/Rückgiebel ein Dreieck. Türblatt in der tatsächlichen Öffnung, nicht über einer geschlossenen Wand. Eckpfosten und umlaufende Rähme; zwei kurze Diagonalstreben pro Seitenwand, Türpfosten und Schwelle. Dachfirst z=`h+(w/2)*tan(pitch)`. Eave-Verlängerung in x=.34 m, in y=.25 m; Traufe z=h−.10 m. Pitch bestimmt so den Anstieg über der nominellen halben Hausbreite; der gemessene Winkel der verlängerten Deckfläche weicht entsprechend geringfügig ab.

Pro Dachseite ein **geschlossenes** Gitter aus oberen und unteren Flächen mit vernähten Randflächen: entlang Breite 9, entlang Tiefe mindestens 12 Abschnitte bzw. `round(depth*4)`; Volumendicke .21 m mit weiteren .06 m an der Traufe. Bounded Seed-Wellen verformen allein Dachkante und Oberfläche. Kurze, sparsame Traufbündel (.13–.21 m) und ein zwölfseitiger, abgerundeter Firstwulst brechen die harte Silhouette. Fünf lokale Materialien: Lehm, Eiche, Stroh, Stein, Türholz; materialbasierte Noise-Farbvariation im Principled-Shader, ohne externe Texturen. Rendering im Workbench-Modus zeigt nur die Grundfarben und Meshform, **nicht** die Shader-Noise; die `.blend` enthält die Shader für Material-/Cycles-Ansichten.

## Grenzen

Bauteile sind unabhängige, teils an Kontaktstellen absichtlich überlappende Meshes. Die Dachschalen sind einzeln geschlossen (bmesh: jeweils 0 nicht-manifold Kanten), das *gesamte* Haus ist kein einheitlicher wasserdichter Solid; Giebel sind dünne Dreiecke. Keine vollständige Schnitt-/UV-/Self-Intersection-Analyse, keine gemessenen FPS. Ländliche Dachwirkung benötigt noch eine künstlerische Prüfung im Material-Render. Keine Fenster, Inneneinrichtung, Export- oder Add-on-Funktion.
