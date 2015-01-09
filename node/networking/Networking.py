from multiprocessing import Process, Queue
from Queue import Empty
import cPickle as pickle
import socket
import struct
import logging
import sys

LOGGER = logging.getLogger(name="node.Networking")

def _chunks(lst, n):
    "Yield successive n-sized chunks from lst"
    for i in xrange(0, len(lst), n):
        yield lst[i:i+n]

class Networking(object):

    def __init__(self, camera_id, ip="cctv", port=8000):
        LOGGER.info("Starting networking")
        self._camera_id = camera_id
        self._ip = ip
        self._port = port
        self._connections = {}
        self._send_queue = Queue()
        self._process = Process(target=self.run, args=(self._send_queue,))
        self._process.start()

    def send_data(self, data):
        LOGGER.debug("Queue size (SD): %d" % self._send_queue.qsize())
        self._send_queue.put(data)

    def _create_connection(self, module_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self._ip, self._port))

            if self._pickle_and_send(self._camera_id, sock) and self._pickle_and_send(module_name, sock):
                self._connections[module_name] = sock
                LOGGER.debug("Connection for module '%s' set up..." % module_name)
                return sock

        except IOError as e:
            LOGGER.exception("Error connecting to server for module %s (Exception: %s)" % (module_name, e))

        return None

    def _pickle_and_send(self, d, conn):
        ''' serialises d and sends it over connection conn with a length header '''
        serialised = pickle.dumps(d, -1)
        toSend = struct.pack(str(len(serialised)) + 's', serialised)

        sent_bytes = 0

        try:
            conn.send(struct.pack("I", len(serialised)))
            for chunk in _chunks(toSend, 4096):
                sent_bytes += conn.send(chunk)
        except IOError as e:
            LOGGER.exception("Exception whilst sending data: %s" % e)
            return False

        LOGGER.debug("Data sent (%d bytes)" % sent_bytes)

        return True

    def _get_connection(self, module_name):
        try:
            return self._connections[module_name]
        except KeyError, e:
            return self._create_connection(module_name)

    def _remove_connection(self, module_name):
        try:
            del self._connections[module_name]
            return True
        except KeyError:
            return False

    def run(self, queue):
        queue_buffer = Queue()
        kill_received = False
        while True:
            try:
                if kill_received and queue_buffer.empty() and queue.empty():
                    LOGGER.debug("Flushed all data.")
                    break
                if not queue_buffer.empty():
                    (module_name, data) = queue_buffer.get()
                else:
                    (module_name, data) = queue.get(True)
                if(module_name == "RootNode"):
                    if data == None:
                        kill_received = True
                        LOGGER.debug("Shutdown signal received. Flushing data...")
                        continue
                elif data is not None:
                    connection = self._get_connection(module_name)
                    if connection is None:
                        queue_buffer.put((module_name, data)) #this will keep failed sends in the queue to send later...
                        continue
                    if not self._pickle_and_send(data, connection):
                        LOGGER.exception("Error writing data to network for module %s" % module_name)
                        self._remove_connection(module_name)
                        continue
                    else:
                        LOGGER.debug("Pickled and sent data for module %s" % module_name)
            except Empty:
                pass
            except KeyboardInterrupt:
                break
        LOGGER.debug("Networking queue processor shutting down...")
        sys.exit()

    def shutdown(self):
        self.send_data(("RootNode", None))

        LOGGER.debug("Sent kill request to Networking processor...")
