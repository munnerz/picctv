from django.db import models
from mongoengine import *
from cctvweb.settings import DBNAME

connect(DBNAME)

class logmsg(DynamicDocument):
    message = StringField()
    level = StringField()

class clip(DynamicDocument):
	data = FileField()
	save_time = DateTimeField()
	start_frame_index = LongField() 
	start_time = DateTimeField() 
	end_time = DateTimeField() 
	module_name = StringField() 
	end_frame_index = LongField() 
	camera_name = StringField()

class analysis(DynamicDocument):
    pass
