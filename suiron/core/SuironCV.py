"""
SuironCV contains functions that does some preprocessing on the images
before it is fed into the feed forward network
"""
import math
import cv2
import numpy as np
import sys
sys.path.append(r'/home/ubuntuml/PycharmProjects/suiron')

from suiron.utils.helperfunctions import *

# Median blur
def get_median_blur(gray_frame):
    return cv2.medianBlur(gray_frame, 5)

# Canny edge detection
def get_canny(gray_frame):
    return cv2.Canny(gray_frame, 50, 200, apertureSize=3)

# Hough lines
def get_lane_lines(inframe):
    frame = inframe.copy()
    ret_frame = np.zeros(frame.shape, np.uint8)

    # We converted it into RGB when we normalized it
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    gray = get_median_blur(gray)
    canny = get_canny(gray)

    # Hough lines
    # threshold = number of 'votes' before hough algorithm considers it a line
    lines = cv2.HoughLinesP(canny, 1, np.pi/180, threshold=25, minLineLength=40, maxLineGap=100)

    try:
        r = lines.shape[0]
    except AttributeError:
        r = 0

    for i in range(0):
        for x1, y1, x2, y2 in lines[i]:
            # Degrees as its easier for me to conceptualize
            angle = math.atan2(y1-y2, x1-x2)*180/np.pi

            # If it looks like a left or right lane
            # Draw it onto the new image
            if 100 < angle < 170 or -170 < angle < -100:
                cv2.line(ret_frame, (x1, y1), (x2, y2), (255, 255, 255), 10)

    return ret_frame

def wrap_for_lanes(frame, height=480, width=640, ratio=10):
    tl = [220/ratio, 170/ratio]
    tr = [410/ratio, 170/ratio]
    bl = [0/ratio, 320/ratio]
    br = [640/ratio, 310/ratio]

    tlm = [40/ratio,0/ratio]
    trm = [600/ratio,0/ratio]
    blm = [600/ratio,480/ratio]
    brm = [40/ratio,480/ratio]

    src = np.float32([tl,tr,br,bl])
    dst = np.float32([tlm,trm,brm,blm])

    M = cv2.getPerspectiveTransform(src, dst)
    frame = cv2.warpPerspective(frame, M, (width/ratio, height/ratio), flags=cv2.INTER_LINEAR)


    return frame

def filter_for_lanes(frame,height=480, width=640, xgrad_thresh_temp = (10,100), s_thresh_temp = (20,100)):
    oriheight = 480
    oriwidth = 640
    ratio = int(oriwidth/width)

    tl = [220/ratio, 170/ratio]
    tr = [410/ratio, 170/ratio]
    bl = [0/ratio, 320/ratio]
    br = [640/ratio, 310/ratio]

    tlm = [50/ratio,0/ratio]
    trm = [590/ratio,0/ratio]
    blm = [50/ratio,480/ratio]
    brm = [590/ratio,480/ratio]


    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_CUBIC)
    mframe = frame.astype('uint8')

    src = np.float32([tl,tr,br,bl])
    dst = np.float32([tlm,trm,brm,blm])

    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)

    blank_canvas = np.zeros((height, width))
    colour_canvas = cv2.cvtColor(blank_canvas.astype(np.uint8), cv2.COLOR_GRAY2RGB)
    have_fit = False
    while have_fit == False:
        combined_binary = apply_threshold_v2(mframe, xgrad_thresh=xgrad_thresh_temp, s_thresh=s_thresh_temp)
        warped = cv2.warpPerspective(combined_binary, M, (width, height), flags=cv2.INTER_LINEAR)

        leftx, lefty, rightx, righty = histogram_pixels(warped, horizontal_offset=0)
        if len(leftx) > 1 and len(rightx) > 1:
            have_fit = True
        xgrad_thresh_temp = (xgrad_thresh_temp[0] - 2, xgrad_thresh_temp[1] + 2)
        s_thresh_temp = (s_thresh_temp[0] - 2, s_thresh_temp[1] + 2)

    left_fit, left_coeffs = fit_second_order_poly(lefty, leftx, return_coeffs=True)
    right_fit, right_coeffs = fit_second_order_poly(righty, rightx, return_coeffs=True)

    y_eval = np.max(lefty)
    left_curverad = ((1 + (2 * left_coeffs[0] * y_eval + left_coeffs[1]) ** 2) ** 1.5) \
                    / np.absolute(2 * left_coeffs[0])
    right_curverad = ((1 + (2 * right_coeffs[0] * y_eval + right_coeffs[1]) ** 2) ** 1.5) \
                     / np.absolute(2 * right_coeffs[0])
    curvature = (left_curverad + right_curverad) / 2
    centre = center(319, left_coeffs, right_coeffs)

    polyfit_left = draw_poly(blank_canvas, lane_poly, left_coeffs, 30)
    polyfit_drawn = draw_poly(polyfit_left, lane_poly, right_coeffs, 30)

    trace = colour_canvas
    trace[polyfit_drawn > 1] = [0, 0, 255]
    #print (left_coeffs)
    area = highlight_lane_line_area(polyfit_drawn, left_coeffs, right_coeffs, end_y =height)
    trace[area == 1] = [0, 255, 0]

    lane_lines = cv2.warpPerspective(trace, Minv, (width, height), flags=cv2.INTER_LINEAR)
    frame = cv2.add(lane_lines, mframe)
    #frame = cv2.resize(frame, (width/ratio, height/ratio), interpolation=cv2.INTER_CUBIC)

    return frame

def bw_rgb_filter (frame,height=480, width=640, xgrad_thresh = (60,100), s_thresh = (80,250)):
    offset = 0
    offseth = 0
    pts = np.array([[(offset), (offset)], [(width), (offset)], [(width), (height/3)],
              [(offset), (height/3)]])
    #frame = cv2.resize(frame, (width/ratio, height/ratio), interpolation=cv2.INTER_CUBIC)
    #mframe = frame.astype('uint8')
    mframe=frame
    minRGB = np.array([0, 10, 0])
    maxRGB = np.array([255, 200, 255])
    maskRGB = cv2.inRange(mframe, minRGB, maxRGB)
    frame = cv2.bitwise_and(mframe, mframe, mask=maskRGB)

    gray = cv2.cvtColor(mframe, cv2.COLOR_RGB2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)  # Take the derivative in x
    abs_sobelx = np.absolute(sobelx)  # Absolute x derivative to accentuate lines away from horizontal
    scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))
    sxbinary = np.zeros_like(scaled_sobel)
    sxbinary[(scaled_sobel >= xgrad_thresh[0]) & (scaled_sobel <= xgrad_thresh[1])] = 255

    hls = cv2.cvtColor(frame, cv2.COLOR_RGB2HLS)
    s_channel = hls[:, :, 2]
    s_binary = np.zeros_like(s_channel)

    s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 255
    s_binary = cv2.fillPoly(s_binary, [pts], (0, 0, 0), 8)
    s_binary[(s_binary >= 150)] = 255
    color_binary = np.dstack((np.zeros_like(sxbinary), np.zeros_like(sxbinary), s_binary))
    final = cv2.cvtColor(s_binary, cv2.COLOR_GRAY2RGB)


    return color_binary

def colour_lane_filter(frame,):
    minRGB = np.array([0, 0, 41])
    maxRGB = np.array([88, 88, 255])
    maskRGB = cv2.inRange(frame, minRGB, maxRGB)
    frame = cv2.bitwise_and(frame, frame, mask=maskRGB)
    return frame

def main_filter(frame, height=480, width = 640,filter = "latest"):

    if (filter == "latest"):
        final = bw_rgb_filter(frame,height,width)
    else:
        final = colour_lane_filter(frame)
    return final
