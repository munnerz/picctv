from pymongo import MongoClient
from gridfs import GridFS

_CLIENT = MongoClient()
_FS = GridFS(_CLIENT.clips)
print("Client & fs created")

class Writer:
    def __init__(self, db_name="analysis"):
        self.db_name = db_name

    def save_file(self, i):
        (info, data) = i
        _FS.put(data, **info)

    def write(self, data):
        _CLIENT[self.db_name].insert(data)