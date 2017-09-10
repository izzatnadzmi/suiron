# from suiron.core.SuironIO import SuironIO
# import cv2
# import os
# import time
# import json
# import numpy as np

# suironio = SuironIO(serial_location='/dev/ttyUSB0', baudrate=57600, port=5050)

# if __name__ == "__main__":
#     while True:
#     	# suironio.record_inputs()
#     	print('turn90')
#         suironio.servo_test(90)
#         print('turn0')
#         suironio.servo_test(0)
#         print('turn-90')
#         suironio.servo_test(-90)

# import socket
# import struct
# import pandas as pd

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = raw_input("Server hostname or ip? ")
# port = input("Server port? ")
# # sock.connect((host,port))
# sock.connect(('192.168.0.164',5051))

# while True:
#     data = raw_input("message: ")
#     # sock.send(data)
#     raw_data = {
# 	            'image': [2,4,2,5,6,3,2,3], 
# 	            'servo': [22,42,5,45,34,534,2,3],
# 	            'motor': [23423,324,32,324,324,2,4,2]
# 	        }
#     df = pd.DataFrame(raw_data, columns=['image', 'servo', 'motor'])
#     df = df.to_csv()
#     sock.sendall(struct.pack('>i', len(df))+df)
#     # sock.sendall(struct.pack('>i', len(data))+data)
#     print("response: ", sock.recv(1024))

import numpy as np
import cv2
import pandas as pd

from suiron.utils.functions import raw_to_cnn, cnn_to_raw, raw_motor_to_rgb
from suiron.utils.img_serializer import deserialize_image

# Visualize images
# With and without any predictions
def visualize_data(filename, width=72, height=48, depth=3, cnn_model=None):
    """
    When cnn_model is specified it'll show what the cnn_model predicts (red)
    as opposed to what inputs it actually received (green)
    """
    data = pd.DataFrame.from_csv(filename)     

    for i in range(30):
        cur_img = data['image'][i]
        cur_steer = int(data['servo'][i])
        cur_throttle = int(data['motor'][i])
        
        # [1:-1] is used to remove '[' and ']' from string 
        cur_img_array = deserialize_image(cur_img)
        # cur_img_array = cv2.resize(cur_img_array, (480, 320), interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(cur_img_array, cv2.COLOR_RGB2BGR)
        print(i)
        cv2.imwrite('test'+str(i)+'.jpg', image)

import sys
import json

# from suiron.core.SuironVZ import visualize_data
from suiron.utils.file_finder import get_latest_filename

# Load image settings
with open('settings.json') as d:
    SETTINGS = json.load(d)

# Visualize latest filename
filename = get_latest_filename() 

# If we specified which file
if len(sys.argv) > 1:
    filename = sys.argv[1]

visualize_data(filename, width=SETTINGS['width'], height=SETTINGS['height'], depth=SETTINGS['depth'])