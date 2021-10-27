import ultra, time, json, requests, os

from requests.exceptions import Timeout
from json.decoder import JSONDecodeError

from datetime import datetime

import urs_config as cof
import functionDriving as fDrive

import webHelper

# Klasse
class RangeStrategie(object):
    """Strategy Pattern: Auswahlpattern"""

    def runs(self):
        self.function()

    def __init__(self,x0: int,x1: int , name: str,lastObject: int,mode: str, funcs):
        self.x0 = x0
        self.x1 = x1
        self.name = name
        self.function = funcs
        self.mode = mode
        self.lastObject = lastObject
        
    def ispossible(self, x : int,functionMode: str, lastObject):
        """Ausführungs Funktion
		x - Kordinate
		lo = lastObjectSeen"""
        if ((functionMode == self.mode) or self.mode == "all") and  (self.x0 <= x and x <= self.x1) and  ((self.lastObject == lastObject) or (self.lastObject == -1)):           
            return True
        else:
            return False

# Strategien
def init_strategien(self):
	"""YOLO Advance Strategien starten"""
	strategien = []
	print("[YOLO] Initalisiere Strategien")
	# Yolo Einfache Strategien
	strategien.append(RangeStrategie(-2,-2,"Pause",						0,"yolo",self.pause))
	strategien.append(RangeStrategie(-1,0,"Pause",						0,"yolo",self.pause))

	# YOLO Advance Strategien
	# -1 bei den Integern beduetet, dass der letzte gesehen Ort uninteresant ist
	strategien.append(RangeStrategie(-2,-2,"Nichts gefunden @ -1",		-1,"yoloAD",self.yolo_counter))
	strategien.append(RangeStrategie(-1,-1,"Zunah dran @ -1",			0,"yoloAD",self.pause))

	# Sammler Modus
	strategien.append(RangeStrategie(-2,-2,"Nichts gefunden @ 0",		-1,"Object",self.sammel_counter))
	strategien.append(RangeStrategie(-1,-1,"Zunahn dran",				-1,"Object",self.sammel_back))

	# Generische Strategien
	# all bedeutet, dass der Modus egal ist, wann diese BEdingung getriggert wird
	#					Range von x0 bis x, Name der Option		LastObject, Mode, Funktion 
	strategien.append(RangeStrategie(1,140,"Links",						0,"all", self.fahr_links))
	strategien.append(RangeStrategie(141,279,"Grade aus",				0,"all",self.fahr_gradeaus))
	strategien.append(RangeStrategie(280,640,"Rechts",					0,"all",self.fahr_rechts))

	# Raum Scann Funktionen
	strategien.append(RangeStrategie(1,640,"Rechts Mitte Abiegen @ 1",	1,"all",self.yolo_turn_rightmittig))
	strategien.append(RangeStrategie(1,640,"Rechtsabiegen @ 2",			2,"all",self.yolo_turn_right))
	strategien.append(RangeStrategie(1,640,"Links Mittig abbiegen @ 3",	3,"all",self.yolo_turn_leftmittig))
	strategien.append(RangeStrategie(1,640,"Linksabbiegen @ 4",			4,"all",self.yolo_turn_left))
	return strategien

def init_function_entscheider(self):
	Goings = []
	Goings.append(webHelper.Entscheider('none', self.pause))
	Goings.append(webHelper.Entscheider('Automatic', self.automatic_processing))
	Goings.append(webHelper.Entscheider('Steady', self.steady_processing))
	Goings.append(webHelper.Entscheider('trackLine', self.track_line_processing))
	Goings.append(webHelper.Entscheider('speechRecProcessing', self.speech_rec_processing))
	Goings.append(webHelper.Entscheider('keepDistance', self.keep_dis_processing))
	Goings.append(webHelper.Entscheider('konst', self.konst_fahrmodus_processing))
	Goings.append(webHelper.Entscheider('konst2', self.konst_fahrmodus2_processing))
	Goings.append(webHelper.Entscheider('kreis', self.kreis_fahrmodus_processing))
	Goings.append(webHelper.Entscheider('turnRight', self.turn_right_processing))
	Goings.append(webHelper.Entscheider('turnLeft', self.turn_left_processing))
	Goings.append(webHelper.Entscheider('yolo', self.yolo_einfach))
	Goings.append(webHelper.Entscheider('yoloAD', self.yolo_move))
	Goings.append(webHelper.Entscheider('roomScan', self.room_scan))
	Goings.append(webHelper.Entscheider('roomScanSmart', self.drive_scan))
	Goings.append(webHelper.Entscheider('Object', self.sammel_process))
	Goings.append(webHelper.Entscheider('alarm',self.alarm_process))
	return Goings

def yolo_look_advance(object: str,scGear, lastObject):
	""" Kopf des Roboters nach Rechts, Links oder Vorne gucken lassen und erkennen wo die Flasche ist"""
	kordinate = []
	if lastObject == 0:
		 kordinate = look_normal(1,0,object,scGear) # Objekt war vorne
	elif lastObject == 1:
		kordinate = look_normal(1,-45,object,scGear) # rechts, mittig
		# Objekt war rechts
	elif lastObject == 2:
		kordinate = look_normal(1,-90,object,scGear)# rechts
		# Objekt war rechts
	elif lastObject == 3:
		kordinate = look_normal(1,45,object,scGear) # links, mittig
		# Objekt war links
	elif lastObject == 4:
		kordinate = look_normal(1,90,object,scGear) # links
		# Objekt war links
	return kordinate

	# Den Kopf zum ausrichten, zur Gradzahl
def look_normal(motor: int ,tilt : int, object : str, scGear):
	"""Für YOLO Objektverfolgungsmodus: Mit Servo Motor Steuerung 
	-2: Gegenstand nicht gefunden
	-1: Gegenstand steht im Weg herum"""
	print("[YOLO] Look")
	scGear.moveAngle(motor, tilt)
	dist = dist_redress()
	kordinate =[-2,-2,-2,-2]
	if dist <= 50:
		kordinate = [-1,-1,-1,-1]
	else:
		time.sleep(1.5) # Auf Bild warten
		JSON_LIST = send_picture()
		print(JSON_LIST)
		splitter = JSON_LIST.split("|")
		for astring in splitter:
			try:	
				tmp = json.loads(astring)
				if tmp['text'] == object:
					kordinate[0] = tmp['x']
					kordinate[1] = tmp['y']
					kordinate[2] = tmp['w']
					kordinate[3] = tmp['h']
			except JSONDecodeError:
				pass
	print("[YOLO] look_normal: x=",kordinate[0])	
	return kordinate
	
def pic_analyse():
	""" Bildanalyse: Für den Raum Scanner Modus"""
	Liste = []
	JSON_LIST = send_picture()
	splitter = JSON_LIST.split("|")
	for astring in splitter:
		try:	
			tmp_json = json.loads(astring)
			if tmp_json['text'] not in Liste:
				Liste.append(tmp_json['text'])
				print("[YOLO] Add: ",tmp_json ['text'])
		except JSONDecodeError:
			pass	
	return Liste

	# Gehört zur obigen
def send_picture():
	""" Wir senden das Bild an den Erkennungsserver als Base64 String und erhalten ein JSON-DICT Objekt zurück"""
	print("[YOLO] Sende Bild")
	# Wir kodieren unser Bild in Base64
	pic = cof.get_base64_encoded_image(cof.PIC_PATH)
	out = str("")
	try:
		# An Server senden
		request = requests.get(cof.URL + cof.URL_OPTION + pic, timeout=15)
		out = request.text
	except Timeout:
		print("[Fail] Timeout")
	return out


# Filter out occasional incorrect distance data.
def dist_redress(): 
	"""Filter out occasional incorrect distance data."""
	mark = 0
	dist_value = ultra.checkdist() * 100
	while True:
		time.sleep(0.1)
		dist_value = ultra.checkdist() * 100
		if dist_value > 900:
			mark +=  1
		elif mark > 5 or dist_value < 900:
			break
		print(dist_value)
	return round(dist_value,2)

def write_db(liste1):
	""" Gefundene List in eine Datei schreiben"""
	datei = open(cof.LIST_GEGEN,'a')
	for entry in liste1:
		if entry != "":
			print(entry)
			datei.write(entry+",")
	datei.write("\r\n")
	datei.flush()
	datei.close()


def room_scan_util(motor,tilt, time_sets,scGear):
	"""Motor und Foto aufnehmen und analysieren"""
	scGear.moveAngle(motor, tilt) 
	time.sleep(time_sets)
	return pic_analyse()

def room_scan_scan(scGear):
	""" Logik hinter dem Scannen; Gekapselte Funktion
	Array[0] = Distanzmessungen
	Array[1] = Werte"""
	time_sets = 2
	scGear.moveAngle(0, 10) # Tilt Motor
	time.sleep(0.1)

	liste1 = room_scan_util(1,90,time_sets,scGear) # links
	dist_li = dist_redress()
	liste2 = room_scan_util(1,45,time_sets,scGear)
	liste3 = room_scan_util(1,0,time_sets,scGear)	# mitte
	dist_vo = dist_redress()
	liste4 = room_scan_util(1,-45,time_sets,scGear)	
	liste5 = room_scan_util(1,-90,time_sets,scGear) # rechts
	dist_re = dist_redress()

	time.sleep(0.1)
	scGear.moveAngle(1, 0) # Kopf wieder nach vorne Ausrichten
	
	# Listen appenden
	backlist = []
	backlist.append([dist_li,dist_vo,dist_re]) #0
	list_of_list = []
	for liste in liste1, liste2, liste3, liste4, liste5:
		for entry in liste:
			list_of_list.append(entry)
	backlist.append(list_of_list) #1
	return backlist

def drive_scan(scGear,move):
	"""##### Fahrmodus: fahrender Scanner"""
	scGear.moveAngle(2,10) # Lenker ausrichten

	# optische Sache
	_all = room_scan_scan(scGear=scGear)

	# Datenstrukturen verwalten
	_list = _all[1]
	write_db(_list)
	dist_li,dist_vorne,dist_re = _all[0]

	# Entscheide Funktion
	if dist_vorne > 100:
		print("Option 1")
		move.move(cof.ROBOT_SPEED,'forward','no',0)
		time.sleep(5)
		move.motorStop()
	else:
		print("Option 2")
		if dist_li > dist_re:
			fDrive.raw_turn(True, scGear,move) # Links
		else:
			fDrive.raw_turn(False, scGear,move) # Rechts


def alarm_scan(scGear,move,self,alarm_object):
	"""##### Fahrmodus: Alarm"""
	scGear.moveAngle(2,10) # Lenker
	time.sleep(0.1)
	
	# Scannen und Datenstrukturen verwalten
	_all= room_scan_scan(scGear=scGear)
	_list = _all[1] # Liste der Objekte, die gefunden wurden sind
	dist_li,dist_vorne,dist_re = _all[0] # Distanzwerte
	
	# erhaltene Liste Analysieren
	for entry_conf in alarm_object:
		for entry_found in _list:
			if (entry_conf == entry_found):
				# Falls Objekt aus der Liste gefunden und wir die noch nicht gefunden haben
				# Adden wir es in unseren Speicher
				txt = "Ich habe " + entry_conf + " gefunde."
				print("[ALARM]",txt)
				requests.get('http://localhost:5000/api/sendinfo/'+txt)
				

	# Entscheide Funktion
	if dist_vorne > 100:
		print("-> Option 1")
		move.move(cof.ROBOT_SPEED,'forward','no',0)
		time.sleep(3)
		move.motorStop()
	else:
		print("-> Option 2")
		if dist_li > dist_re:
			fDrive.raw_turn(True, scGear,move) # Links
		else:
			fDrive.raw_turn(False, scGear,move) # Rechts
	scGear.moveAngle(1,0) # Kopf grade ausrichten


def room_scan(scGear, move):
	"""##### Fahrmodus: Raumscannen"""
	# ersten scan Durchgang ausführen
	_all = room_scan_scan(scGear=scGear)
	write_db(_all[1]) # Wir interessieren uns nur für die Werte

	# Robotor macht 180° Drehung
	fDrive.raw_turn(True,scGear,move)
	move.move(cof.ROBOT_SPEED,'backward','no',0)
	time.sleep(0.5)
	fDrive.raw_turn(True,scGear,move)

	_all = room_scan_scan(scGear=scGear)
	write_db(_all[1])
	

def delete_file(filename):
	"""Datei löschen"""
	if os.path.exists(filename): # Wenn Datei vorhanden
		os.remove(filename) # Lösche diese Datei

def init_scan_log():
	""" Initalisierung des Scanlogs"""
	print("[API] init scan log")
	datei = open(cof.LIST_GEGEN,'a')
	dtstr = datetime.now().strftime("%d-%b-%Y--(%H-%M-%S)")
	datei.write("---- {} \r\n".format(dtstr))
	datei.flush()
	datei.close()

def sammler_read_conf():
	"""Einlesen der zu suchenden Objekte"""
	Array = []
	try:
		datei = open(cof.SAMMLER_CONF,'r')
		for zeile in datei:
			zeile = zeile.replace("\n","")
			array_inhalt = zeile.split(",")
			for entry in array_inhalt:
				Array.append(entry)
	except FileNotFoundError:
		pass
	return Array
