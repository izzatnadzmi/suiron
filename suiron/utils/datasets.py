"""
datasets.py provides functions to help condense data 'collect.py' into
numpy arrays which can be fed into the CNN/NN
"""

import numpy as np
import pandas as pd

from suiron.utils.img_serializer import deserialize_image
from suiron.utils.functions import raw_to_cnn, remapvalue

# Gets servo dataset
def get_servo_dataset(filename, start_index=0, end_index=None):
    data = pd.DataFrame.from_csv(filename)

    # Outputs
    x = []

    # Servo ranges from 40-150
    servo = []

    for i in data.index[start_index:end_index]:
        # Don't want noisy data
        xj = data['servo'][i]

        if xj < 50 or xj > 150 :
            continue

        # Append
        x.append(deserialize_image(data['image'][i]))
        servo.append(raw_to_cnn(remapvalue(xj)))

    return x, servo

# Gets motor output dataset
# Assumption is that motor and servo has
# some sort of relationship
# Ignore mapping for motor and servo at same time
def get_motor_dataset(filename, start_index=0, end_index=None):
    data = pd.DataFrame.from_csv(filename)

    # Servo
    servo = []

    # Motor ranges from 40-150
    motor = []

    for i in data.index[start_index:end_index]:
        # Don't want noisy data
        if data['motor'][i] < 50 or data['motor'][i] > 150:
            continue

        if data['servo'][i] < 50 or data['servo'][i] > 150:
            continue

        # Append
        servo.append(raw_to_cnn(data['servo'][i]))
        motor.append(raw_to_cnn(data['motor'][i], min_arduino=50, max_arduino=150))

    return servo, motor