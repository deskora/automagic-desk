#from multiprocessing import Process, Queue
import time
import cv2
import RPi.GPIO as GPIO  ### GPIO Library


GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(26, GPIO.OUT) ## Setup GPIO Pin 23 to OUT - Up
GPIO.setup(19, GPIO.OUT) ## Setup GPIO Pin 24 to OUT - Down


webcam = cv2.VideoCapture(0)				# Get ready to start getting images from the webcam
webcam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)		# I have found this to be about the highest-
webcam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)	# 	resolution you'll want to attempt on the pi
cv2.cv.NamedWindow("video", cv2.cv.CV_WINDOW_AUTOSIZE)

frontalface = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")		# frontal face pattern detection
profileface = cv2.CascadeClassifier("haarcascade_profileface.xml")		# side face pattern detection

face = [0,0,0,0]	# This will hold the array that OpenCV returns when it finds a face: (makes a rectangle)
Cface = [0,0]		# Center of the face: a point calculated from the above variable
lastface = 0		# int 1-3 used to speed up detection. The script is looking for a right profile face,-
			# 	a left profile face, or a frontal face; rather than searching for all three every time,-
			# 	it uses this variable to remember which is last saw: and looks for that again. If it-
			# 	doesn't find it, it's set back to zero and on the next loop it will search for all three.-
			# 	This basically tripples the detect time so long as the face hasn't moved much.


def DeskDown(distance):			# Same logic as above
    print "Moving Desk Down"
    GPIO.output(26,GPIO.HIGH)
    time.sleep (distance)
    print "Stopping"
    GPIO.output(26,GPIO.LOW)
    return;


def DeskUp(distance):			# Same logic as above
    print "Moving Desk Up"
    GPIO.output(19,GPIO.HIGH)
    time.sleep (distance)
    print "Stopping"
    GPIO.output(19,GPIO.LOW)
    
    return;



#============================================================================================================


while True:

	faceFound = False	# This variable is set to true if, on THIS loop a face has already been found
				# We search for a face three diffrent ways, and if we have found one already-
				# there is no reason to keep looking.
	
	if not faceFound:
		if lastface == 0 or lastface == 1:
			aframe = webcam.read()[1]	# there seems to be an issue in OpenCV or V4L or my webcam-
			aframe = webcam.read()[1]	# 	driver, I'm not sure which, but if you wait too long,
			aframe = webcam.read()[1]	#	the webcam consistantly gets exactly five frames behind-
			aframe = webcam.read()[1]	#	realtime. So we just grab a frame five times to ensure-
			aframe = webcam.read()[1]	#	we have the most up-to-date image.
			fface = frontalface.detectMultiScale(aframe,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(60,60))
			if fface != ():			# if we found a frontal face...
				lastface = 1		# set lastface 1 (so next loop we will only look for a frontface)
				for f in fface:		# f in fface is an array with a rectangle representing a face
					faceFound = True
					face = f

	if not faceFound:				# if we didnt find a face yet...
		if lastface == 0 or lastface == 2:	# only attempt it if we didn't find a face last loop or if-
			aframe = webcam.read()[1]	# 	THIS method was the one who found it last loop
			aframe = webcam.read()[1]
			aframe = webcam.read()[1]	# again we grab some frames, things may have gotten stale-
			aframe = webcam.read()[1]	# since the frontalface search above
			aframe = webcam.read()[1]
			pfacer = profileface.detectMultiScale(aframe,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(80,80))
			if pfacer != ():		# if we found a profile face...
				lastface = 2
				for f in pfacer:
					faceFound = True
					face = f

	if not faceFound:				# a final attempt
		if lastface == 0 or lastface == 3:	# this is another profile face search, because OpenCV can only-
			aframe = webcam.read()[1]	#	detect right profile faces, if the cam is looking at-
			aframe = webcam.read()[1]	#	someone from the left, it won't see them. So we just...
			aframe = webcam.read()[1]
			aframe = webcam.read()[1]
			aframe = webcam.read()[1]
			cv2.flip(aframe,1,aframe)	#	flip the image
			pfacel = profileface.detectMultiScale(aframe,1.3,4,(cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH),(80,80))
			if pfacel != ():
				lastface = 3
				for f in pfacel:
					faceFound = True
					face = f

	if not faceFound:		# if no face was found...-
		lastface = 0		# 	the next loop needs to know
		face = [0,0,0,0]	# so that it doesn't think the face is still where it was last loop


	x,y,w,h = face
	Cface = [(w/2+x),(h/2+y)]	# we are given an x,y corner point and a width and height, we need the center
	#print str(Cface[0]) + "," + str(Cface[1])

	if Cface[0] != 0:		# if the Center of the face is not zero (meaning no face was found)


		if Cface[1] > 140:	# and moves diffrent amounts depending on what axis we are talking about.
			DeskDown(1)
		if Cface[1] > 150:
			DeskDown(2)
		if Cface[1] > 160:
			DeskDown(3)

		if Cface[1] < 100:
			DeskUp(1)
		if Cface[1] < 90:
			DeskUp(2)
		if Cface[1] < 80:
			DeskUp(3)

#	cv2.cv.Rectangle(cv2.cv.fromarray(aframe), (x,y), (x+w,y+h), cv2.cv.RGB(255, 0, 0), 3, 8, 0)
#	cv2.imshow("video", aframe)
#	cv2.waitKey(1)
