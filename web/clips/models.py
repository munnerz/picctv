from django.db import models
from mongoengine import *
from cctvweb.settings import DBNAME

connect(DBNAME)

class logs(DynamicDocument):
	pass

class analysis(DynamicDocument):
    pass
# Create your models here.
