from pymongo import MongoClient
from gridfs import GridFS

from utils import Utils

_CLIENT = MongoClient()
_DB = _CLIENT.cctv
_FS = GridFS(_DB)
print("Client & fs created")

def save_file(data, info):
    try:
        _FS.put(data, **info)
    except Exception as e:
        Utils.dbg("Error saving file to mongodb: %s" % e, "library.save_file")
        pass

def write(data):
    try:
        Utils.dbg("Saving data: %s to database..." % data, "library.write")
        _DB.analysis.insert(data)
    except Exception as e:
        Utils.dbg("Error saving data to mongodb: %s" % e, "library.write")
        pass