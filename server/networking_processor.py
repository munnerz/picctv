import struct
import pickle
from multiprocessing.reduction import _rebuild_socket

from utils import Utils

def initialise_connection(fd):
    connection = fd
    try:
        Utils.dbg("Getting camera name & module name", "networking_processor.initialise_connection")
        camera_name_length = struct.unpack("I", connection.recv(4))[0] #read the camera ID
        camera_name_pickled = struct.unpack(str(camera_name_length) + 's', connection.recv(camera_name_length))[0]
        camera_name = pickle.loads(camera_name_pickled)

        module_name_length = struct.unpack("I", connection.recv(4))[0] #read the chunk ID
        module_name_pickled = struct.unpack(str(module_name_length) + 's', connection.recv(module_name_length))[0]
        module_name = pickle.loads(module_name_pickled)
        Utils.dbg("Got camera name '%s', module name '%s'" % (camera_name, module_name), "networking_processor.initialise_connection")

        return {"connection": fd, "module_name": module_name, "camera_name": camera_name}
    except Exception:
        Utils.err("Error initialising connection %s", "networking_processor.initialise_connection")
        raise #TODO: handle this gracefully

def process_incoming(connectionDict):
        connection = connectionDict['connection']
        try:
            data_length = struct.unpack("I", connection.recv(4))[0]
            Utils.dbg("Reading %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
                "networking_processor.process_incoming")
            data_pickled = struct.unpack(str(data_length) + 's', connection.recv(data_length))[0]
            data = pickle.loads(data_pickled)

            Utils.dbg("Read %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
                "networking_processor.process_incoming")
            return (connectionDict, data)
        except Exception:
            raise #todo:handle properly

        return None