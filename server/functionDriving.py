import time
import functionHelper as fH
import urs_config as cof


def raw_turn(leftorright: bool,scGear,move):
	"""##### Rechts oder Links fahren: 
	 True == Links 
	 False == Rechts"""
	if leftorright:
		raw_turns(1,1,scGear,move) # Links
	else:
		raw_turns(-1,1,scGear,move) # Rechts

def raw_turns( lenkungsfaktor, zeitfaktor: float, scGear, move):
	"""##### eigentliche Kurven Logik
	1: Links
	-1: Rechts"""
	try:
		datei = open(cof.ZEITFAKTOR,"r")
		untergrundzeitfaktor = float(datei.readline().split(",")[0])
		datei.close()
	except FileNotFoundError:
		untergrundzeitfaktor = 2
	robot_speed_turn = 100
	if lenkungsfaktor == 1 or lenkungsfaktor == -1:			
		scGear.moveAngle(2, 0) # Lenker ausrichten
		time.sleep(0.5)
		scGear.moveAngle(2, lenkungsfaktor*30) # Nach vorne links lenken
		move.move(robot_speed_turn,'forward','no',0.9)
		time.sleep(untergrundzeitfaktor*zeitfaktor) # Land 3

		scGear.moveAngle(2, lenkungsfaktor*-30) # NAch rechts hinten
		move.move(robot_speed_turn, 'backward','left',0.9)
		time.sleep(untergrundzeitfaktor*zeitfaktor)# Land 3

		scGear.moveAngle(2, lenkungsfaktor*30) # Nach vorne links lenken
		move.move(robot_speed_turn,'forward','no',0.9)
		time.sleep(untergrundzeitfaktor*zeitfaktor*0.5) # Land 2

		move.motorStop()
		scGear.moveAngle(2, 10) # Lenker ausrichten
	else:
		raise ValueError("The value must be -1 or 1")


def configure_head(scGear):
	"""##### Kopf Ausrichten"""
	print("[YOLO] configureHead")
	scGear.moveAngle(0, 10) # Oben/Unten Ausrichtung
	scGear.moveAngle(1, 0) # Links Rechts Ausrichtung (grade aus)
	scGear.moveAngle(2, 10)

def konst_fahrmodus_processing(scGear,move):
	"""##### Fahrmodus: Vorwärtsfahren"""
	scGear.moveAngle(1, 10)
	dist = fH.dist_redress()
	time.sleep(0.2)
	print(dist)
	if dist >= 60:
		move.move(cof.ROBOT_SPEED,'forward','no',0.3)
		time.sleep(0.3)
		return True
	else:
		return False