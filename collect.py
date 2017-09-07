import cv2
import os
import time
import json
import numpy as np

from suiron.core.SuironIO import SuironIO

# Load image settings
with open('settings.json') as d:
    SETTINGS = json.load(d)

# Instantiatees our IO class
print('Initialising...')
suironio = SuironIO(width=SETTINGS['width'], height=SETTINGS['height'], depth=SETTINGS['depth'], baudrate=9600, host='')
print('Done Init...')
suironio.init_saving()  # open fileout

# Allows time for the camerae to warm up
print('Warming up...')
time.sleep(5)

input('Press any key to conitnue')
print('Recording data...')
while True:
    try:
        suironio.record_inputs()
    except KeyboardInterrupt:
        break

print('Saving file...')
suironio.save_inputs()
print('Done!')