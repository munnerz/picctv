from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Video(Base):
	__tablename__ = 'videos'

	video_id = Column(Integer, primary_key=True)
	camera_id = Column(Integer, ForeignKey('cameras.camera_id'))
	saved_at = Column(DateTime)
	file_name = Column(String)
	file_path = Column(String)
	file_length = Column(Integer)

	def __init__(self, camera_id, saved_at, file_name, file_path, file_length):
		self.camera_id = camera_id
		self.saved_at = saved_at
		self.file_name = file_name
		self.file_path = file_path
		self.file_length = file_length

class Camera(Base):
	__tablename__ = 'cameras'

	camera_id = Column(Integer, primary_key=True)