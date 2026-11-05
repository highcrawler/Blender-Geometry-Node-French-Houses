# Phase 8D – Hybrid-Dachentwurf

Ausgang: `3749fa4`, nur die Long Cottage `5,1 × 7,3 × 2,3 m`, Dach 40°, Seed 23. Neues Modul `experiments/cottage_generator_08d/hybrid.py`; unveränderte `cottage.py` und `roofs.py` aus 8A–8C werden importiert. `compare.py` entfernt ausschließlich `role='roof'`-Objekte der frisch generierten H-Cottage; Hauskörper, Tür, Holz, Sockel, Grundriss und maximale Bauhöhe werden gegen die Baseline getestet. Die 8B-Baseline und 8C-A/B werden zusätzlich gegen **separat gespeicherte** `.blend`-Collections geprüft. Kein Generatorstandard wird umgestellt.

## A – zusammenhängende Basis

Zwei geschlossene 8C-B-ähnliche Stützschalen mit 6 Fall- und `max(18, round(depth*3))` Längssegmenten. x-Abstand zur alten Traufe und Satteldachformel bleiben wie zuvor; 22–27 cm tiefe Deckung. Die Basis schließt auch dort alle Zwischenräume, wo an den Enden der neuen Bündel kleine Lücken auftreten. Keine horizontalen Schichtreihen wie 8C-A, keine große Dachplatten-Unterteilung.

## B – kleines wiederverwendbares Traufbündel

Längs der Traufe `max(18, round((depth+0,5)/0,19))` **Module pro Dachseite**; bei 7,3 m sind es **41 je Seite, insgesamt 82**. Jedes Modul besteht aus deterministisch **2 oder 3** schmalen, seitlich leicht überdeckenden und geringfügig gebogenen Streifen. Gesamt hier **219 Teilstreifen**. Ein Teilstreifen ist ein geschlossener, zur Mitte breiterer, an Anfang/Ende schmalerer Körper mit drei geneigten Querschnitten; 12 Vertices, **20 Dreiecke**. Der hintere Teil ist ca. 9 mm in den Stützkörper eingebettet; die Mitte hebt sich nur ca. 18 mm, die unregelmäßig gekürzte Spitze reicht etwa 4–13 cm über die alte Trauflinie hinaus. Kleine Y- und Verlaufsabweichungen werden allein vom festen Seed erzeugt. Beide Seiten sind zwei kombinierte Meshes statt 219 separater Objekte. Ein visueller Strohhalm-pro-Mesh-Ansatz wird ausdrücklich vermieden. Der Körper bleibt auch bei Zwischenräumen als zusammenhängendes Dach erkennbar; dichte Teilstreifen können sich konstruktionsbedingt geringfügig überschneiden.

## C – gerichtete Faserstruktur und First

Ein neues Material mit derselben gedeckten Stroh-Grundfarbe wie die Cottage-Baseline; Material-Object-Koordinaten werden über eine grobe Noise minimal in y verzerrt und dann anisotrop skaliert (y hochfrequent, x/z niedrig), sodass die feinen Striche überwiegend dem Gefälle folgen. Farb-Rampe mit warmen gedämpften Brauntönen, Roughness ca. 0,83–0,95, Metallic=0 und sehr schwacher Bump (Strength 0,055, Distance 0,006). Die Faserwirkung ist in den Blender-Cycles-Bildern sichtbar, nicht im materialfreien Silhouettenrender. First: der bereits seedvariierte, geschlossene zwölfseitige Rollabschluss aus 8C wird verwendet, mit demselben Firstmaximum wie die 8B-Baseline. Seine Endkappe wirkt noch relativ starr und zeigt an der Giebelspitze einen dunklen Anschlussschatten; dieser Prototyp fügt keine neue Firstarchitektur hinzu.

## Messung, Grenzen und spätere Ausfuhr

H = **1.280 Dachgrundkörper- + 4.380 Bündel- + 212 First-Dreiecke = 5.872 Dach-Dreiecke**, 6.234 insgesamt. Alle tragenden Dachschalen und Details sind einzeln geschlossen; 0 nicht-manifold Kanten und 0 doppelte Flächen auf den beiden Stützschalen, positive Volumina und gültige Normalen bei den geschlossenen Dachdetails. Die Gesamtdeckung ist **kein einzelnes manifold Solid**, denn Bündel überlappen sich und liegen teilweise im Stützkörper. Keine vollständige paarweise Selbstschnitt-/UV-Prüfung. Wiederholung mit Seed liefert gleiche Geometrie. Ein temporärer Breite-/Tiefe-Test (5,6 × 8,3 m) prüft, dass Breite der Stützschale und Zahl der Module tatsächlich wachsen; er erzeugt **keinen** weiteren gespeicherten Haus-Prototyp.

Der geschlossene Dachkörper, die Bündel und der First sind grundsätzlich **Mesh-GLB-tauglich**, müssen für ein Spielasset jedoch noch auf UVs, Zusammenführung und Exportkanten geprüft werden. Die Object-Coordinate-Noise, farbige Ramp, Roughness-Verschaltung und Bump sind **nicht als identische Shader per GLB garantiert**: Farbe/Normal/Roughness bräuchten später Texture-Baking, eine Engine-Shader-Reimplementierung oder bewusste Vereinfachung. Kein Export oder Baking in Phase 8D.
