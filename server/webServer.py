#!/usr/bin/env/python
# File name   : server.py
# Production  : GWR
# Website     : www.adeept.com
# Author      : William
# Date        : 2020/03/17

import time
import threading

import sqlalchemy
import move
import Adafruit_PCA9685
import os
import info
import RPIservo
import ultra

import functions
import robotLight
import switch
import socket

#websocket
import asyncio
import websockets

import json
import app

import webHelper

# Arrays
FuncEntscheider = []
RobotEntscheider = []
SwitchEntscheider = []
configEntscheider = []

functionMode = 0
speed_set = 100
rad = 0.5
turnWiggle = 60

manPlusModus = 0
einrasten = 0
blockForwardSetting = 0

scGear = RPIservo.ServoCtrl()
scGear.moveInit()

P_sc = RPIservo.ServoCtrl()
P_sc.start()

T_sc = RPIservo.ServoCtrl()
T_sc.start()


# modeSelect = 'none'
modeSelect = 'PT'

init_pwm0 = scGear.initPos[0]
init_pwm1 = scGear.initPos[1]
init_pwm2 = scGear.initPos[2]
init_pwm3 = scGear.initPos[3]
init_pwm4 = scGear.initPos[4]

fuc = functions.Functions()
fuc.start()

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

direction_command = 'no'
turn_command = 'no'

def servoPosInit():
	scGear.initConfig(2,init_pwm2,1)
	P_sc.initConfig(1,init_pwm1,1)
	T_sc.initConfig(0,init_pwm0,1)


def replace_num(initial,new_num):   #Call this function to replace data in '.txt' file
	global r
	newline=""
	str_num=str(new_num)
	with open(thisPath+"/RPIservo.py","r") as f:
		for line in f.readlines():
			if(line.find(initial) == 0):
				line = initial+"%s" %(str_num+"\n")
			newline += line
	with open(thisPath+"/RPIservo.py","w") as f:
		f.writelines(newline)


def FPV_thread():
	global fpv
	fpv=FPV.FPV()
	fpv.capture_thread(addr[0])


def ap_thread():
	os.system("sudo create_ap wlan0 eth0 Adeept_Robot 12345678")

### Function Methoden ###
def scanner(response,modeSelect):
	if modeSelect == 'PT':
			radar_send = fuc.radarScan()
			response['title'] = 'scanResult'
			response['data'] = radar_send
			time.sleep(0.3)

def findColor(response,modeSelect):
	if modeSelect == 'PT':
		flask_app.modeselect('findColor')

def watchDog(response,modeSelect):
	flask_app.modeselect('watchDog')

def stopCV(response,modeSelect):
	flask_app.modeselect('none')
	switch.switch(1,0)
	switch.switch(2,0)
	switch.switch(3,0)
	move.motorStop()

def KD(response,modeSelect):
	servoPosInit()
	fuc.keepDistance()
	RL.police()

def automaticOff(response,modeSelect):
	RL.pause()
	fuc.pause()
	scGear.moveAngle(2,0)
	move.motorStop()
	time.sleep(0.3)
	move.motorStop()

def automatic(response,modeSelect):
	RL.pause()
	RL.breath(125,255,3)
	if modeSelect == 'PT':
		fuc.automatic()
	else:
		fuc.pause()

def trackLine(response,modeSelect): # 
	servoPosInit()
	fuc.trackLine()

def trackLineOff(response,modeSelect): # Äquivalent zu steadyCamera
	fuc.pause()
	move.motorStop(response,modeSelect)

def steady_camera(response,modeSelect):
	fuc.steady(T_sc.lastPos[2])

def speech(response,modeSelect):
	RL.both_off()
	fuc.speech()

def speech_off(response,modeSelect):
	RL.both_off()
	fuc.pause()
	move.motorStop()
	time.sleep(0.3)
	move.motorStop()

def kreis(response,modeSelect): # Kreisfahrmodus
	RL.breath(0,85,128) # Dark cerulean
	fuc.kreis_fahrmodus()

def konst(response,modeSelect):
	RL.breath(251,255,230) # Light yellow
	fuc.konst_fahrmodus_v()

def konst2(response,modeSelect):
	RL.breath(150,0,4) # rot
	fuc.konst_fahrmodus_r()

def turnRight(response,modeSelect):
	RL.breath(255,153,187) # Pastel magenta
	RL.turnRight()
	fuc.turnRight()

def turnLeft(response,modeSelect):
	RL.breath(153,25,0) # Rufous
	RL.turnLeft()
	fuc.turnLeft()

def yolo(response,modeSelect):
	RL.pause()
	RL.both_on()
	RL.setColor(24,255,0)
	RL.breath(24,255,0) # Farbe: Hellgrün
	fuc.yolo_start()

def yolo_ad(response,modeSelect):
	RL.pause()
	RL.both_on()
	RL.breath(255,178,0) # Farbe Dunkel Orange
	RL.setColor(255,178,0)
	fuc.yolo_advance_start()

def man_plus(response,modeSelect):
	global manPlusModus
	print("Wechsel auf Manueller Plus Modus")
	manPlusModus = 1

def man(response,modeSelect):
	global manPlusModus
	print("Wechsel auf Manueller Modus")
	manPlusModus = 0

def room_scan(response,modeSelect):
	RL.breath(204,0,102)
	fuc.room_scan_start()

def smart_scan(response,modeSelect):
	RL.breath(179,179,255) # Pale cornflower blue
	fuc.drive_room_scan_start()

def alarmfunc(command_input,response):
	""" Alarm Funktion starten """
	print("ALARM")
	fuc.alarm_start()
	RL.breath(255,153,238) # Napier green

def objectfunc(c,r):
	""" Objekt Sammeln starten"""
	print("Object Sammeln")
	fuc.sammel_start()
	RL.breath(68,102,0) # Lavender Rosa

def init_function_entscheider():
	if len(FuncEntscheider) == 0:
		print("[API] init_function_entscheider")
		# Voreingestellt
		FuncEntscheider.append(webHelper.Entscheider('scan',scanner))
		FuncEntscheider.append(webHelper.Entscheider('findColor',findColor))
		FuncEntscheider.append(webHelper.Entscheider('motionGet',watchDog))
		FuncEntscheider.append(webHelper.Entscheider('stopCV',stopCV))
		FuncEntscheider.append(webHelper.Entscheider('KD',KD))
		FuncEntscheider.append(webHelper.Entscheider('automaticOff',automaticOff))
		FuncEntscheider.append(webHelper.Entscheider('automatic',automatic))
		FuncEntscheider.append(webHelper.Entscheider('trackLine',trackLine))
		FuncEntscheider.append(webHelper.Entscheider('trackLineOff',trackLineOff))
		FuncEntscheider.append(webHelper.Entscheider('steadyCameraOff',trackLineOff))
		FuncEntscheider.append(webHelper.Entscheider('steadyCamera',steady_camera))
		FuncEntscheider.append(webHelper.Entscheider('speech',speech))
		FuncEntscheider.append(webHelper.Entscheider('speechOff',speech_off))
		
		# Meine Modi
		FuncEntscheider.append(webHelper.Entscheider('kreis',kreis)) # Kreisfahren
		FuncEntscheider.append(webHelper.Entscheider('konst',konst)) # Vorwärtsfahren
		FuncEntscheider.append(webHelper.Entscheider('konst2',konst2)) # Rückwärtsfahren
		FuncEntscheider.append(webHelper.Entscheider('turnRight',turnRight)) # Rechts Kruve
		FuncEntscheider.append(webHelper.Entscheider('turnLeft',turnLeft)) # Links Kurve
		FuncEntscheider.append(webHelper.Entscheider('yolo',yolo)) # YOLO Nr. 1
		FuncEntscheider.append(webHelper.Entscheider('yoloAD',yolo_ad)) # YOLO Nr. 2
		FuncEntscheider.append(webHelper.Entscheider('roomScan',room_scan)) # Raum Scanner
		FuncEntscheider.append(webHelper.Entscheider('manPlus',man_plus)) # Manueller Plus Modi
		FuncEntscheider.append(webHelper.Entscheider('man',man)) # Manueller Modus
		FuncEntscheider.append(webHelper.Entscheider('fahrScan',smart_scan)) # Smart Scann
		# alarm ; Object
		FuncEntscheider.append(webHelper.Entscheider('alarm',alarmfunc))
		FuncEntscheider.append(webHelper.Entscheider('Object',objectfunc))

def function_select(command_input, response):
	global functionMode, manPlusModus
	init_function_entscheider()
	for option in FuncEntscheider:
		if option.ispossible(command_input):
			option.run2(response,modeSelect)		
	

### Switch Controll ###
def Switch_1_on():
	switch.switch(1,1)
def Switch_1_off():
	switch.switch(1,0)

def Switch_2_on():
	switch.switch(2,1)
def Switch_2_off():
	switch.switch(2,0)

def Switch_3_on():
	switch.switch(3,1)
def Switch_3_off():
	switch.switch(3,0) 


def init_switch():
	if len(SwitchEntscheider) == 0:
		print("[API] init_switch")
		SwitchEntscheider.append(webHelper.Entscheider('Switch_1_on',Switch_1_on))
		SwitchEntscheider.append(webHelper.Entscheider('Switch_1_off',Switch_1_off))
		SwitchEntscheider.append(webHelper.Entscheider('Switch_2_on',Switch_2_on))
		SwitchEntscheider.append(webHelper.Entscheider('Switch_2_off',Switch_2_off))
		SwitchEntscheider.append(webHelper.Entscheider('Switch_3_on',Switch_3_on))
		SwitchEntscheider.append(webHelper.Entscheider('Switch_3_off',Switch_3_off))

def switch_ctrl(command_input, response):
	init_switch()
	for option in SwitchEntscheider:
		if option.ispossible(command_input):
			option.run0()
		


### Robot Entscheider ###
def forward():
	global direction_command, manPlusModus,einrasten
	direction_command = 'forward'
	if manPlusModus == 1:
		if einrasten == 0:
			einrasten = 1
			fuc.konst_fahrmodus_v()
		else:
			einrasten = 0
			fuc.pause()
	else:
		move.motor_left(1, 0, speed_set)
		move.motor_right(1, 0, speed_set)
	RL.both_on()
	RL.breath(255,255,255)

def backward():
	global direction_command, einrasten, manPlusModus
	direction_command = 'backward'
	if manPlusModus == 1:
		if einrasten == 0:
			einrasten = 1
			fuc.konst_fahrmodus_r()
		else:
			einrasten = 0
			fuc.pause()
	else:
		move.motor_left(1, 1, speed_set)
		move.motor_right(1, 1, speed_set)
	RL.red()
	RL.breath(255,0,0)

def ds():
	global direction_command, manPlusModus
	if manPlusModus == 0:
		direction_command = 'no'
		move.motorStop()
		if turn_command == 'left':
			RL.both_off()
			RL.turnLeft()
		elif turn_command == 'right':
			RL.both_off()
			RL.turnRight()
		elif turn_command == 'no':
			RL.both_off()

# Bewege Vorderräder nach links
def left():
	global turn_command
	turn_command = 'left'
	scGear.moveAngle(2, 30)
	RL.both_off()
	RL.turnLeft()

# Bewege Vorderräder nach rechts
def right():
	global turn_command
	turn_command = 'right'
	scGear.moveAngle(2,-30)
	RL.both_off()
	RL.turnRight()

def ts():
	global turn_command, direction_command
	turn_command = 'no'
	scGear.moveAngle(2, 0)
	if direction_command == 'forward':
		RL.both_on()
	elif direction_command == 'backward':
		RL.both_off()
		RL.red()
	elif direction_command == 'no':
		RL.both_off()

def lookleft():
	P_sc.singleServo(1, 1, 7)

def lookright():
	P_sc.singleServo(1,-1, 7)

def lr_stop():
	P_sc.stopWiggle()

def up():
	T_sc.singleServo(0, -1, 7)

def down():
	T_sc.singleServo(0,1, 7)

def ud_stop():
	T_sc.stopWiggle()

def home():
	P_sc.moveServoInit([init_pwm1])
	T_sc.moveServoInit([init_pwm0])
	G_sc.moveServoInit([init_pwm2])



def init_robot_ctrl():
	global RobotEntscheider
	if len(RobotEntscheider) == 0:
		print("[API] init_robotCtrl")
		RobotEntscheider.append(webHelper.Entscheider('forward',forward))
		RobotEntscheider.append(webHelper.Entscheider('backward',backward))
		RobotEntscheider.append(webHelper.Entscheider('DS',ds))
		RobotEntscheider.append(webHelper.Entscheider('left',left))
		RobotEntscheider.append(webHelper.Entscheider('right',right))
		RobotEntscheider.append(webHelper.Entscheider('TS',ts))
		RobotEntscheider.append(webHelper.Entscheider('lookleft',lookleft)) # Bewege Vorderräder nach links
		RobotEntscheider.append(webHelper.Entscheider('lookright',lookright))
		RobotEntscheider.append(webHelper.Entscheider('LRstop',lr_stop))
		RobotEntscheider.append(webHelper.Entscheider('up',up)) # Bewege Vorderräder nach links
		RobotEntscheider.append(webHelper.Entscheider('down',down))
		RobotEntscheider.append(webHelper.Entscheider('UDstop',ud_stop))
		RobotEntscheider.append(webHelper.Entscheider('home',home)) # Bewege Vorderräder nach links


# Roboter Kontrolle
def robot_ctrl(command_input, response):
	global direction_command, turn_command, einrasten, manPlusModus, functionMode,speed_set
	#print("webServer-robotCtrl: ",einrasten)
	init_robot_ctrl()
	for option in RobotEntscheider:
		if option.ispossible(command_input):
			option.run0()
	
### Config Entscheider ###
def SiLeft(command_input):
	global init_pwm0, init_pwm1, init_pwm2
	numServo = int(command_input[7:])
	if numServo == 0:
		init_pwm0 -= 1
		T_sc.setPWM(0,init_pwm0)
	elif numServo == 1:
		init_pwm1 -= 1
		P_sc.setPWM(1,init_pwm1)
	elif numServo == 2:
		init_pwm2 -= 1
		scGear.setPWM(2,init_pwm2)

def SiRight(command_input):
	global init_pwm0, init_pwm1, init_pwm2
	numServo = int(command_input[8:])
	if numServo == 0:
		init_pwm0 += 1
		T_sc.setPWM(0,init_pwm0)
	elif numServo == 1:
		init_pwm1 += 1
		P_sc.setPWM(1,init_pwm1)
	elif numServo == 2:
		init_pwm2 += 1
		scGear.setPWM(2,init_pwm2)

def PWMMS(command_input):
	global init_pwm0, init_pwm1, init_pwm2
	numServo = int(command_input[6:])
	if numServo == 0:
		T_sc.initConfig(0, init_pwm0, 1)
		replace_num('init_pwm0 = ', init_pwm0)
	elif numServo == 1:
		P_sc.initConfig(1, init_pwm1, 1)
		replace_num('init_pwm1 = ', init_pwm1)
	elif numServo == 2:
		scGear.initConfig(2, init_pwm2, 2)
		replace_num('init_pwm2 = ', init_pwm2)
	
def PWMINIT():
	global init_pwm1
	print(init_pwm1)
	servoPosInit()

def PWMD():
	global init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4
	init_pwm0,init_pwm1,init_pwm2,init_pwm3,init_pwm4=300,300,300,300,300
	T_sc.initConfig(0,300,1)
	replace_num('init_pwm0 = ', 300)

	P_sc.initConfig(1,300,1)
	replace_num('init_pwm1 = ', 300)

	scGear.initConfig(2,300,1)
	replace_num('init_pwm2 = ', 300)


def init_config():
	if len(configEntscheider) == 0:
		print("[API] init_config")
		configEntscheider.append(webHelper.Entscheider('SiLeft',SiLeft))
		configEntscheider.append(webHelper.Entscheider('SiRight',SiRight))
		configEntscheider.append(webHelper.Entscheider('PWMMS',PWMMS))

		configEntscheider.append(webHelper.Entscheider('PWMINIT',PWMINIT))
		configEntscheider.append(webHelper.Entscheider('PWMD',PWMD))


# Config PWN
def configPWM(command_input, response):
	global init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4
	init_config()
	for option in configEntscheider:
		if option.ispossible(command_input):
			option.run1(command_input)

		


def update_code():
	# Update local to be consistent with remote
	projectPath = thisPath[:-7]
	with open(f'{projectPath}/config.json', 'r') as f1:
		config = json.load(f1)
		if not config['production']:
			print('Update code')
			# Force overwriting local code
			if os.system(f'cd {projectPath} && sudo git fetch --all && sudo git reset --hard origin/master && sudo git pull') == 0:
				print('Update successfully')
				print('Restarting...')
				os.system('sudo reboot')
			
def wifi_check():
	try:
		s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		s.connect(("1.1.1.1",80))
		ipaddr_check=s.getsockname()[0]
		s.close()
		print(ipaddr_check)
		update_code()
	except:
		#ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
		#ap_threading.ssetDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
		#ap_threading.start()                                  #Thread starts
		RL.setColor(0,16,50)
		time.sleep(1)
		RL.setColor(0,16,100)
		time.sleep(1)
		RL.setColor(0,16,150)
		time.sleep(1)
		RL.setColor(0,16,200)
		time.sleep(1)
		RL.setColor(0,16,255)
		time.sleep(1)
		RL.setColor(35,255,35)

async def check_permit(websocket):
	while True:
		recv_str = await websocket.recv()
		cred_dict = recv_str.split(":")
		if cred_dict[0] == "admin" and cred_dict[1] == "123456":
			response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
			await websocket.send(response_str)
			return True
		else:
			response_str = "sorry, the username or password is wrong, please submit again"
			await websocket.send(response_str)

async def recv_msg(websocket):
	global speed_set, modeSelect, direction_command, turn_command
	move.setup()
	direction_command = 'no'
	turn_command = 'no'

	while True: 
		response = {
			'status' : 'ok',
			'title' : '',
			'data' : None
		}

		data = ''
		data = await websocket.recv()
		try:
			#print(data)
			data = json.loads(data)
			
		except Exception as e:
			print('not A JSON')

		if not data:
			continue

		if isinstance(data,str):
			if 'test' == data:
				continue

			robot_ctrl(data, response)

			switch_ctrl(data, response)

			function_select(data, response)

			configPWM(data, response)

			if 'get_info' == data:
				response['title'] = 'get_info'
				response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

			# Speed einstellen
			if 'wsB' in data:
				try:
					set_B=data.split()
					speed_set = int(set_B[1])
				except:
					pass

			elif 'AR' == data:
				modeSelect = 'AR'
				screen.screen_show(4, 'ARM MODE ON')
				try:
					fpv.changeMode('ARM MODE ON')
				except:
					pass

			elif 'PT' == data:
				modeSelect = 'PT'
				screen.screen_show(4, 'PT MODE ON')
				try:
					fpv.changeMode('PT MODE ON')
				except:
					pass

			#CVFL
			elif 'CVFL' == data:
				flask_app.modeselect('findlineCV')

			elif 'CVFLColorSet' in data:
				color = int(data.split()[1])
				flask_app.camera.colorSet(color)

			elif 'CVFLL1' in data:
				pos = int(data.split()[1])
				flask_app.camera.linePosSet_1(pos)

			elif 'CVFLL2' in data:
				pos = int(data.split()[1])
				flask_app.camera.linePosSet_2(pos)

			elif 'CVFLSP' in data:
				err = int(data.split()[1])
				flask_app.camera.errorSet(err)

			elif 'defEC' in data:#Z
				fpv.defaultExpCom()

		elif(isinstance(data,dict)):
			if data['title'] == "findColorSet":
				color = data['data']
				flask_app.colorFindSet(color[0],color[1],color[2])

		#print(data)
		response = json.dumps(response)
		if websocket is not None:
			await websocket.send(response)

async def main_logic(websocket, path):
	await check_permit(websocket)
	await recv_msg(websocket)

if __name__ == '__main__':
	switch.switchSetup()
	switch.set_all_switch_off()

	HOST = ''
	PORT = 10223                              #Define port serial 
	BUFSIZ = 1024                             #Define buffer size
	ADDR = (HOST, PORT)

	global flask_app
	flask_app = app.webapp()
	flask_app.startthread()

	try:
		RL=robotLight.RobotLight()
		RL.start()
		RL.breath(70,70,255)
	except:
		print('Use "sudo pip3 install rpi_ws281x" to install WS_281x package\n使用"sudo pip3 install rpi_ws281x"命令来安装rpi_ws281x')
		pass

	while  1:
		wifi_check()
		try:                  #Start server,waiting for client
			start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
			asyncio.get_event_loop().run_until_complete(start_server)
			print('waiting for connection...')
			# print('...connected from :', addr)
			break
		except Exception as e:
			print(e)
			RL.setColor(0,0,0)

		try:
			RL.setColor(0,80,255)
		except:
			pass
	try:
		asyncio.get_event_loop().run_forever()
	except Exception as e:
		print(e)
		RL.setColor(0,0,0)
		move.destroy()
