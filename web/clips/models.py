from django.db import models
from mongoengine import *
from cctvweb.settings import DBNAME

connect(DBNAME)

class logs(DynamicDocument):
    message = StringField()
    level = StringField()

class clip(DynamicDocument):
    pass

class analysis(DynamicDocument):
    pass
