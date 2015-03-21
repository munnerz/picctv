import cv2

def process_data(data):
    (module, data) = data
    cv2.namedWindow("%s: %s" % module, cv2.WINDOW_NORMAL)
    cv2.imshow("%s: %s" % module, data)
    cv2.waitKey(1)

def name():
    return "MotionDebug"

def shutdown_module():
    cv2.destroyAllWindows()