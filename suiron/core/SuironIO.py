import time
import random
import socket
import struct
import numpy as np
import pandas as pd
import cv2, os, serial, csv
import matplotlib.pyplot as plt

from suiron.utils.functions import cnn_to_raw
from suiron.utils.img_serializer import serialize_image
from suiron.utils.file_finder import get_new_filename
from suiron.socket.controller import Server

class SuironIO:
    """
    Class which handles input output aspect of the suiron 
    - Reads inputs from webcam and normalizes them
    - Also reads serial input and write them to file
    """

    # Constructor
    def __init__(self, width=72, height=48, depth=3, serial_location='/dev/ttyACM0', baudrate=9600, host='', port=5050, mode='collect'):
        # Image settings
        self.width = int(width)
        self.height = int(height)
        self.depth = int(depth)

        # Video IO 
        self.cap =  cv2.VideoCapture(0) # Use first capture device

        # Serial IO
        self.ser = None
        if os.path.exists(serial_location):
            print('Found %s, starting to read from it...' % serial_location)
            self.ser = serial.Serial(serial_location, baudrate)        
        self.outfile = None        

        # Controller IO
        self.ctrl = None
        if self.mode == 'collect':
            print('Hosting server')
            self.ctrl, self.addr = Server(host, port).listen()
            print('Server hosted')

        # In-memory variable to record data
        # to prevent too much I/O
        self.frame_results = []
        self.servo_results = []
        self.motorspeed_results = [] 

        self.End = b'LOOOOLDFSODJOSSD'
    
    """ Functions below are used for inputs (recording data) """
    # Initialize settings before saving 
    def init_saving(self, folder='data', filename='output_', extension='.csv'):
        fileoutname = get_new_filename(folder=folder, filename=filename, extension=extension)

        # Filename to save serial data and image data
        # Output file
        outfile = open(fileoutname, 'w') # Truncate file first
        self.outfile = open(fileoutname, 'a')

    # Saves both inputs
    def record_inputs(self):
        # Frame is just a numpy array
        frame = self.get_frame()

        # Serial inputs is a dict with key 'servo', and 'motor'
        serial_inputs = self.get_serial()
        print(serial_inputs)
        # If its not in manual mode then proceed
        if serial_inputs:
            servo = serial_inputs['servo'] 
            motor = serial_inputs['motor'] 

            self.servo_test(servo, motor)

            # Append to memory
            # tolist so it actually appends the entire thing
            self.frame_results.append(serialize_image(frame))
            self.servo_results.append(servo)
            self.motorspeed_results.append(motor)

    # Get motor inputs, steering inputs etc
    def get_serial(self):
        # For debugging
        serial_raw = '-1,-1,-1\n'
        # if self.ser:
        #     # Polling for consistent data
        #     self.ser.write('d')
        #     serial_raw = self.ser.readline()
        if self.ctrl:
            serial_raw = self.ctrl.recv(102)
            # print(repr(serial_raw))
        serial_processed = self.normalize_serial(serial_raw)
        return serial_processed

    # Gets frame
    def get_frame(self):
        ret, frame = self.cap.read()

        # If we get a frame, save it
        if not ret:
            raise IOError('No image found!')

        frame = self.normalize_frame(frame)
        return frame

    # Gets frame for prediction
    def get_frame_prediction(self):
        ret, frame = self.cap.read()

        # if we get a frame
        if not ret:
            raise IOError('No image found!')

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        frame = frame.astype('uint8')

        minRGB = np.array([0, 0, 41])
        maxRGB = np.array([88, 88, 255])
        maskRGB = cv2.inRange(frame,minRGB,maxRGB)
        frame = cv2.bitwise_and(frame, frame, mask = maskRGB)

        return frame
    

    # Normalizes inputs so we don't have to worry about weird
    # characters e.g. \r\n
    def normalize_serial(self, line):
        # Assuming that it receives 
        # servo, motor
        
        # 'error' basically means that 
        # its in manual mode
        try:
            # line = line.decode("utf-8").split('\x00', 1)[0].split(', ')
            line = line.split(b'\x00', 1)[0].split(b', ')
            print(repr(line))
            line_dict = {'mode': line[0],'motor': int(line[1]), 'servo': int(line[2])}
            print(repr(line_dict))
            return line_dict
        except:
            return None

    # Normalizes frame so we don't have BGR as opposed to RGB
    def normalize_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height), interpolation=cv2.INTER_CUBIC)
        frame = frame.flatten()
        frame = frame.astype('uint8')
        return frame

    # Saves files
    def save_inputs(self):
        raw_data = {
            'image': self.frame_results, 
            'servo': self.servo_results,
            'motor': self.motorspeed_results
        }
        df = pd.DataFrame(raw_data, columns=['image', 'servo', 'motor'])
        df.to_csv(self.outfile)
        df = df.to_csv().encode()
        print(type(df))
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(('192.168.0.164',5051))
        # sizee = struct.pack('>i', len(df))
        # print(sizee)
        # sock.sendall(sizee+df)
        sock.sendall(df+self.End)
        sock.close() 

    """ Functions below are used for ouputs (controlling servo/motor) """    
    # Controls the servo given the numpy array outputted by
    # the neural network
    def servo_write(self, np_y):
        servo_out = cnn_to_raw(np_y)

        if (servo_out < 90):
            servo_out *= 0.85

        elif (servo_out > 90):
            servo_out *= 1.15

        serialBytes = 'mode, 30, ' + str(servo_out) + '\n'
        self.ser.write(serialBytes.encode()) 
        time.sleep(0.02)

    # Sets the motor at a fixed speed
    def motor_write_fixed(self):    
        self.ser.write('mode, 50, 0\n'.encode())
        time.sleep(0.02)

    # Stops motors
    def motor_stop(self):      
        self.ser.write('mode, 0, 0\n'.encode())
        time.sleep(0.02)

    # Staightens servos
    def servo_straighten(self):
        self.ser.write('mode, 0, 0\n'.encode())
        time.sleep(0.02)

    def servo_test(self, steer, motor):
        serialBytes = 'mode, ' + str(motor) + ', '+ str(steer) + '\n'
        self.ser.write(serialBytes.encode())
        time.sleep(0.02)
        
    def __del__(self):
        if self.outfile:
            self.outfile.close()
