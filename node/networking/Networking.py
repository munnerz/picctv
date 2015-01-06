from multiprocessing import Process, Queue
import cPickle as pickle
import socket, struct
from Queue import Empty

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
        conn.send(struct.pack("I", len(serialised)))
        conn.send(struct.pack(str(len(serialised)) + 's', serialised))
        return True

    def _get_connection(self, module_name):
        try:
            return self._connections[module_name]
        except KeyError, e:
            return self._create_connection(module_name)

    def run(self, queue):
        while True:
            try:
                (module_name, data) = queue.get(True, 0.1)
                if(module_name == "RootNode"):
                    if data == None:
                        break
                elif data is not None:
                    connection = self._get_connection(module_name)
                    if not self._pickle_and_send(data, connection):
                        print ("Error writing data to network for module %s" % module_name)
            except Empty:
                pass
            except KeyboardInterrupt:
                break
        print ("Run method complete")

    def shutdown(self):
        self.send_data(("RootNode", None))
        self._process.join()
