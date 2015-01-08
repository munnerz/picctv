import struct
import pickle
import socket
import threading
from multiprocessing.reduction import rebuild_handle, reduce_handle

from utils import Utils

def initialise_connection(connection):
    try:
        #connection = socket.fromfd(rebuild_handle(fd), socket.AF_INET, socket.SOCK_STREAM)
        Utils.dbg("Getting camera name & module name", "networking_processor")
        camera_name_length = struct.unpack("I", connection.recv(4))[0] #read the camera ID
        camera_name_pickled = struct.unpack(str(camera_name_length) + 's', connection.recv(camera_name_length))[0]
        camera_name = pickle.loads(camera_name_pickled)

        module_name_length = struct.unpack("I", connection.recv(4))[0] #read the chunk ID
        module_name_pickled = struct.unpack(str(module_name_length) + 's', connection.recv(module_name_length))[0]
        module_name = pickle.loads(module_name_pickled)
        Utils.dbg("Got camera name '%s', module name '%s'" % (camera_name, module_name), "networking_processor")

        return {"connection": connection, "connection_lock": threading.Lock(), "module_name": module_name, "camera_name": camera_name}
    except Exception as e:
        Utils.err("Error initialising connection: %s" % e, "networking_processor")
        raise #TODO: handle this gracefully

def process_incoming(connectionDict):
    try:
        with connectionDict['connection_lock']:
            connection = connectionDict['connection']
            data_length = struct.unpack("I", connection.recv(4))[0]
            Utils.dbg("Reading %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
                "networking_processor")
            grabbed = 0
            data_pickled = ''
            while len(data_pickled) < data_length:
                data_pickled = ''.join((data_pickled, connection.recv(data_length)))
            data_pickled = struct.unpack(str(data_length) + 's', data_pickled)[0]
            data = pickle.loads(data_pickled)

            Utils.dbg("Read %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
                "networking_processor")

            return (connectionDict, data)
    except Exception as e:
        Utils.err("%s whilst reading module data for module '%s' from camera '%s': %s" % 
            (type(e).__name__, connectionDict['module_name'], connectionDict['camera_name'], e),
            "networking_processor")
        pass

    return (connectionDict, None)
