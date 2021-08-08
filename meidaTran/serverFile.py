import json
import os
import socket
import struct
count = 0
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('127.0.0.1', 12345)
s.bind(server_addr)
savePath = './recv/'
print('Bind UDP...')
while True:
    while True:
        if count == 0:
            fileName,client_addr = s.recvfrom(1024)
            print('connected from %s:%s'%client_addr)
            f = open(savePath+str(fileName, encoding = "utf-8"), 'wb')
        data, client_addr = s.recvfrom(1024)
        if str(data) != "b'end'":
            f.write(data)
            print('recieved '+str(count)+' byte')
        else:
            print('waiting for next video')
            break
        s.sendto('ok'.encode('utf-8'),client_addr)
        count+=1
    print('recercled'+str(count))
    count = 0
f.close()
s.close()
