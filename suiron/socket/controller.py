import socket
import threading

class Server(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.address = None

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            # client.settimeout(60)
            # threading.Thread(target = self.listenToClient,args = (client,address)).start()
            return client, address

    def listenToClient(self, client, address):
        size = 102
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    print(response)
                    client.send(response)
                else:
                    raise error('Client disconnected')
            except:
                print('closing')
                client.close()
                return False

    def __del__(self):
        if self.sock:
            self.sock.close()


if __name__ == "__main__":
    while True:
        port_num = input("Port? ")
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    Server('',port_num).listen()