from multiprocessing import Process, Queue
import cPickle as pickle
import socket
import struct
import logging

from Queue import Empty

LOGGER = logging.getLogger(name="Networking")

def _chunks(lst, n):
    "Yield successive n-sized chunks from lst"
    for i in xrange(0, len(lst), n):
        yield lst[i:i+n]

class Networking(object):

    def __init__(self, camera_id, ip="cctv", port=8000):
        print("Starting networking")
        self._camera_id = camera_id
        self._ip = ip
        self._port = port
        self._connections = {}
        self._send_queue = Queue()
        self._process = Process(target=self.run, args=(self._send_queue,))
        self._process.start()

    def send_data(self, data):
        print("Queue size (SD): %d" % self._send_queue.qsize())
        self._send_queue.put(data)

    def _create_connection(self, module_name):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._ip, self._port))

        if self._pickle_and_send(self._camera_id, sock) and self._pickle_and_send(module_name, sock):
            self._connections[module_name] = sock
            print "Connection set up"
            return sock

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
            LOGGER.debug("Exception sending data...")
            return False

        print ("Data sent (%d bytes)" % sent_bytes)

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
        while True:
            try:
                (module_name, data) = queue.get(True, 0.1)
                print("Got data for module %s" % module_name)
                if(module_name == "RootNode"):
                    if data == None:
                        print ("Ending...")
                        break
                elif data is not None:
                    connection = self._get_connection(module_name)
                    if not self._pickle_and_send(data, connection):
                        print ("Error writing data to network for module %s" % module_name)
                        self._remove_connection(module_name)
                        continue
                    else:
                        print ("Pickled and sent data for module %s" % module_name)
            except Empty:
                pass
            except KeyboardInterrupt:
                break
        print ("Run method complete")

    def shutdown(self):
        self.send_data(("RootNode", None))
        self._process.join()
