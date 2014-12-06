from utils import Utils
from network.network import NetworkManager
from capture.capture import Capture
from analysis.analysis import Analysis
import signal


class Root:
	def __init__(self):
		self._networkManager = NetworkManager()
		self._networkManager.start()
		camera = Utils.getPiCamera()
		self._analysis = Analysis(camera)
		self._capture = Capture(self._networkManager, camera, self._analysis)


if __name__ == "__main__":
	#set signals behaviour
	signal.signal(signal.SIGINT, Utils.signal_handler)

	root = Root()
