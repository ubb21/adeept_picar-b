import cv2
import numpy as np
import imutils

DARKNET_PATH = 'C:/Users/Schutz/Documents/adeep_roboter/detect/'
IMAGE_PATH = 'C:/Users/Schutz/Documents/adeep_roboter/'

# Load Yolo
net = cv2.dnn.readNet(DARKNET_PATH+"yolov3.weights", DARKNET_PATH+"cfg/yolov3.cfg")
classes = []
with open(DARKNET_PATH+"data/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))


# repalce the test.mp4 with an video of your own 
camera = cv2.VideoCapture(DARKNET_PATH+"robot.mp4")

fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
frame_width = int(1920)
frame_height = int(1080)
dim = (frame_width, frame_height) 
outVi = cv2.VideoWriter(DARKNET_PATH+"the_new_video_is.avi", fourcc , 25, (frame_width,frame_height))

while True:
    ret,img = camera.read()
    height, width, channels = img.shape
    #print(height, ":",width)

    if ret == True:
        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (320, 320), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        # Showing informations on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[i]
                label = "{}: {:.4f}".format(label, confidences[i])
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 3, color, 3)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        #cv2.imshow("Image", img)
        outVi.write(img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

camera.release()
outVi.release()
cv2.destroyAllWindows()
