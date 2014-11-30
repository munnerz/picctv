from web.WebServer import WebServer
from capture.capture import Capture
from library.library import Library

def getLibrary():
    return Library.getDefaultLibrary()

def main():
    global library, webServer, capture

    library = getLibrary()

    webServer = WebServer(library)
    capture = Capture(library)

    capture.start()
    webServer.start()

if __name__ == "__main__":
    main()