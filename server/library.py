import traceback
from datetime import datetime

from mongoengine import *

from utils import Utils

connect('cctv')

Utils.msg("Client & fs created", "library")

class clip(DynamicDocument):
    data = FileField()
    pass

class analysis(DynamicDocument):
    pass

class logmsg(DynamicDocument):
    pass

def save_file(data, info):
    try:
        Utils.dbg("Saving file to database... info: %s" % info, "library.save_file")
        c = clip()
        c.data.put(data, content_type="video/h264")
        c.save_time = datetime.now()
        for x, y in info.iteritems():
            c.__setattr__(x, y)
        c.save()
    except Exception as e:
        Utils.err("Error saving file to mongodb: %s" % e, "library.save_file")
        traceback.print_exc()
        pass

def write(data):
    try:
        Utils.dbg("Saving data: %s to database..." % data, "library.write")
        c = analysis()
        for x, y in data.iteritems():
            c.__setattr__(x, y)
        c.save()
    except Exception as e:
        Utils.err("Error saving data to mongodb: %s" % e, "library.write")
        traceback.print_exc()
        pass

def log(text, level, sender):
    try:
        c = logmsg()
        c.message = text
        c.level = level
        c.sender = sender
        c.save_time = datetime.now()
        c.save()
        Utils.dbg("Logging: %s" % text, "library.log")
    except Exception as e:
        Utils.err("Error logging to mongodb: %s" % e, "library.log")
        traceback.print_exc()
        pass