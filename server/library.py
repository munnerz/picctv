from pymongo import MongoClient
from gridfs import GridFS

from utils import Utils

_CLIENT = MongoClient()
_DB = _CLIENT.cctv
_FS = GridFS(_DB)

Utils.msg("Client & fs created", "library")

def save_file(data, info):
    try:
        Utils.dbg("Saving file to database... info: %s" % info, "library.write")
        _FS.put(data, **info)
    except Exception as e:
        Utils.err("Error saving file to mongodb: %s" % e, "library.save_file")
        pass

def write(data):
    try:
        Utils.dbg("Saving data: %s to database..." % data, "library.write")
        _DB.analysis.insert(data)
    except Exception as e:
        Utils.err("Error saving data to mongodb: %s" % e, "library.write")
        pass

def log(text, level, sender):
    try:
        _DB.logs.insert({"message": text, "level": level, "sender": sender})
        Utils.dbg("Logging: %s" % text, "library.log")
    except Exception as e:
        Utils.err("Error logging to mongodb: %s" % e, "library.log")
        pass