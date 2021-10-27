# Adeept Mars Rover Erweiterung

## Yolo Installation
Siehe unter: https://pjreddie.com/darknet/
-> Auf einen leistungsstarken PC installieren.

## Neues 2. Dashboard
Unter localhost:5000/dashboard zu finden.
Von doer aus kann man die vieles einstellen. Man muss die E-Mail Konfiguration und/oder die Telegram Bot Konfiguration vornehmen.

### Menü Punkt: Konfig
* E-Mail Konfiguration
    * Hier muss man die E-Mail SMTP Server einstellungen vornehmen.
    * Dabei muss gesetzt sein:
        * MAIL_USE_TLS = True
        * MAIL_USE_SSL = False
* Alarm Modus: Benachrichtung
    * Hier kann man eingeben, wie man informiert werden will, wenn der Roboter im Modus "Alarm" ist.
    * Checkboxes für die Benachrichtungen
    * Textfelder für die Empfänger, die mit einen "," getrennt werden.
* Untergrundeinstellungen
    * Hier kann man die Drehzeit des Roboters manipulieren. Man muss nur drauf achten, dass es eine float Zahl ist, ansonsten wird ein Fehler geworfen.
    * z.B. für 1 muss man 1.0 eingeben.
* Konfig löschen
    * Hier kann man alle Konfigurationen auf einmal löschen.
    * Nicht zu empfehlen, es sei denn, man verschenkt den Roboter.

### Menü Punkt: Raum Scanner
Das ist nur die Liste der Gegenstände, die der Roboter erkannt hat.

### Menü Punkt: YOLO Modus
Hier kann man die Einstellungen zu YOLO Einfach und YOLO Move machen.
Es ist nur ein Singel Choice Objekt, da der Roboter nur ein Gegenstand finden kann, in diesen Modus.

### Menü Punkt: Sammel Modus
Hier kann man die Gegenstände einstellen, die der Roboter finden muss.
Sofern er nichts findet, so überspringt der Roboter das nicht vorhandene Objekt.
Bevor der Roboter ein Objekt skipt, dreht er sich um 180°, da es durch aus sein kann, das es hinter ihm stehen könnte.

### Menü Punkt: Alarm Modus
Hier kann man die Gegenstände einstellen, bei dem der Roboter einen informieren soll, wenn er sie findet.

## Eingabearten:

### Singel Choice
Es ist eine Eingabe Tabelle mit 4 Feldern, bei den man die Reihenfolge bearbeitbar ist.
Nachteil: nur bis zu 4 Objekte einstellbar.
*None* bedeutet nichts und wird nicht in die Konfig geschrieben.

### Multiple Choice
Man kann alle möglichen Objekte anwählen, aber nur in der dort angebenen Reihenfolge und auch nur einmal.


### Swip Swap
Man hat 2 Felder und 3 Buttons (Hinzufügen, Entfernen, Speichern). Man kann die Reihenfolge nach belieben ändern und Dopplungen vornehmen.
Ist der Eingabe modus mit der freisten Auswahlmöglichkeit.

## Eigene Modi und Funktionen
### Neue Modi:
* YOLO 1+2
* Raum scannen
* fahrender Raum Scanner
* Alarm
* Sammeln

### Neue Funktionen:
* Rechts- und Links-Kurve
* Konstant vor und zurück fahren
* Kreisfahrmodus

## Modi Erläuterungen

### YOLO Einfach
Der zu suchende Gegenstand muss vor der Kamera stehen, damit der Roboter hinfährt

### YOLO Move
Der zu suchende Gegenstand muss im Raum stehen, damit der Roboter hinfährt

### Raum Scanner
Der Roboter registeriert alle ihm bekannte Objekte und speichert sie.
Dabei macht er nach dem ersten Intervall eine 180° Drehung

### Fahrender Raum Scanner
Der Roboter fährt und scannt im 180° Winkel alle ihm bekannte Objekte.

#### Logik
Ist ein meter vor dir frei? -> fahre grade aus.
Aonst fahre nach rechts bzw. links.

### Alarm
Wenn der Roboter den trigger hat, wird dem Besitzer eine Nachricht per (E-Mail) gesendet.

### Sammeln
Fahre zum Objekt hin, bewege dich zurück und fahre zum nächsten Objekt hin.
*Voraussetzung*: YOLO Move