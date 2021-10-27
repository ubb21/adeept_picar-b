import urs_config as cof
import requests
from flask_mail import Message


def send_telegram(text):
    """Sendet eine Telegram Nachricht an die Empfänger"""
    try:
        datei_empfanger = open(cof.TELEGRAM_EMP_CONF,"r")
        empfanger = datei_empfanger.readline().split(",")
        datei_empfanger.close()
        datei_token = open(cof.TELEGRAM_BOT_CONF,"r")
        token = datei_token.readline()
        if len(token) > 30:
            for entry in empfanger:#token,entry,text
                print("An die ID {} wurde eine Nachricht gesendet".format(entry))
                requests.post(cof.TELEGRAM_BOT_URL.format(token,entry,text),timeout=2)
    except FileNotFoundError:
        pass

def send_mail(text,mail):
    """Sendet eine E-Mail an die Empfänger"""
    empfanger = []
    try:
        datei_empfanger = open(cof.MAIL_EMP_CONF,"r")
        empfanger = datei_empfanger.readline().split(",")
        datei_empfanger.close()
        msg = Message(subject='Mars Rover Alarm',sender='noreply@ursb.de',recipients=empfanger)
        msg.body = text
        msg.html = text
        mail.send(msg)
        print("An die ID {} wurde eine Nachricht gesendet".format(empfanger))
    except FileNotFoundError:
        pass
