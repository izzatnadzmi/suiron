"""
datasets.py provides functions to help condense data 'collect.py' into
numpy arrays which can be fed into the CNN/NN
"""

import numpy as np
import pandas as pd
import cv2

from suiron.utils.img_serializer import deserialize_image
from suiron.utils.functions import raw_to_cnn

# Gets servo dataset
def get_servo_dataset(filename, start_index=0, end_index=None):
    data = pd.DataFrame.from_csv(filename)

    # Outputs
    x = []

    # Servo ranges from 40-150
    servo = []

    for i in data.index[start_index:end_index]:
        # Don't want noisy data
        if data['servo'][i] < -100 or data['servo'][i] > 100 :
            continue

        # Append
        image = deserialize_image(data['image'][i])

        minRGB = np.array([0, 0, 41])
        maxRGB = np.array([88, 88, 255])
        maskRGB = cv2.inRange(image,minRGB,maxRGB)
        image = cv2.bitwise_and(image, image, mask = maskRGB)

        x.append(image)
        servo.append(raw_to_cnn(data['servo'][i]))

    return x, servo

# Gets motor output dataset
# Assumption is that motor and servo has
# some sort of relationship
def get_motor_dataset(filename, start_index=0, end_index=None):
    data = pd.DataFrame.from_csv(filename)

    # Servo
    servo = []

    # Motor ranges from 40-150
    motor = []

    for i in data.index[start_index:end_index]:
        # Don't want noisy data
        if data['motor'][i] < -100 or data['motor'][i] > 100:
            continue

        if data['servo'][i] < 40 or data['servo'][i] > 150:
            continue

        # Append
        servo.append(raw_to_cnn(data['servo'][i]))
        motor.append(raw_to_cnn(data['motor'][i], min_arduino=-100, max_arduino=100))

    return servo, motor