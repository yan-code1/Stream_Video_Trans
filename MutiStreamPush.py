import cv2
import sys
if sys.version > '3':
	from queue import Queue
else:
	from Queue import Queue

import queue
import subprocess as sp
import threading
import os

INPUT = 0  # 'http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8'
OUTPUT = 'rtmp://127.0.0.1:1935/live/stream'
streamNum =2           #    推流个数
rate = [str(100+i*100)+'k' for i in range(streamNum) ] #[100k ,200k ,300k ,.....]
outPut = [OUTPUT + str(i) for i in range(streamNum)]
SIZE = (640, 480)
print(rate)

class StreamPush():
    global rate
    def __init__(self, strNum = streamNum,inputSourse=INPUT, outputSource=outPut, sizeWanted=SIZE):
        # source config
        self.strNum = strNum
        self.cap = cv2.VideoCapture(inputSourse)  # stream media source
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        # self.fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
        # self.outVideo = cv2.VideoWriter('./saveVideo.avi', self.fourcc, self.fps, (self.width, self.height))
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.SCALE_FLAG = False
        self.capReset(25, sizeWanted)

        # queue config
        self.max_size = 1
        self.frameQueue = Queue()

        # ffmpeg config
        self.outputSource = outputSource
        self.cmd = []
        self.pipes = []
        self.command = ['ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(640, 480),
                        '-r', str(self.fps),#推流输出fps
                        '-i', '-',
                        '-c:v', 'libx264',#h264编码库
                        '-b:v', '100k',#码率
                        # '-bufsize' '200k',
                        '-pix_fmt', 'yuv420p',#
                        '-preset', 'ultrafast',
                        '-f', 'flv']

        for i in range(self.strNum):
            cmd_temp = self.command.copy()
            cmd_temp.append(outputSource[i])
            cmd_temp[-8] = rate[i]
            self.cmd.append(cmd_temp)
            self.pipes.append(sp.Popen(cmd_temp, stdin=sp.PIPE))

        #
        print(type(self.pipes[0]))



    def capReset(self, fps, size):
        # size
        width, height = size
        self.width = width
        self.height = height
        self.fps = fps
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # FPS  default:600
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        # solve delay problem
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.SCALE_FLAG = True

    def isMediaRead(self):
        if self.cap.isOpened():
            print('get stream media successfully')
            print('FPS ：{} size：{}'.format(self.fps, (self.width, self.height)))
            return True
        else:
            print('faild to get stream media ')
            return False

    def save(self, frame, imgIdx):
        save_path = 'save_folder'
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        # image
        save = os.path.join(save_path, '%s.jpg' % str(imgIdx))
        cv2.imwrite(save, frame)
        # video
        self.outVideo.write(frame)

        print('saved')

    def image_sample(self):
        while True:
            self.frameQueue.put(self.cap.read()[1])
            if self.frameQueue.qsize() > self.max_size:
                self.frameQueue.get()  # lastest frame

    def image_push(self):
        while True:
            if not self.frameQueue.empty():
                frame = self.frameQueue.get()
                if frame is not None:
                    self.temp = frame
                if self.SCALE_FLAG:
                    frame = cv2.resize(frame, (640, 480))
                for i in range(self.strNum):
                    self.pipes[i].stdin.write(self.temp.tostring())


    def pushStart(self):
        if self.isMediaRead():
            threadList = [threading.Thread(target=self.image_sample, args=()),
                          threading.Thread(target=self.image_push, args=())]
            for t in threadList:
                t.start()
        else:
            print("resource error!")


streamPush = StreamPush()
streamPush.pushStart()