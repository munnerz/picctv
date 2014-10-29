import numpy as np
import time
import cv2
import cv2.cv as cv


def currentTime():
	return int(time.time())

maxVideoLengthMillis = 10000
cameraId = 0
storagePath = "/recording-bin/%d/" % cameraId 
fps = 20
resolutionX = 640
resolutionY = 360
resolution = (resolutionX, resolutionY)
capturePath = storagePath + 'capture-%d.avi' % currentTime()


cap = cv2.VideoCapture(0)
cap.set(3,resolutionX)
cap.set(4,resolutionY)
# Define the codec and create VideoWriter object
print "Opening file " + capturePath
out = cv2.VideoWriter(capturePath, cv2.cv.CV_FOURCC('X','V','I','D'), fps, resolution, True)
numFrames = 0

while(cap.isOpened()):
	currentTimeMillis = 1000 * (numFrames * (1.0 / fps));
	if(currentTimeMillis >= maxVideoLengthMillis):
		#reset video file
		out.release()
		print "Finished writing " + capturePath
		capturePath = storagePath + 'capture-%d.avi' % currentTime()
		print "Opening file " + capturePath
		out = cv2.VideoWriter(capturePath, cv2.cv.CV_FOURCC('X','V','I','D'), fps, resolution, True)
		numFrames = 0
	
	print "frame capture %d,  %.3fs in" % ( numFrames, numFrames * (1.0 / fps) )
	numFrames += 1
	ret, frame = cap.read()
	if ret==True:
		frame = cv2.flip(frame,0)
		# write the flipped frame
		out.write(frame)

	#cv2.imshow('frame',frame)
	if cv2.waitKey(int(1000 * (1.0 / fps))) & 0xFF == ord('q'):
		break
print "ended"

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()