import threading
import socket
import logging

import settings

LOGGER = settings.logger("node.modules.Live")


_keepListening = True

_outputs = []
_outputLock = threading.Lock()
arguments = None
_listeningThread = None

def _listen():
    global _server_socket, _outputs, arguments
    _server_socket = socket.socket()
    _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _server_socket.settimeout(1)
    _server_socket.bind(arguments['listen_address'])
    _server_socket.listen(0)

    while _keepListening:
        try:
            fos = _server_socket.accept()[0].makefile('wb')
            with _outputLock:
                _outputs.append(fos)
        except socket.timeout:
            pass
    return

def process_data(data):
    with _outputLock:
        for output in _outputs[:]:
            try:
                output.write(data[1][0])
            except IOError as e:
                LOGGER.exception("IOException in Live module during processFrame: %s" % e)
                _outputs.remove(output)
                pass
    return None

def name():
    return "Live"
    
def shutdown():
    global _keepListening, _outputs
    LOGGER.debug("Shutting down...")

    _keepListening = False
    with _outputLock:
        map(lambda o: o.close(), _outputs)
        del _outputs[:]
    _server_socket.close()
    _listeningThread.join(timeout=1)

    LOGGER.debug("Shut down.")

def module_started():
    global _listeningThread
    _listeningThread = threading.Thread(target=_listen)
    _listeningThread.start()
