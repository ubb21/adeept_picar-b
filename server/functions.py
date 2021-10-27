#!/usr/bin/env python3
# File name   : servo.py
# Description : Control Functions
# Author	  : William
# Date		: 2020/03/17
from json.decoder import JSONDecodeError
import time
from datetime import datetime

# from imports
from requests.exceptions import ReadTimeout, Timeout

# Auf PPC nicht vorhanden
from mpu6050 import mpu6050
import Adafruit_PCA9685
import RPi.GPIO as GPIO
# imports
import requests

import threading

import os
import ultra
import Kalman_filter
import move
import speech
import RPIservo

# import as
import urs_config as cof
import constant as c
import functionHelper as fH
import functionDriving as fDrive


Goings = []
scGear = RPIservo.ServoCtrl()
kordinate = []

move.setup()

# Meine Auswahl Strategien
Strategien = []
"""Strategien"""

sammler_counter = 0
"""Zählvariable der Fehlversuche"""

sammler_gefunden = 0
"""Zählvariable der gefunden Objekte"""

sammler_target = []
"""Liste der zu suchenden Objekte"""

kalman_filter_X =  Kalman_filter.Kalman_filter(0.01,0.1)

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

def num_import_int(initial):        #Call this function to import data from '.txt' file
	global r
	with open(thisPath+"/RPIservo.py") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				r=line
	begin=len(list(initial))
	snum=r[begin:]
	n=int(snum)
	return n

pwm0_direction = 1
pwm0_init = num_import_int('init_pwm0 = ')
pwm0_max  = 520
pwm0_min  = 100
pwm0_pos  = pwm0_init

pwm1_direction = 1
pwm1_init = num_import_int('init_pwm1 = ')
pwm1_max  = 520
pwm1_min  = 100
pwm1_pos  = pwm1_init

pwm2_direction = 1
pwm2_init = num_import_int('init_pwm2 = ')
pwm2_max  = 520
pwm2_min  = 100
pwm2_pos  = pwm2_init

line_pin_right = 20
line_pin_middle = 16
line_pin_left = 19

## Yolo Advance
# Wo zuletzt gefunden
lastObject = 0
"""Zustand des Kopfes des Roboters"""

def pwmGenOut(angleInput):
	return int(round(23/9*angleInput))


def setup():
	""" GPIO Setup für die Funktionen"""
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(line_pin_right,GPIO.IN)
	GPIO.setup(line_pin_middle,GPIO.IN)
	GPIO.setup(line_pin_left,GPIO.IN)


class Functions(threading.Thread):
	def __init__(self, *args, **kwargs):
		self.functionMode = 'none'
		self.steadyGoal = 0

		self.scanNum = 3
		self.scanList = [0,0,0]
		self.scanPos = 1
		self.scanDir = 1
		self.rangeKeep = 0.7
		self.scanRange = 100
		self.scanServo = 1
		self.turnServo = 2
		self.turnWiggle = 200

		setup()

		super(Functions, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()

	def radarScan(self):
		"""Radar Scanner"""
		global pwm0_pos
		scan_speed = 3
		result = []

		if pwm0_direction:
			pwm0_pos = pwm0_max
			pwm.set_pwm(1, 0, pwm0_pos)
			time.sleep(0.8)

			while pwm0_pos>pwm0_min:
				pwm0_pos-=scan_speed
				pwm.set_pwm(1, 0, pwm0_pos)
				dist = ultra.checkdist()
				if dist > 20:
					continue
				theta = 180 - (pwm0_pos-100)/2.55 # +30 deviation
				result.append([dist, theta])
		else:
			pwm0_pos = pwm0_min
			pwm.set_pwm(1, 0, pwm0_pos)
			time.sleep(0.8)

			while pwm0_pos<pwm0_max:
				pwm0_pos+=scan_speed
				pwm.set_pwm(1, 0, pwm0_pos)
				dist = ultra.checkdist()
				if dist > 20:
					continue
				theta = (pwm0_pos-100)/2.55
				result.append([dist, theta])
		pwm.set_pwm(1, 0, pwm0_init)
		return result


	def pause(self):
		"""Thread stoppen"""
		print("Funktion STOP!")
		self.functionMode = 'none'
		move.motorStop()
		self.__flag.clear()


	def resume(self):
		"""Thread anfangen"""
		self.__flag.set()


	def automatic(self):
		self.functionMode = 'Automatic'
		self.resume()


	def trackLine(self):
		self.functionMode = 'trackLine'
		self.resume()


	def keepDistance(self):
		self.functionMode = 'keepDistance'
		self.resume()


	def steady(self,goalPos):
		self.functionMode = 'Steady'
		self.steadyGoal = goalPos
		self.resume()


	def speech(self):
		self.functionMode = 'speechRecProcessing'
		self.resume()

	def kreis_fahrmodus(self):
		"""Kreisfahr Modus"""
		self.functionMode = 'kreis'
		self.resume()
	
	def konst_fahrmodus_v(self):
		"""Konstanter Fahrmodus nach Vorne"""
		self.functionMode = 'konst'
		self.resume()

	def konst_fahrmodus_r(self):
		"""Konstanter Fahrmodus nach Hinten"""
		self.functionMode = 'konst2'
		self.resume()

	def turn_right_processing(self):
		"""Rechts Kurve"""
		self.functionMode = 'turnRight'
		self.resume()

	def turn_left_processing(self):
		"""Links Kurve"""
		self.functionMode = 'turnLeft'
		self.resume()
	
	def yolo_start(self):
		""" Objekterkennungs Modus Nr.1 starten"""
		self.functionMode = 'yolo'
		self.yolo_init()
		self.resume()
	
	def yolo_advance_start(self):
		""" Objekterkennungs Modus Nr.2 starten"""
		self.functionMode = 'yoloAD'
		self.yolo_init()
		self.resume()
	
	def room_scan_start(self):
		""" fast stationärer Raumscan """
		self.functionMode = 'roomScan'
		fH.delete_file(cof.LIST_GEGEN)
		fH.init_scan_log()
		self.yolo_init()
		self.resume()

	def drive_room_scan_start(self):
		""" Fahrender Raum Scanner """
		self.functionMode = 'roomScanSmart'
		fH.delete_file(cof.LIST_GEGEN)
		fH.init_scan_log()
		self.yolo_init()
		self.resume()

	def alarm_start(self):
		""" Alarm Raum Scanner """
		self.functionMode = 'alarm'
		self.yolo_init()
		self.resume()

	def sammel_start(self):
		""" Sammel Modus starten"""
		self.functionMode = 'Object'
		global sammler_counter,sammler_gefunden,sammler_target
		sammler_counter = 0 
		sammler_gefunden = 0
		self.yolo_init()
		self.resume()

    # Processing
	def track_line_processing(self):
		"""Line Tracker"""
		status_right = GPIO.input(line_pin_right)
		status_middle = GPIO.input(line_pin_middle)
		status_left = GPIO.input(line_pin_left)
		#print('R%d   M%d   L%d'%(status_right,status_middle,status_left))
		if status_middle == 0:
			move.motor_left(1, 0, 80)
			move.motor_right(1, 0, 80)
		elif status_left == 0:
			scGear.moveAngle(2, 45)
			move.motor_left(1, 0, 80)
			move.motor_right(1, 0, 80)
		elif status_right == 0:
			scGear.moveAngle(2,-45)
			move.motor_left(1, 0, 80)
			move.motor_right(1, 0, 80)
		else:
			move.motor_left(1, 1, 80)
			move.motor_right(1, 1, 80)
		print(status_left,status_middle,status_right)
		time.sleep(0.1)

	def automatic_processing(self):
		"""Automatischer Modus"""
		print('automaticProcessing')
		scGear.moveAngle(1, 0)
		dist = fH.dist_redress()
		print(dist, "cm")
		time.sleep(0.2)
		if dist >= 40:			# More than 40CM, go straight.
			scGear.moveAngle(2, 0)
			move.motor_left(1, 0, 100)
			move.motor_right(1, 0, 100)
			print("Forward")
		# More than 20cm and less than 40cm, detect the distance between the left and right sides.
		elif dist > 20 and dist < 50:	
			move.motor_left(1, 0, 0)
			move.motor_right(1, 0, 0)
			scGear.moveAngle(1, 30)
			time.sleep(0.3)
			distLeft = fH.dist_redress()
			self.scanList[0] = distLeft

			# Go in the direction where the detection distance is greater.
			scGear.moveAngle(1, -30)
			time.sleep(0.3)
			distRight = fH.dist_redress()
			self.scanList[1] = distRight
			print(self.scanList)
			scGear.moveAngle(1, 0)
			if self.scanList[0] >= self.scanList[1]:
				scGear.moveAngle(2, 30)
				time.sleep(0.3)
				move.motor_left(1, 0, 100)
				move.motor_right(1, 0, 100)
				print("Left")
				time.sleep(1)
			else:
				scGear.moveAngle(2, -30)
				time.sleep(0.3)
				move.motor_left(1, 0, 100)
				move.motor_right(1, 0, 100)
				print("Right")
				time.sleep(1)
		else:		# The distance is less than 20cm, back.
			move.motor_left(1, 1, 100)
			move.motor_right(1, 1, 100)
			print("Back")
			time.sleep(1)

	def speech_rec_processing(self):
		print('speechRecProcessing')
		speech.run()

	def steady_processing(self):
		print('steadyProcessing')
		xGet = sensor.get_accel_data()
		xGet = xGet['x']
		xOut = kalman_filter_X.kalman(xGet)
		pwm.set_pwm(2, 0, self.steadyGoal+pwmGenOut(xOut*9))
		# pwm.set_pwm(2, 0, self.steadyGoal+pwmGenOut(xGet*10))
		time.sleep(0.05)

	def keep_dis_processing(self):
		print('keepDistanceProcessing')
		distanceGet = ultra.checkdist()
		if distanceGet > (self.rangeKeep/2+0.1):
			move.motor_left(1, 0, 80)
			move.motor_right(1, 0, 80)
		elif distanceGet < (self.rangeKeep/2-0.1):
			move.motor_left(1, 1, 80)
			move.motor_right(1, 1, 80)
		else:
			move.motorStop()
	
	def konst_fahrmodus_processing(self):
		""" Konstant fahren nach Vorne (Logik)"""
		if not fDrive.konst_fahrmodus_processing(scGear,move):
			self.pause()
		

	def konst_fahrmodus2_processing(self):
		""" Konstant fahren nach Hinten (Logik)"""
		scGear.moveAngle(1, 10)
		move.move(cof.ROBOT_SPEED,'backward','no',0.3)
		time.sleep(0.3)

	def kreis_fahrmodus_processing(self):
		""" Kreis fahren (Logik)"""
		scGear.moveAngle(2, -30)
		move.move(cof.ROBOT_SPEED,'forward','no',0.6)
		time.sleep(0.3)

	def yolo_einfach(self):
		""" Objekterkennung nur nach Vorne (Logik)"""
		global kordinate
		fDrive.configure_head(scGear)

		# Gegenstands Datei lesen und einspielen
		# Wir können nur ein Gegenstand in diesen Modus tracken.
		gegenstand = ""
		try:
			datei = open(cof.YOLO_CONF)
			gegenstand = datei.readline()
		except FileNotFoundError:
			pass

		# File Not found oder ist leer
		# Es wird anhand der String länge gemessen.
		# cup hat 3 Buchstaben also habe ich 3-1 genommen. Damit ich auf Nummer sicher gehe
		if len(gegenstand) <= 2:
			self.pause()
			return

		# Modus starten
		print("[YOLO] Suche:",gegenstand)
		kordinate = fH.look_normal(1,0, gegenstand,scGear)
		xkordinate= kordinate[0]
		# Strategien überprüfen
		for entry in Strategien:
			if entry.ispossible(xkordinate, self.functionMode, lastObject):
				entry.runs()
				break
	
	def alarm_process(self):
		"""Der Alarm Process wird gestartet"""
		gegenstand = []
		try:
			# Gegenstände einlesen
			datei = open(cof.ALARM_CONF)
			gegenstand = datei.readline().split(",")
		except FileNotFoundError:
			pass
		# Es gibt kein Eintrag in der Konfig --> Pause
		if len(gegenstand) < 1:
			self.pause()
			return
		
		#Modus starten
		fH.alarm_scan(scGear=scGear,self=self,move=move,alarm_object=gegenstand)

		
	def yolo_move(self):
		""" Der Objekt Erkennungserweterung Modus. Der Roboter guckt sich die Umgebung an. (Logik)"""
		global lastObject, Strategien,kordinate
		fDrive.configure_head(scGear)
		
		# Gegenstands Datei lesen und einspielen
		gegenstand = ""
		try:
			# Gegenstände einlesen
			datei = open(cof.YOLO_CONF)
			gegenstand = datei.readline()
			print(gegenstand)
		except FileNotFoundError:
			pass

		if len(gegenstand) <= 2:
				self.pause()

		# Modus starten
		print("[YOLO] Suche:",gegenstand)
		kordinate = fH.yolo_look_advance(gegenstand,scGear,lastObject)
		xkordinate= kordinate[0]
		print("[YOLO] Strategie Eingabe: x={}, Mode={} und lastObject={}".format(xkordinate, self.functionMode, lastObject))

		# Strategien überprüfen
		for entry in Strategien:
			if entry.ispossible(xkordinate, self.functionMode, lastObject):
				entry.runs()
				break
		
	def yolo_init(self):
		""" Initalisiere die Stategien"""
		global Strategien
		if len(Strategien) == 0:
			Strategien = fH.init_strategien(self=self)
	

	def sammel_back(self):
		""" Sammel-Modus: Wenn Objekt gefunden fahre zurück"""
		print("Sammler gefunden")
		global sammler_gefunden,sammler_target,sammler_counter
		# Zählvariable für gefundene Objekte
		sammler_gefunden = sammler_gefunden +1
		# Zählvariable der Fehlversuche
		sammler_counter = 0
		move.move(cof.ROBOT_SPEED, 'backward','no',0)
		time.sleep(3)
		move.motorStop()
		if sammler_gefunden >= len(sammler_target):
			self.pause()	

	def sammel_counter(self):
		"""Sammel-Modus:  Last Object Counter"""
		global lastObject, sammler_counter
		lastObject = lastObject + 1
		if lastObject == 5:
			lastObject = 0	
			# Zählvariable der Fehlversuche erhöhen
			sammler_counter = sammler_counter + 1
			print("[Sammel] Fehlversuch:",sammler_counter)
			if sammler_counter == 3:
				# Vor dir ist das Objekt nicht, also drehe dich um 180°
				fDrive.raw_turn(True,scGear,move)
				move.move(cof.ROBOT_SPEED,'backward','no',0)
				time.sleep(0.5)
				fDrive.raw_turn(True,scGear,move)
			if sammler_counter == 6:
				# Objekt ist wirklich nicht da
				# Beende den Modus
				self.sammel_back()

	def yolo_turn_rightmittig(self):
		"""45 Grad Kurve nach Rechts"""
		self.yolo_counter()
		fDrive.raw_turns(-1,0.5,scGear,move)

	def yolo_turn_right(self):
		"""90 Grad Kurve nach Rechts"""
		self.yolo_counter()
		fDrive.raw_turn(False,scGear,move)
	
	def yolo_turn_leftmittig(self):
		"""45 Grad Kurve nach Links"""
		self.yolo_counter()
		fDrive.raw_turns(1,0.5,scGear,move)

	def yolo_turn_left(self):
		"""90 Grad Kurve nach Links"""
		self.yolo_counter()
		fDrive.raw_turns(1,1.2,scGear,move)

	def yolo_counter(self):
		"""YOLO Lst Object Counter"""
		global lastObject
		lastObject = lastObject +1
		if lastObject == 5:
			lastObject = 0
	
	# Eine Rechtskurve machen
	def turnRight(self):
		""" Rechts Kurve machen (Aufruf)"""
		fDrive.raw_turn(False,scGear,move)
		self.pause()

	# Eine Linkskurve machen
	def turnLeft(self):
		"""Links Kurve machen (Aufruf)"""
		fDrive.raw_turn(True,scGear,move)
		self.pause()

	def room_scan(self):
		""" Room Scanner Funktions (Aufruf)"""
		fH.room_scan(scGear, move)
		self.pause()
	
	def fahr_rechts(self):
		"""Rechts Fahren"""
		print("[API] >> rechts")
		scGear.moveAngle(2, -30)
		move.move(cof.ROBOT_SPEED,'forward','no',0.1)
		time.sleep(0.8)
		move.motorStop()
		
	def fahr_links(self):
		"""Links fahren"""
		print("[API] << links")
		scGear.moveAngle(2, 30)
		move.move(cof.ROBOT_SPEED,'forward','no',0.1)
		time.sleep(0.8)
		move.motorStop()

	def fahr_gradeaus(self):
		"""Grade aus fahren"""
		print("[API] ==")
		print("Gloable Koordienaten", kordinate)
		scGear.moveAngle(2, 10)
		move.move(cof.ROBOT_SPEED,'forward','no',0.1)	
		if kordinate[2] <= 50: 
			# kordinate[2] ist die width des Erkanntes Objektes
			# je kleiner die Zahl, desto weiter entfernt ist das Objekt
			time.sleep(3)
		elif kordinate[2]	<= 75:
			time.sleep(2)
		else:
			time.sleep(1)	
		move.motorStop()

	def drive_scan(self):
		"""Überreiche Funktion an andere Datei weiter"""
		fH.drive_scan(scGear,move)

	def sammel_process(self):
		global kordinate,sammler_target
		""" Sammelprozess Funktionen starter"""
		global lastObject, Strategien,sammler_gefunden,sammler_target
		fDrive.configure_head(scGear)
		
		# Sammel Liste einlesen
		sammler_target = fH.sammler_read_conf()
		print(sammler_target)
		
		try:
			# Das zu suchende Objekt anzeigen
			print("Suche: "+sammler_target[sammler_gefunden])
		except IndexError:
			self.pause()
			return	
		if sammler_target[sammler_gefunden] == "" or sammler_target[sammler_gefunden] == " ":
			print("Empty String")
			self.pause()
		kordinate = fH.yolo_look_advance(sammler_target[sammler_gefunden],scGear,lastObject)
		xkordinate= kordinate[0]
		print("[Sammler] Strategie Eingabe: x={}, Mode={} und lastObject={}".format(xkordinate, self.functionMode, lastObject))
		for entry in Strategien:
			if entry.ispossible(xkordinate, self.functionMode, lastObject):
				entry.runs()
				break

	# Thread Auswahl
	def function_going(self):
		global Goings
		"""Thread Optionsauswahl"""
		if len(Goings) == 0:
			Goings = fH.init_function_entscheider(self)
		for entry in Goings:
			if entry.ispossible(self.functionMode):
				entry.run0()
				break
			

	def run(self):
		while 1:
			self.__flag.wait()
			self.function_going()


if __name__ == '__main__':
	Fuc = Functions()

