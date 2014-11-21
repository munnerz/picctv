import socket
import threading
import time

class CaptureStream(threading.Thread):
    def __init__(self, connection, output=open('out.h264', 'wb')):
        threading.Thread.__init__(self)
        self._connection = connection
        self._output = output
        self._recording = True

    def run(self):
        try:
            while self._recording:
                data = self._connection.read(1024)
                if not data:
                    break
                self._output.write(data)
        finally:
            connection.close()

    def stop(self):
        self._recording = False


# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
sock_addr = ('0.0.0.0', 8000)

server_socket = socket.socket()
server_socket.bind(sock_addr)
server_socket.listen(0)
print ("Listening for connections on %s:%d" % sock_addr)
try:
    while True:
        # Accept a single connection and make a file-like object out of it
        connection = server_socket.accept()[0].makefile('rb')
        connectionHandler = CaptureStream(connection, open('/recordings/capture-%d.h264' % int(time.time()), 'wb'))
        connectionHandler.start()
        print ("Accepted connection")
finally:
    server_socket.close()
