import base64


PIC_PATH = '/root/urs_robot/server/pic.jpg'
"""Pfad, wo wir das Foto abgreifen können"""

URL = 'http://192.168.1.103:5000'
"""URL für dem Objekterkennungs Server"""
URL_OPTION = '/send-image/data:image/jpeg;base64,'
"""Wie wurde das Bild kodiert, inklusiv URL"""

LIST_GEGEN = 'gegenstaende.csv'
""" Auflistung der gefunden Gegenstände"""

SAMMLER_CONF = 'sammler.csv'
""" Auflsitungen der zu suchenden Objekte"""



ALARM_CONF = 'alarm.csv'
""" Bei welchen Objekt soll der Roboter alarm schlagen"""
ALARM_MSG_CONF = 'alarmnachricht.csv'
"""Hier soll die Einstellungen zur Benachrichtung eingestellt werden.
PS: Ob E-Mail oder Telegram Nachricht"""
MAIL_EMP_CONF = 'mail_empf.csv'
"""Hier kommen die Empfänger der E-Mail rein"""
TELEGRAM_BOT_CONF = 'tg_bot.csv'
"""Hier wird der Telegram vom @BotFather hinterlegt für den Telegram Bot"""
TELEGRAM_EMP_CONF = 'tg_empf.csv'
"""Hier wird die ID des Empfängers der Nachricht hinterlegt."""
TELEGRAM_BOT_URL = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
"""Erster Teil der URL Nachrichtsende URL von Telegram """


YOLO_CONF = 'yolo.csv'
""" YOLO Such und fahr hin Gegenstand"""

MAIL_conf = "mailconf.csv"
"""E-Mail Server Konfigations Datei"""

# Roboter Einstellungen
ROBOT_SPEED = 95
""" Geschwindigkeit des Roboter"""

ZEITFAKTOR = "lenker.csv"
""" Zeitfaktor in der Datei"""



def get_base64_encoded_image(image_path):
    """Bild -> Base64 String"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

