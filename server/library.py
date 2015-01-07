from pymongo import MongoClient

_CLIENT = MongoClient()
_FS = GridFS(_CLIENT.clips)
print("Client & fs created")

class Writer:
    def __init__(self, module_name, db_name="analysis"):
        self.module_name = module_name
        self.db_name = db_name

    def save_file(self, data, metadata):
        _FS.put(data, **metadata)

    def write(self, data):
        _CLIENT[self.db_name].insert(dict({"module_name": self.module_name}, **data))