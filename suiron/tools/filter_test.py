import sys
sys.path.append(r'C:\Users\rosliahm\PycharmProjects\suiron-baru')
import cv2
import time
from suiron.core.SuironCV import *
from suiron.utils.helperfunctions import *

width = 640
height = 480
real = True

cap = cv2.imread(r'C:\Users\rosliahm\PycharmProjects\suiron-baru\suiron\samples\clockwise\20170910135115.jpg', 1)
cap = cv2.resize(cap, (width, height), interpolation=cv2.INTER_CUBIC)


xgrad_thresh = (30, 110)
s_thresh = (40, 150)
ratio = 1
tl = [220 / ratio, 170 / ratio]
tr = [410 / ratio, 170 / ratio]
bl = [0 / ratio, 320 / ratio]
br = [640 / ratio, 310 / ratio]

tlm = [40 / ratio, 0 / ratio]
trm = [600 / ratio, 0 / ratio]
blm = [40 / ratio, 480 / ratio]
brm = [600 / ratio, 480 / ratio]

src = np.float32([tl, tr, br, bl])
dst = np.float32([tlm, trm, brm, blm])

while True:
    frame = cap
    if real:
        frame = filter_for_lanes(frame,ratio=1,xgrad_thresh_temp=xgrad_thresh,s_thresh_temp=s_thresh)
    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Sobel x
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)  # Take the derivative in x
        abs_sobelx = np.absolute(sobelx)  # Absolute x derivative to accentuate lines away from horizontal
        scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))

        # Threshold x gradient
        sxbinary = np.zeros_like(scaled_sobel)
        sxbinary[(scaled_sobel >= xgrad_thresh[0]) & (scaled_sobel <= xgrad_thresh[1])] = 1

        # Threshold colour channel

        # Convert to HLS colour space and separate the S channel
        # Note: img is the undistorted image
        hls = cv2.cvtColor(frame, cv2.COLOR_RGB2HLS)
        s_channel = hls[:, :, 2]

        # Cont'd: Threshold colour channel
        s_binary = np.zeros_like(s_channel)
        s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 1

        # Stack each channel to view their individual contributions in green and blue respectively
        # This returns a stack of the two binary images, whose components you can see as different colors
        color_binary = np.dstack((np.zeros_like(sxbinary), sxbinary, s_binary))

        # Combine the two binary thresholds
        combined_binary = np.zeros_like(sxbinary)
        combined_binary[(s_binary == 1) | (sxbinary == 1)] = 255
        M = cv2.getPerspectiveTransform(src, dst)
        Minv = cv2.getPerspectiveTransform(dst, src)
        warped = cv2.warpPerspective(combined_binary, M, (width, height), flags=cv2.INTER_LINEAR)
        frame = warped
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

