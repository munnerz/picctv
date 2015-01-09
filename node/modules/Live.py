import threading
import socket
import logging

from modules.ModuleBase import ModuleBase

LOGGER = logging.getLogger("node.Live")

class Live(ModuleBase):

    def __init__(self):
        ModuleBase.__init__(self) #to ensure the main frame loop begins
        self._sock_addr = ('0.0.0.0', 8000)
        self._keepListening = True
        self._listeningThread = threading.Thread(target=self._listen)

        self._outputs = []
        self._outputLock = threading.Lock()

        #now start listening...
        self._listeningThread.start()


    def _listen(self):
        self._server_socket = socket.socket()
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.settimeout(1)
        self._server_socket.bind(self._sock_addr)
        self._server_socket.listen(0)

        while self._keepListening:
            try:
                fos = self._server_socket.accept()[0].makefile('wb')
                with self._outputLock:
                    self._outputs.append(fos)
            except socket.timeout:
                pass
        return

    def required_quality(self):
        return "high"

    def process_frame(self, data):
        with self._outputLock:
            for output in self._outputs[:]:
                try:
                    output.write(data[0])
                except Exception as e:
                    LOGGER.exception("Exception in Live module during processFrame: %s" % e)
                    self._outputs.remove(output)
                    pass
        return None

    def shutdown(self):
        LOGGER.debug("Shutting down...")

        self._keepListening = False
        with self._outputLock:
            map(lambda o: o.close(), self._outputs)
            del self._outputs[:]
        self._server_socket.close()
        self._listeningThread.join(timeout=1)

        LOGGER.debug("Shut down.")
