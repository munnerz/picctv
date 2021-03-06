import struct
import pickle
import socket
from multiprocessing.reduction import rebuild_handle, reduce_handle

from utils import Utils
import modules

# this method initialises a new connection from a node
# it receives the camera and modules name, and constructs
# a dictionary of information relating to this connection
# for use in the process_incoming and various other functions
def initialise_connection(connection):
    try:
        Utils.dbg("Getting camera name & module name", "networking_processor")
        camera_name_length = struct.unpack("I", connection.recv(4))[0] #read the camera ID
        camera_name_pickled = struct.unpack(str(camera_name_length) + 's', connection.recv(camera_name_length))[0]
        camera_name = pickle.loads(camera_name_pickled)

        module_name_length = struct.unpack("I", connection.recv(4))[0] #read the chunk ID
        module_name_pickled = struct.unpack(str(module_name_length) + 's', connection.recv(module_name_length))[0]
        module_name = pickle.loads(module_name_pickled)
        Utils.dbg("Got camera name '%s', module name '%s'" % (camera_name, module_name), "networking_processor")

        Utils.weblog("'%s' module on '%s' started." % (module_name, camera_name), "info", "Networking")

        return {"connection": connection, "module_name": module_name, "camera_name": camera_name, "active": True}
    except Exception as e:
        Utils.err("Error initialising connection: %s" % e, "networking_processor")
        raise #TODO: handle this gracefully

# one instance of this function is executed per connection
# the function will not return until the connection
# closes. it receives data from the node, and sends
# it to the module post-processor for storage.
def process_incoming(connectionDict):
    while connectionDict['active']:
        try:
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

            modules.process_data((connectionDict, data))
        except Exception as e:
            Utils.err("%s whilst reading module data for module '%s' from camera '%s': %s" % 
                (type(e).__name__, connectionDict['module_name'], connectionDict['camera_name'], e),
                "networking_processor")
            modules.process_data((connectionDict, None))
            pass
            break
    Utils.dbg("Thread for module '%s' from camera '%s' ending..." % 
        (connectionDict['module_name'], connectionDict['camera_name']), "networking_processor")
