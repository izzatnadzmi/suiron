import socket
import struct
import pandas as pd

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# host = input("Server hostname or ip? ")
host = '192.168.0.164'
# port = input("Server port? ")
port = 5051
sock.connect((host,port))
End = b'LOOOOLDFSODJOSSD'

while True:
    data = input("message: ")
    # sock.send(data)
    # raw_data = {
	   #          'image': [2,4,2,5,6,3,2,3], 
	   #          'servo': [22,42,5,45,34,534,2,3],
	   #          'motor': [23423,324,32,324,324,2,4,2]
	   #      }
    # df = pd.DataFrame(raw_data, columns=['image', 'servo', 'motor'])
    df = pd.read_csv('./data/output_3.csv', names=['image', 'servo', 'motor'])
    df = df.to_csv().encode()
    # sock.sendall(struct.pack('>i', len(df))+df)
    # sizee = struct.pack('>i', len(df))
    # print(sizee)
    # sock.sendall(sizee+df)
    sock.sendall(df+End)
    # sock.sendall(struct.pack('>i', len(data))+data)
    print("response: ", sock.recv(1024))

# import socket
# import threading

# class ThreadedServer(object):
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.sock.bind((self.host, self.port))

#     def listen(self):
#         self.sock.listen(5)
#         while True:
#             client, address = self.sock.accept()
#             client.settimeout(60)
#             threading.Thread(target = self.listenToClient,args = (client,address)).start()

#     def listenToClient(self, client, address):
#         size = 1024
#         while True:
#             try:
#                 data = client.recv(size)
#                 if data:
#                     # Set the response to echo back the recieved data 
#                     # response = data
#                     # client.send(response)
#                     print(data)
#                 else:
#                     raise error('Client disconnected')
#             except:
#                 client.close()
#                 return False

# if __name__ == "__main__":
#     while True:
#         port_num = input("Port? ")
#         try:
#             port_num = int(port_num)
#             break
#         except ValueError:
#             pass

#     ThreadedServer('',port_num).listen()
