import move
import servo
import ultra
import time
import Adafruit_PCA9685
import RGB
import robotLight

try:
  RL=robotLight.RobotLight()
  RL.start()
  RL.breath(70,70,255)
  print("Sucess")
except:
  print("No")
  exit()

time.sleep(5)
RL.pause()
print("1")
RL.setColor(255,0,0)
time.sleep(5)
print("2")
RL.pause()
RL.setColor(0,255,0)
time.sleep(5)
print("3")
RL.setColor(0,0,0)
print("Ende")
