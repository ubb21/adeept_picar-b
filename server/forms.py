from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import SubmitField,SelectField
from wtforms.fields.core import BooleanField, FloatField, SelectMultipleField
from wtforms.fields.simple import TextField
from wtforms.validators import DataRequired

# Alle verfügbaren Objekte aus der Darknet Coco.names herauslesen
DARKNET = "/root/urs_robot/detect/data/coco.names"
DARKNET_1 = ['None']
DARKNET_2 = []
datei = open(DARKNET,"r")
for zeile in datei:
    zeile = zeile.replace("\n","")
    DARKNET_1.append(zeile)
    DARKNET_2.append([zeile,zeile])
datei.close()
DARKNET_1.sort()
DARKNET_2.sort()

class ChangeSammlerForm(FlaskForm):
    """ Singel Choice Formular"""
    textarea1= SelectField('Gegenstand 1', choices=DARKNET_1, default=1)
    textarea2= SelectField('Gegenstand 2', choices=DARKNET_1, default=1)
    textarea3= SelectField('Gegenstand 3', choices=DARKNET_1, default=1)
    textarea4= SelectField('Gegenstand 4', choices=DARKNET_1, default=1)
    submit = SubmitField('Speichern')

class YoloChangeSC(FlaskForm):
    """ Singel Singel Choice Formular für den Suchmodus (YOLO)"""
    textarea1 = SelectField('Gegenstand 1',choices=DARKNET_1, default=1)
    submit = SubmitField('Speichern')

class AlarmBenachrichtung(FlaskForm):
    """ Formular um die Kontaktdaten für den Alarm Modus"""
    mail_btn = BooleanField('E-Mail Benachrichtung')
    tg_btn = BooleanField('Telegram Benachrichtung')
    mail_empfanger = TextField('E-Mail Empfänger (getrennt mit ,)')
    tg_user = TextField('Telegram Empfänger ID (getrennt mit ,)')
    tg_bot = TextField('Telegram Bot Token')
    submit = SubmitField('Speichern')

class EmailChange(FlaskForm):
    """ Formular um den E-Mail Server zu konfigurieren """
    server = TextField('E-Mail Server',validators=[DataRequired()])
    port = TextField('Port',validators=[DataRequired()])
    username = TextField('Username',validators=[DataRequired()])
    password = TextField('Passwort',validators=[DataRequired()])
    mail_tls = BooleanField('MAIL_USE_TLS')
    mail_ssl = BooleanField('MAIL_USE_SSL')
    submit = SubmitField('Speichern')

class UntergrundSetting(FlaskForm):
    """ Den Zeitfaktor zum lenken einstellen"""
    eingabe = FloatField('Zeitfaktor für den Untergrund',validators=[DataRequired()])
    submit = SubmitField('Speichern')

class d_felder(FlaskForm):
    """ Swip Swap Formular"""
    ein = SelectMultipleField('Zur Verfügung stehende Objekte',choices=DARKNET_2)
    submit2 = SubmitField("-->")        # Hinzufügen
    selected = SelectMultipleField('Ausgewählte Objekte',choices=[])
    submit3 = SubmitField("<--")        #Entfernen
    submit = SubmitField("Speichern")   #Speichern
    submit4 = SubmitField("Auswahl lösen")

class delete_conf_form(FlaskForm):
    submit = SubmitField("Alle Konfigs löschen")

print("[API] Forms created")