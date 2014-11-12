import socket
import time
import picamera

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('cctv', 8000))

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(2)
        # Start recording, sending the output to the connection for 60
        # seconds, then stop
        camera.start_recording(connection, format='h264')
        camera.wait_recording(60)
        camera.stop_recording()
finally:
    connection.close()
    client_socket.close()

#from __future__ import print_function#

#import io
#import time
#import cv2
#import cv2.cv as cv
#import numpy as np
#import picamera
#import picamera.array
#from PIL import Image#

#class VideoProcessor(object):
#	def write(self, s):
#		print("write")#
#

#def currentTime():
#	return int(time.time())#
#

##out = cv2.VideoWriter(capturePath, cv2.cv.CV_FOURCC('X','V','I','D'), fps, resolution, True)
#bOut = io.BytesIO()#

#with picamera.PiCamera() as camera:
#    with picamera.array.PiMotionArray(camera) as stream:
#        camera.resolution = (640, 480)
#        camera.framerate = 30
#        camera.start_recording(VideoProcessor(), format='h264', motion_output=stream)
#
#

#maxVideoLengthMillis = 10000
#cameraId = 0
#storagePath = "/recording-bin/%d/" % cameraId 
#fps = 15
#resolutionX = 960
#resolutionY = 540
#resolution = (resolutionX, resolutionY)
#capturePath = storagePath + 'capture-%d.avi' % currentTime()#
#

##cap = cv2.VideoCapture(0)
##cap.set(3,resolutionX)
##cap.set(4,resolutionY)
## Define the codec and create VideoWriter object
#print("Opening file " + capturePath)
#out = cv2.VideoWriter(capturePath, cv2.cv.CV_FOURCC('X','V','I','D'), fps, resolution, True)
#numFrames = 0#

##while(cap.isOpened()):
#with picamera.PiCamera() as camera:
#	camera.framerate = fps
#	camera.resolution = resolution
#	camera.start_recording(VideoProcessor(), [format='h264'])#

##	currentTimeMillis = 1000 * (numFrames * (1.0 / fps));
##	if(currentTimeMillis >= maxVideoLengthMillis):
##		#reset video file
##		out.release()
##		print "Finished writing " + capturePath
##		capturePath = storagePath + 'capture-%d.avi' % currentTime()
##		print "Opening file " + capturePath
##		out = cv2.VideoWriter(capturePath, cv2.cv.CV_FOURCC('X','V','I','D'), fps, resolution, True)
##		numFrames = 0
##	
##	print "frame capture %d,  %.3fs in" % ( numFrames, numFrames * (1.0 / fps) )
##	numFrames += 1
##	ret, frame = cap.read()
##	if ret==True:
##		frame = cv2.flip(frame,0)
##		# write the flipped frame
##		out.write(frame)#

#	#cv2.imshow('frame',frame)
##	if cv2.waitKey(int(1000 * (1.0 / fps))) & 0xFF == ord('q'):
##		break
#print ("ended")#

## Release everything if job is finished
##cap.release()
#out.release()
##cv2.destroyAllWindows()