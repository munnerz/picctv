import numpy as np
import cv2

cap = cv2.VideoCapture(0)
frameSize = (1280, 720);
writer = cv2.VideoWriter('capture.avi', cv2.cv.CV_FOURCC('X','V','I','D'), 30, frameSize, True)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1280);
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 720);

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Our operations on the frame come here
    writer.write(frame)        

    # Display the resulting frame
#    cv2.imshow('frame',frame)
    if cv2.waitKey(int(round(1.0/30.0))) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
