import signal

from networking import Network
from utils import Utils, Settings

NETWORK = None

def main():
    global NETWORK

    NETWORK = Network()

try:
    if __name__ == "__main__":
        main()

except KeyboardInterrupt:
    Utils.msg("Server", "Shutting down...")
