import multiprocessing
import socket
import threading

from utils import Utils
from modules import modules
import networking_processor

global PROCESSING_POOL

PROCESSING_POOL = multiprocessing.Pool(processes=4)


class Network(object):

    def __init__(self, ip="0.0.0.0", port=8000):
        multiprocessing.allow_connection_pickling()
        self._ip = ip
        self._port = port
        self._accepting_connections = self._processing_connections = True
        self._connections = []
        self._connectionsLock = threading.Lock()
        self._listeningThread = threading.Thread(target=self.listen)
        self._processingThread = threading.Thread(target=self.process)

        self._server_socket = socket.socket()
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen(0)
        
        Utils.msg("Network started on %s:%d" % (self._ip, self._port))

        self._listeningThread.start()
        self._processingThread.start()

    def accepted_connection(self, connectionDict):
        with self._connectionsLock:
            Utils.msg("Connection accepted")
            self._connections.append(connectionDict)

    def process(self):
        while self._processing_connections:
            with self._connectionsLock:
               PROCESSING_POOL.map_async(networking_processor.process_incoming, self._connections, callback=modules.process_data).get() #maybe keep the callback here?

    def listen(self):
        while self._accepting_connections:
            (connection, address) = self._server_socket.accept()
            Utils.dbg("Dispatching connection for initialisation")
            PROCESSING_POOL.apply_async(networking_processor.initialise_connection, args=[connection], callback=self.accepted_connection).get()
