# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
import pigpio

pi = pigpio.pi()

LEFT = 23
RIGHT = 24 
FRONT = 16
BACK = 25
FAST = 520
SLOW = 260

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (400, 300)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(400, 300))
 
hsv = [55, 229, 158]
thresh = [20, 100, 255]

# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
  
	minHSV = np.array([hsv[0] - thresh[0], 25, 25])
	maxHSV = np.array([hsv[0] + thresh[0], 255, 255])
 
	imageHSV = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

	maskHSV = cv2.inRange(imageHSV, minHSV, maxHSV)
	
	kernel = np.ones((5,5),np.uint8)
	erosion = cv2.erode(maskHSV, kernel, iterations = 1)

	_, contours, _ = cv2.findContours(erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#	resultHSV = cv2.bitwise_and(imageHSV, imageHSV, mask = erosion)

	# find largest contour on screen
	maxArea = 100
	maxContour = None
	for wrapper in contours:
		area = cv2.contourArea(wrapper)
		if area > maxArea:
			maxArea = area
			maxContour = wrapper 
	
	if maxArea > 100:
		(x,y),radius = cv2.minEnclosingCircle(maxContour)
		center = (int(x),int(y))
		radius = int(radius)
		cv2.circle(image,center,radius,(0,255,0),2)	
		cv2.putText(image, str(x) + ", " + str(y), center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

		pi.write(LEFT, 0)
		pi.write(RIGHT, 0)
		pi.write(FRONT, 0)
		pi.write(BACK, 0)
	
		if center[0] <= 190:
			pi.write(LEFT, 1)
		elif center[0] >= 210:
			pi.write(RIGHT, 1)

		if center[1] <= 80:
			pi.write(BACK, 1)
		elif center[1] >= 175:
			pi.write(FRONT, 1)
	else:
		pi.write(LEFT, 0)
		pi.write(RIGHT, 0)
		pi.write(FRONT, 0)
		pi.write(BACK, 0)

	# show the frame
	cv2.drawContours(image, maxContour, -1, (0,255,0), 3)
	cv2.imshow("Frame", image)

	key = cv2.waitKey(1) & 0xFF

 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

