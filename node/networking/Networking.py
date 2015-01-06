from multiprocessing import Process, Queue

class Networking(object):

    def __init__(self, ip="cctv", port=8080):
        print("Starting networking")
        self._ip = ip
        self._port = port

        self._send_queue = Queue()
        self._process = Process(target=self.run, args=(self._send_queue,))
        self._process.start()

    def send_data(self, data):
        self._send_queue.put(data)

    def run(self, queue):
        while True:
            (module_name, data) = queue.get(True)
            if data is not None:
                print ("Processing CMD from module %s" % module_name)
                #send data off
            else:
                break
        print ("Killing Networking process as 'None' value detected in queue")

