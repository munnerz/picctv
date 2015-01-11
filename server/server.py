import signal

import global_vars
from networking import Network
from utils import Utils, Settings

def main():
   global_vars.NETWORK = Network()

try:
    if __name__ == "__main__":
        Utils.weblog("Starting...", "success", "Server")
        main()

except KeyboardInterrupt:
    Utils.msg("Server", "Shutting down...")
    Utils.weblog("Shutting down...", "warning", "Server")
