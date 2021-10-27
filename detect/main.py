# Flask
from flask import Flask
from PIL import Image


# System
import base64
from io import BytesIO
import requests
from datetime import datetime

# Lgogging
import logging

import os

# Recognization
import detection as detect

# Flask API
app = Flask(__name__)

# time
import time

#Logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

import socket
print(socket.gethostbyname(socket.gethostname()))

# Routing
@app.route('/')
def home():
    return 'It works! by Urs'

@app.route("/send-image/<path:url>")
def image_check2(url):
    status = "None" 
    file_name_for_base64_data = datetime.now().strftime("%d-%b-%Y--(%H-%M-%S)")
    file_name_for_regular_data = url[-10:-4]
    try:
        # Base64 DATA JPEG
        if "data:image/jpeg;base64," in url:
            base_string = url.replace("data:image/jpeg;base64,", "")
            decoded_img = base64.b64decode(base_string)
            img = Image.open(BytesIO(decoded_img))

            file_name = file_name_for_base64_data + ".jpg"
            img.save(detect.IMAGE_PATH + file_name, "jpeg")
            time.sleep(0.2)

            status = detect.detect_obj_list(detect.IMAGE_PATH + file_name)
            print(file_name_for_base64_data, ":", status)

            os.remove(detect.IMAGE_PATH + file_name)

        # Base64 DATA PNG
        elif "data:image/png;base64," in url:
            base_string = url.replace("data:image/png;base64,", "")
            decoded_img = base64.b64decode(base_string)
            img = Image.open(BytesIO(decoded_img))

            file_name = file_name_for_base64_data + ".png"
            img.save(file_name, "png")
            status = detect.detect_obj_list(file_name)
            print(file_name_for_base64_data, ":", status)
            os.remove(file_name)

        else:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            file_name = file_name_for_regular_data + ".jpg"
            img.save(file_name, "jpeg")

            status = detect.detect_obj_list(file_name)
            print(file_name_for_base64_data, ":", status)
            os.remove(file_name)

    except Exception as e:
        status = "Error! = " + str(e)


    return status

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
    