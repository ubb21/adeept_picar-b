# Objekterkennungsserver
## Server
Dieser Server wird mit Flask betrieben.
## YOLO
Dieser Server benutzt YOLOv3 um die gesendeten Bilder analysieren.

## Funktionsweise
Der Client sendet ein Bild als Base64 kodierten String an den Server per HTTP-GET Request.
Nach etwa 5 Sekunden sendet der Server die Antwort als modifizierter JSON String

## Ausgabe
* Nichts: 
* 1 Objekt: |{...}
* 2 Objekte: |{...}|{...}
* n Objekte: [|{...}]^n

## Analyse Dauer
* Raspberry Pi 4: 15-20 Sekunden
* Tower PC (Ryzen 7): <1 Sekunde, max. 2 Sekunden