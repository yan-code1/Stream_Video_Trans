import json
import shutil
import struct
import os
import socket
import time
from threading import Thread
from ffmpy import video_coding

def getFilelist(dir):
    Filelist = []
    for home, dirs, files in os.walk(dir):
        for filename in files:
            path = os.path.join(home, filename)
            Filelist.append(path)
            # del file
            # shutil.move(path,targetPath)
            #shutil.rmtree('要清空的文件夹名')
            # os.mkdir('要清空的文件夹名')
            # os.remove('')
    return Filelist

def getVideoThread(videoSource,savePath = None,videoMaxNum = 10):
    # videoMaxNum = 10
    # videoSource = './xiao_li_yu.mp4'
    # videoSource = 0
    #清空
    savePath = './send'
    shutil.rmtree(savePath)
    os.mkdir(savePath)

    vc = video_coding(videoSource)
    for videoIdx in range(videoMaxNum):
        videoOut = './send/{}.mp4'.format(str(videoIdx))
        vc.setVideoOut(videoOut)
        num = 100
        vc.vf2img(num)
        video_bitrate = '100k'
        vc.img2vf(video_bitrate)

def videoSend(head,sk):
    '''
    head = {'filepath': r'./videos/1.mp4',
            'filename': r'',
            'filesize': None  }
    '''
    buffer = 4096
    file_path = head['filepath']#os.path.join(head['filepath'], head['filename'])
    file_name = head['filename']
    filesize = os.path.getsize(file_path)
    head['filesize'] = filesize
    json_head = json.dumps(head)
    bytes_head = json_head.encode('utf-8')
    print(json_head)
    # 计算head长度
    head_len = len(bytes_head)
    pack_len = struct.pack('i', head_len)
    sk.send(pack_len)  # 先发报头长度
    sk.send(bytes_head)  # 再发送byte类型的报头
    with open(file_path, 'rb') as f:
        while filesize:
            print(filesize)
            if filesize >= buffer:
                content = f.read(buffer)  # 每次读出来的内容
                sk.send(content)
                filesize -= buffer
            else:
                content = f.read(filesize)
                sk.send(content)
                break
def videoSendd(filepath,fileName,s):
    f = open(filepath, 'rb')
    count = 0
    flag = 1
    while True:
        if count == 0:
            data = bytes(fileName, encoding="utf8")
            start = time.time()
            s.sendto(data, client_addr)
        data = f.read(1024)
        if str(data) != "b''":
            s.sendto(data, client_addr)
            print(str(count) + 'byte')

        else:
            s.sendto('end'.encode('utf-8'), client_addr)
            break
        data, server_addr = s.recvfrom(1024)
        count += 1
    print('recircled' + str(count))
    end = time.time()
    print('cost' + str(round(end - start, 2)) + 's')
    # for data in [b'Michael',b'Tracy',b'Sarah']:
    #     s.sendto(data,('127.0.0.1',9999))
    #     print(s.recv(1024).decode('utf-8'))
    # s.close()

def videoSendThread(savePath,s):
    videoList = getFilelist(savePath)
    temp = videoList
    while True:
        videoList = getFilelist(savePath)
        if len(videoList) < 3:
            continue
        filepath = videoList[1] # 0:del  1:send  2:generate
        print('file:',filepath,filepath.split('/')[-1])
        videoSendd(filepath,filepath.split('/')[-1],s)
        os.remove(filepath)


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_addr = ('127.0.0.1', 12345)

videoSource ='./video.mp4'
savePath = './send/'
t1 = Thread(target = getVideoThread, args=(videoSource,)).start()
t2 = Thread(target = videoSendThread,args=(savePath,s,)).start()



