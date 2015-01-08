from pymongo import MongoClient
from gridfs import GridFS

_CLIENT = MongoClient()
_FS = GridFS(_CLIENT.clips)
print("Client & fs created")

def save_file(data, info):
	try:
    	_FS.put(data, **info)
    except Exception as e:
        Utils.dbg("Error saving file to mongodb: %s" % e)
        pass

def write(data):
	try:
    	_CLIENT.analysis.insert(data)
    except Exception as e:
    	Utils.dbg("Error saving data to mongodb: %s" % e)
    	pass