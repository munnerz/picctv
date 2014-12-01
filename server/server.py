from web.WebServer import WebServer
from capture.capture import Capture
from library import library
import signal
from utils import Utils, Settings


def main():
    global library, webServer, capture

    library = library.lib

    webServer = WebServer(library)
    capture = Capture(library)
    capture.daemon = True

    capture.start()
    webServer.start()

def getCapture():
	global capture
	return capture

if __name__ == "__main__":
	#set signals behaviour
	signal.signal(signal.SIGINT, Utils.signal_handler)
	main()