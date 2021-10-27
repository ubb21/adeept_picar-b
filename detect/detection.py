import cv2 
import numpy as np
import os

import json
from json import JSONEncoder

##DARKNET_PATH = 'D:/adeep_roboter/detect'
#IMAGE_PATH = 'D:/adeep_roboter/'

DARKNET_PATH = 'C:/Users/Schutz/Documents/adeep_roboter/detect'
IMAGE_PATH = 'C:/Users/Schutz/Documents/adeep_roboter/'

class seeObject():
    x = 0
    y = 0
    w = 0
    h = 0
    text = ""

    def __init__(self,x,y,w,h,text):
        self.seting(x,y,w,h,text)

    def seting(self,x,y,w,h,text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
    
    def __iter__(self):
        yield from {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "text": self.text
        }.items()
    
    def __str__(self):
        return json.dumps(dict(self), cls=MyEncoder)

    def __repr__(self) -> str:
        return self.__str__()

class MyEncoder(JSONEncoder):
    def default(self, obj):
        return obj.__dict__

def detect_obj_list(path):
  JSON_string = str("")
  # Read labels that are used on object
  labels = open(os.path.join(DARKNET_PATH, "data", "coco.names")).read().splitlines() # Namen der gelernten Objekte
  #print(labels) # alle Erkennbare dinger ausgeben
  # Erstelle zufällige Farben mit einem Samen, so dass sie beim nächsten Mal die gleichen sind
  np.random.seed(0)
  colors = np.random.randint(0, 255, size=(len(labels), 3)).tolist()

  # Geben Sie die Konfigurations- und Gewichtsdateien für das Modell an und laden Sie das Netz.
  net = cv2.dnn.readNetFromDarknet(os.path.join(DARKNET_PATH, "cfg", "yolov3.cfg"), os.path.join(DARKNET_PATH,"yolov3.weights"))
  # Bestimmen Sie die Ausgabeschicht, dieser Teil ist nicht intuitiv
  ln = net.getLayerNames()
  ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

  image = cv2.imread(path)

  # Get the shape
  h, w = image.shape[:2]
  # Als Blob laden und in das Netz einspeisen
  blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
  net.setInput(blob)

  # Abrufen der Ausgabe
  layer_outputs = net.forward(ln)


  # Initialisierung der Listen, die wir zur Interpretation der Ergebnisse benötigen
  boxes = []
  confidences = []
  class_ids = []

  # Loop over the layers
  for output in layer_outputs:
      # For the layer loop over all detections
      for detection in output:
          # The detection first 4 entries contains the object position and size
          scores = detection[5:]
          # Then it has detection scores - it takes the one with maximal score
          class_id = np.argmax(scores).item()
          # The maximal score is the confidence
          confidence = scores[class_id].item()

          # Ensure we have some reasonable confidence, else ignorre
          if confidence > 0.3:
              # The first four entries have the location and size (center, size)
              # It needs to be scaled up as the result is given in relative size (0.0 to 1.0)
              box = detection[0:4] * np.array([w, h, w, h])
              center_x, center_y, width, height = box.astype(int).tolist()

              # Calculate the upper corner
              x = center_x - width//2
              y = center_y - height//2

              # Add our findings to the lists
              boxes.append([x, y, width, height])
              confidences.append(confidence)
              class_ids.append(class_id)

  # Nur die besten Boxen der sich überschneidenden Boxen behalten
  idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.3)

  # Ensure at least one detection exists - needed otherwise flatten will fail
  Obj1 = seeObject(0,0,0,0,"None")
  if len(idxs) > 0:
      # Loop over the indexes we are keeping
      for i in idxs.flatten():
          # Informationen über die Box abrufen
          x, y, w, h = boxes[i]
          #  Erstellen Sie ein Rechteck
          cv2.rectangle(image, (x, y), (x + w, y + h), colors[class_ids[i]], 2)
          # Text erstellen und hinzufügen
          text = "{}: {:.4f}".format(labels[class_ids[i]], confidences[i])
          cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[class_ids[i]], 1)
          Obj1.seting(x,y,w,h, labels[class_ids[i]])
          JSON_string = JSON_string + "|" + json.dumps(dict(Obj1), cls=MyEncoder)
  cv2.rectangle(image,(0,0),(10,10),(255,0,0))
  #cv2.imwrite(os.path.join(path + "-detect.jpg"), image)
  return JSON_string

if __name__ == '__main__':
    detect_obj_list("20-Oct-2021--(08-07-04).jpg")