from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing import Queue
from Queue import Empty
from threading import Thread
from cPickle import dumps
from struct import pack
from time import sleep
from sys import exit

from node import settings


LOGGER = settings.logger("node.modules.Networking")

_connections = {}
_send_queue = Queue()
_process = None

def _chunks(lst, n):
    "Yield successive n-sized chunks from lst"
    for i in xrange(0, len(lst), n):
        yield lst[i:i+n]

def module_started():
    global _connections, _send_queue, _process
    LOGGER.info("Starting networking")
    _process = Thread(target=run, args=(_send_queue,))
    _process.start()

def process_data(data):
    global _send_queue
    _send_queue.put(data)
    return None

def _create_connection(module_name):
    global _connections
    sock = socket(AF_INET, SOCK_STREAM)

    try:
        sock.connect(arguments['server_address'])

        if _pickle_and_send(arguments['node_name'], sock) and _pickle_and_send(module_name, sock):
            _connections[module_name] = sock
            LOGGER.debug("Connection for module '%s' set up..." % module_name)
            return sock

    except IOError as e:
        LOGGER.exception("Error connecting to server for module %s (Exception: %s)" % (module_name, e))

    return None

def _pickle_and_send(d, conn):
    ''' serialises d and sends it over connection conn with a length header '''
    serialised = dumps(d, -1)
    toSend = pack(str(len(serialised)) + 's', serialised)

    sent_bytes = 0

    try:
        conn.send(pack("I", len(serialised)))
        for chunk in _chunks(toSend, 4096):
            sent_bytes += conn.send(chunk)
    except IOError as e:
        LOGGER.exception("Exception whilst sending data: %s" % e)
        return False

    LOGGER.debug("Data sent (%d bytes)" % sent_bytes)

    return True

def _get_connection(module_name):
    global _connections
    try:
        return _connections[module_name]
    except KeyError, e:
        return _create_connection(module_name)

def _remove_connection(module_name):
    global _connections
    try:
        del _connections[module_name]
        return True
    except KeyError:
        return False

def run(queue):
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
                (module_name, data) = queue.get()
            if(module_name == "RootNode"):
                if data == None:
                    kill_received = True
                    LOGGER.debug("Shutdown signal received. Flushing data...")
                    continue
            elif data is not None:
                connection = _get_connection(module_name)
                if connection is None:
                    queue_buffer.put((module_name, data))
                    sleep(1)
                    continue
                if not _pickle_and_send(data, connection):
                    LOGGER.exception("Error writing data to network for module %s" % module_name)
                    _remove_connection(module_name)
                    continue
                else:
                    LOGGER.debug("Pickled and sent data for module %s" % module_name)
        except Empty:
            sleep(0.1)
            pass
        except KeyboardInterrupt:
            pass
    LOGGER.debug("Networking queue processor shutting down...")

def shutdown_module():
    LOGGER.debug("Sending kill request to Networking processor...")
    send_data(("RootNode", None))

def name():
    return "Networking"