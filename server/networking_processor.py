import struct
import pickle
import socket
from multiprocessing.reduction import rebuild_handle, reduce_handle

from utils import Utils

def initialise_connection(connection):
    try:
        #connection = socket.fromfd(rebuild_handle(fd), socket.AF_INET, socket.SOCK_STREAM)
        Utils.dbg("Getting camera name & module name", "networking_processor.initialise_connection")
        camera_name_length = struct.unpack("I", connection.recv(4))[0] #read the camera ID
        camera_name_pickled = struct.unpack(str(camera_name_length) + 's', connection.recv(camera_name_length))[0]
        camera_name = pickle.loads(camera_name_pickled)

        module_name_length = struct.unpack("I", connection.recv(4))[0] #read the chunk ID
        module_name_pickled = struct.unpack(str(module_name_length) + 's', connection.recv(module_name_length))[0]
        module_name = pickle.loads(module_name_pickled)
        Utils.dbg("Got camera name '%s', module name '%s'" % (camera_name, module_name), "networking_processor.initialise_connection")

        return {"connection": connection, "module_name": module_name, "camera_name": camera_name}
    except Exception as e:
        Utils.err("Error initialising connection %s" % e, "networking_processor.initialise_connection")
        raise #TODO: handle this gracefully

def process_incoming(connectionDict):
    try:
        #print ("Processing...")
        #hndl = rebuild_handle(connectionDict['connection'])
        #print ("Rebuilt handle")
        #connection = socket.fromfd(hndl, socket.AF_INET, socket.SOCK_STREAM)
        connection = connectionDict['connection']
        data_length = struct.unpack("I", connection.recv(4))[0]
        Utils.dbg("Reading %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
            "networking_processor.process_incoming")
        grabbed = 0
        data_pickled = ''
        while grabbed < data_length:
            data_pickled = ''.join((data_pickled, connection.recv(data_length)))
        data_pickled = struct.unpack(str(data_length) + 's', data_pickled)[0]
        data = pickle.loads(data_pickled)

        Utils.dbg("Read %d bytes from %s/%s" % (data_length, connectionDict["camera_name"], connectionDict["module_name"]),
            "networking_processor.process_incoming")

        return ({ "module_name": connectionDict['module_name'], "camera_name": connectionDict['camera_name']}, data)
    except Exception as e:
        print "EXCEPTION: %s" % e
        raise #todo:handle properly
    print "RETURNING NONE"
    return None
