import signal

import global_vars
from networking import Network
from utils import Utils, Settings

def main():
   global_vars.NETWORK = Network()

try:
    if __name__ == "__main__":
        main()

except KeyboardInterrupt:
    Utils.msg("Server", "Shutting down...")
