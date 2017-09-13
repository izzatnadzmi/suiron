from suiron.utils.img_serializer import deserialize_image, serialize_image
from suiron.core.SuironCV import *
from suiron.utils.file_finder import *
import numpy as np
import cv2
import pandas as pd

filename = get_latest_filename()

if len(sys.argv) > 1:
    filename = sys.argv[1]
    filename = "data/output_" + filename + ".csv"
"""
When cnn_model is specified it'll show what the cnn_model predicts (red)
as opposed to what inputs it actually received (green)
"""
fileoutname = get_new_filename(folder='edata', filename='output_', extension='.csv')
outfile = open(fileoutname, 'w')
outfile = open(fileoutname, 'a')

data = pd.DataFrame.from_csv(filename)
frame_results = []
servo_results = []
motorspeed_results = []
for i in data.index:
    cur_img = data['image'][i]
    servo = data['servo'][i]
    motor = data['motor'][i]
    cur_img_array = deserialize_image(cur_img)

    y_input = cur_img_array.copy()  # NN input
    #
    cur_img_array = bw_rgb_filter(cur_img_array, 48, 72)
    cur_img_array = cur_img_array.flatten()
    cur_img_array= cur_img_array.astype('uint8')


    frame_results.append(serialize_image(cur_img_array))
    servo_results.append(servo)
    motorspeed_results.append(motor)
    raw_data = {
        'image': frame_results,
        'servo': servo_results,
        'motor': motorspeed_results
    }
df = pd.DataFrame(raw_data, columns=['image', 'servo', 'motor'])
df.to_csv(outfile)
df = df.to_csv().encode()
outfile.close()



