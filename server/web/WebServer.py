import threading

from library.library import Library

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, asynchronous

class HelloHandler(RequestHandler):

	@asynchronous
	def get(self):
		self.render("templates/home.html", title="PiCCTV Control")

class WebServer(threading.Thread):

	def run(self):
		IOLoop.current().start()

	def make_app(self):
	    return Application([
			url(r"/", HelloHandler),
	        ])

	def __init__(self, library):
		threading.Thread.__init__(self)
		app = self.make_app()
		app.listen(8888)

