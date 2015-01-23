import time

import global_vars
from networking import Network
from utils import Utils


def main():
   global_vars.NETWORK = Network()

if __name__ == "__main__":
    Utils.weblog("Starting...", "success", "Server")
    main()

    try:
        time.sleep(1)
    except KeyboardInterrupt:
        Utils.msg("Server", "Shutting down...")
        Utils.weblog("Shutting down...", "warning", "Server")
        global_vars.NETWORK.shutdown()
