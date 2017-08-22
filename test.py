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

import socket
import struct
import pandas as pd

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = raw_input("Server hostname or ip? ")
port = input("Server port? ")
# sock.connect((host,port))
sock.connect(('192.168.0.164',5051))

while True:
    data = raw_input("message: ")
    # sock.send(data)
    raw_data = {
	            'image': [2,4,2,5,6,3,2,3], 
	            'servo': [22,42,5,45,34,534,2,3],
	            'motor': [23423,324,32,324,324,2,4,2]
	        }
    df = pd.DataFrame(raw_data, columns=['image', 'servo', 'motor'])
    df = df.to_csv()
    sock.sendall(struct.pack('>i', len(df))+df)
    # sock.sendall(struct.pack('>i', len(data))+data)
    print "response: ", sock.recv(1024)