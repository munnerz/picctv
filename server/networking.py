from multiprocessing.pool import ThreadPool
import multiprocessing
import socket
import time
import threading


from utils import Utils
import modules
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
        self._connections_lock = threading.Lock()
        self._listening_thread = threading.Thread(target=self.listen)
        self._processing_thread = threading.Thread(target=self.process)
        self._processing_workers = ThreadPool(processes=2)

        self._server_socket = socket.socket()
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen(0)
        
        Utils.msg("Network started on %s:%d" % (self._ip, self._port))

        self._listening_thread.start()
        self._processing_thread.start()

    def connection_failed(self, connectionInfo):
        try:
            connectionInfo['connection'].close()
        except IOError as e:
            Utils.err("%s whilst reading module data for module '%s' from camera '%s'" % 
                (type(e).__name__, connectionInfo['module_name'], connectionInfo['camera_name']))
        with self._connections_lock:
            self._connections.remove(connectionInfo)
        Utils.msg("Closed connection for module '%s' on camera '%s'" % (connectionInfo['module_name'], connectionInfo['camera_name']))

    def accepted_connection(self, connectionDict):
        with self._connections_lock:
            Utils.msg("Connection accepted")
            self._connections.append(connectionDict)

    def process(self):
        while self._processing_connections:
            with self._connections_lock:
                self._processing_workers.map_async(networking_processor.process_incoming, self._connections, callback=modules.process_data).get()
            time.sleep(0.1)

    def listen(self):
        while self._accepting_connections:
            (connection, address) = self._server_socket.accept()
            Utils.dbg("Dispatching connection for initialisation")
            self.accepted_connection(networking_processor.initialise_connection(connection))
            self._processing_workers.apply_async(networking_processor.initialise_connection, args=connection, callback=self.accepted_connection)
