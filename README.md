PiCCTV
======

``picctv`` is a complete package to set up a reliable, scalable CCTV network with a plugin based system for doing analysis of frames that is tied into a server backend to store gathered data.

``picctv`` is designed to offload the analysis work onto Pi's, allowing for easy expansion as you add more cameras to it.

Componenets
-----------

* **Node** : The node software runs on any number of Raspberry Pi's. It provides a framework for developing analysis plugins to infer information/perform actions, and a system with which a plugin can return any type of serializable Pythonic data structure to be packaged and saved by the server.
* **Server** : The server accepts data from connected Nodes, and stores it away in a MongoDB backend. It is possible to write custom plugins for processing of Node data differently, otherwise it is just stored as-is.
* **Web** : The web client is a Django+Bootstrap3 interface for viewing notifications from the Server,  viewing clips that have been recorded and their associated analysis data.

Default Plugins (node)
----------------------

* **Motion** : does motion detection using a bespoke algorithm
* **Recording** : records h264 frames and sends them off to the server
* **Live** : sets up a basic TCP socket_server so users can view cameras data live

Requirements
------------

* node
	* `picamera <https://github.com/waveform80/picamera>`_ 1.9+
	* `opencv <https://github.com/Itseez/opencv>`
	* `numpy <https://github.com/numpy/numpy>`
* server
	* `mongoengine <https://github.com/MongoEngine/mongoengine>`
	* a correctly configured mongodb server
* web
	* `django <https://github.com/django/django>`
	* `django-graphos <https://github.com/agiliq/django-graphos>`
	* `django-bootstrap3 <https://github.com/dyve/django-bootstrap3>`
	* `mongoengine <https://github.com/MongoEngine/mongoengine>`

Notes/Ramblings
---------------

FFMPEG command to copy H264 video into an MP4 wrapper:
ffmpeg -i "cameraFront Door-2014-12-01 00:53:22.250299.h264" -vcodec copy -movflags faststart test.mp4

Info on piping in and out of FFMPEG: https://stackoverflow.com/questions/10400556/how-do-i-use-ffmpeg-with-python-by-passing-file-objects-instead-of-locations-to

server deps:

ffmpeg built with "--enable-gpl --enable-libx264 --enable-demuxer=mov" options

https://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/

Info about OpenCV (specifically getting number of msec into video): http://docs.opencv.org/modules/highgui/doc/reading_and_writing_images_and_video.html
