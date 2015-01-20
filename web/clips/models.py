from django.db import models
from django import forms
from mongoengine import *
from cctvweb.settings import DBNAME
from datetimewidget.widgets import DateTimeWidget

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

class ClipForm(forms.Form):
    start_datetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))
    end_datetime = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3))