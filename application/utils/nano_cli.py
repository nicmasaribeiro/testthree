import socket

global HOST
HOST = socket.gethostname()

class Nano:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket()
        try:
            sock.connect((self.host, self.port))
            sock.sendall("Connected".encode())
            while True:
                input_datastream = sock.recv(1024).decode()
                if not input_datastream:
                    break  # Exit the loop if the connection is closed by the server
                print(input_datastream)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            sock.close()
#
#cli = Nano(HOST, 90)
#cli.run()
