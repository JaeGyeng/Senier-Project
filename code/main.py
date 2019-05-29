from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import classifier as cf
import transparentOverlay as tpo
 
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "tangerine"
# ball in the HSV color space, then initialize the
# list of tracked points
mandarLower = (0,172,96)  
mandarUpper = (20, 255, 255)
pts = deque(maxlen=args["buffer"])
 
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=1).start()
	#vs = VideoStream(src='http://172.30.1.55:8080/video').start() #ipcam
# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
#time.sleep(2.0)
			
count = 0
checkGrade = ["Null", "Null", "Null", "Null"]
mandarSize = 0

g_state = cv2.imread('sysImg\\good.png', -1)
b_state = cv2.imread('sysImg\\bad.png', -1)
guide1 = cv2.imread('sysImg\\guide1.png',-1)
guide2 = cv2.imread('sysImg\\guide2.png',-1)
guide3 = cv2.imread('sysImg\\guide3.png',-1)
guide4 = cv2.imread('sysImg\\guide4.png',-1)
guide5 = cv2.imread('sysImg\\guide5.png',-1)

def captureMandar():
    time.sleep(0.5)
    global count, guide
    count += 1
    print(count)   
    _,thresh = cv2.threshold(mask,1,255,cv2.THRESH_BINARY)
    contours = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    (x,y,w,h) = cv2.boundingRect(contours[0]) 
    img_trim = frame[y : (y+h)*2, x : (x+w)*2]
    cv2.imwrite("capture\\%d.jpg" %count, img_trim)
    checkGrade[count-1] = cf.predictMandar('%d' %count)


startTime  = time.time()

# keep looping
while True:  

	# grab the current frame
	frame = vs.read()

	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame
 
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
 
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=700, height = 500)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
 
	# construct a mask for the color "mandarine", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, mandarLower, mandarUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	center = None
 
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

			if(count != 4):
			    mandarSize = int(radius)
			    cv2.circle(frame, (350, 250), 150, (0,0,255), 3)
			    cv2.circle(frame, (350, 250), 90, (0,0,255), 3)
			    cv2.circle(frame, (350, 250), 10, (0,255,0), 3)
			    cv2.putText(frame, "Guide Line", (500,200), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 51))
			    guide = cv2.resize(guide1, (100,175),interpolation=cv2.INTER_CUBIC)
			    tpo.tpOverlay(frame[300:300+175, 10:10+110], guide)

			    if(count == 0 and int(M["m10"] / M["m00"])>=350 and int(M["m01"] / M["m00"])>=250):
                                             
			         timeElapsed =  time.time() - startTime
			         secElapsed = int(timeElapsed)
			         print("count time: ", secElapsed)

			         if(secElapsed >= 10):
			             captureMandar()
			             guide = cv2.resize(guide2, (110,175),interpolation=cv2.INTER_CUBIC)
			             tpo.tpOverlay(frame[300:300+175, 10:10+110], guide)			         


			    elif(count == 1):
			         guide = cv2.resize(guide3, (110,175),interpolation=cv2.INTER_CUBIC)
			         tpo.tpOverlay(frame[300:300+175, 10:10+110], guide)
			         captureMandar()

			    elif(count == 2):
			         guide = cv2.resize(guide4, (110,175),interpolation=cv2.INTER_CUBIC)
			         tpo.tpOverlay(frame[300:300+175, 10:10+110], guide)
			         captureMandar()


			    elif(count == 3):
			         captureMandar()

			    rsize = "radius: " + str(int(radius))
			    cv2.putText(frame, "Measuring", (int(x)+100, int(y)+100), cv2.FONT_HERSHEY_TRIPLEX, 1, (204, 255, 51))			
			    cv2.putText(frame, rsize, (int(x)+100, int(y)+200), cv2.FONT_HERSHEY_TRIPLEX, 1, (204, 255, 51))
	

		key = cv2.waitKey(1) & 0xFF
		if key == ord("r"):
			count = 0
			checkGrade = ["Null", "Null", "Null", "Null"]
			mandarSize = 0
			startTime  = time.time()
			timeElapsed =  time.time() - startTime
			secElapsed = int(timeElapsed)
		
		if (count == 4):
		
			if (checkGrade[0] == "GOOD" and checkGrade[1] == "GOOD" and checkGrade[2] == "GOOD" and checkGrade[3] == "GOOD"):
			    cv2.putText(frame, "GOOD", (int(x)+100, int(y)+100), cv2.FONT_HERSHEY_TRIPLEX, 1, (204, 255, 51))
			    g_state = cv2.resize(g_state, (100,100),interpolation=cv2.INTER_CUBIC)
			    tpo.tpOverlay(frame[int(x):int(x)+100, int(y):int(y)+100], g_state)

			else:	
			    cv2.putText(frame, "BAD", (int(x)+100, int(y)+100), cv2.FONT_HERSHEY_TRIPLEX, 1, (51, 0, 255))
			    B_state = cv2.resize(b_state, (100,100),interpolation=cv2.INTER_CUBIC)
			    tpo.tpOverlay(frame[int(x):int(x)+100, int(y):int(y)+100], b_state)

			if (mandarSize < 90):
			    cv2.putText(frame, "Size: 2S", (int(x)+100, int(y)+150), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0))
			elif (90 <= mandarSize < 110 ):
			    cv2.putText(frame, "Size: S", (int(x)+100, int(y)+150), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0))
			elif (110 <= mandarSize < 130):
			    cv2.putText(frame, "Size: M", (int(x)+100, int(y)+150), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0))
			elif (mandarSize >= 130):
			    cv2.putText(frame, "Size: L", (int(x)+100, int(y)+150), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0))

			guide = cv2.resize(guide5, (100,175),interpolation=cv2.INTER_CUBIC)
			tpo.tpOverlay(frame[300:300+175, 10:10+110], guide)
			    

			
	# update the points queue
	pts.appendleft(center)

	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		#thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		#cv2.line(frame, pts[i - 1], pts[i], (0, 199, 255), thickness)
 
	# show the frame to our screen
	cv2.imshow("Mandarine", frame)

	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
 
# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()
 
# otherwise, release the camera
else:
	vs.release()
 
# close all windows
cv2.destroyAllWindows()