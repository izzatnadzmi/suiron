import cv2
import time
import os

cam = cv2.VideoCapture(0)

#cv2.namedWindow("test")
width =640
height =480
img_counter = 0

while True:
    ret, frame = cam.read()
    cv2.resize(frame, (width, height), interpolation=cv2.INTER_CUBIC)
    #cv2.imshow("test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        img_counter = time.strftime("%Y%m%d%d%H%M%S")
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        break

cam.release()

cv2.destroyAllWindows()