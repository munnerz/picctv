from pymongo import MongoClient
from gridfs import GridFS

_CLIENT = MongoClient()
_FS = GridFS(_CLIENT.clips)
print("Client & fs created")

def save_file(data, info):
    _FS.put(data, **info)

def write(data):
    _CLIENT.analysis.insert(data)