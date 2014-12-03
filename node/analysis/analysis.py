import io
import time
import threading
import picamera
from utils import Utils, Settings

frameNumber = 0
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self):
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):
        # This method runs in a separate thread
        global frameNumber, lock, pool
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    print ("Processing frame... %d" % frameNumber)
                    frameNumber += 1
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)


class Analysis:
	def __init__(self, camera):
		global pool, lock
		self.thread = threading.Thread(target=self.run)

		# Create a pool of image processors
		pool = [ImageProcessor() for i in range(4)]

		self._keepRecording = True
		self._camera = camera
		self.thread.start()


	def streams(self):
		global pool, lock
		while self._keepRecording:
			with lock:
				if pool:
					processor = pool.pop()
				else:
					processor = None
			if processor:
				yield processor.stream
				processor.event.set()
			else:
				# When the pool is starved, wait a while for it to refill
				time.sleep(0.1)


	def run(self):
		global pool, lock
		self._camera.capture_sequence(self.streams(), format='bgr', use_video_port=True, resize=(1280,720), splitter_port=2)

		# Shut down the processors in an orderly fashion
		while pool:
			with lock:
				processor = pool.pop()
			processor.terminated = True
			processor.join()


