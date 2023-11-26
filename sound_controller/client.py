from socket import *
import sys

host = 'localhost'
port = 777
addr = (host,port)

udp_socket = socket(AF_INET, SOCK_DGRAM)


data = input('write to server: ')
if not data : 
    udp_socket.close() 
    sys.exit(1)

data = str.encode(data)
udp_socket.sendto(data, addr)

while True:
    data = udp_socket.recvfrom(1024)
    print(data)


udp_socket.close()