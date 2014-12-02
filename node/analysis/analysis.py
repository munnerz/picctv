import cv2

class Analysis:
	def __init__(self):
		self.thread = threading.Thread(target=self.run)
