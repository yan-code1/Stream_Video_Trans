import cv2
import queue
import subprocess as sp
import threading
import os

INPUT = 'http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8'
OUTPUT = 'rtmp://localhost:1935/live/test'
SIZE = (640,480)
class StreamPush():
    def __init__(self,inputSourse = INPUT ,outputSource = OUTPUT ,sizeWanted = SIZE):
        # source config
        self.cap = cv2.VideoCapture(inputSourse)         # stream media source
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
        self.outVideo = cv2.VideoWriter('./saveVideo.avi', self.fourcc, self.fps, (self.width, self.height))
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.SCALE_FLAG = False
        self.capReset(25,sizeWanted)

        # queue config
        self.max_size = 1
        self.frameQueue = queue.Queue()

        # ffmpeg config
        self.outputSource = outputSource
        self.command = ['ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(self.width, self.height),
        '-r', str(self.fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv',
        self.outputSource]
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)  # init pipe

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
                # image deal
                # frame = cv2.putText(frame, 'sent rtmp frame', (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 255), 5)
                if self.SCALE_FLAG:
                    frame = cv2.resize(frame, (640, 480))
                    # frame = cv2.resize(frame, (640, 480), fx=0.25, fy=0.25, interpolation=cv2.INTER_NEAREST)
                self.pipe.stdin.write(frame.tostring())

                # cv2.imshow("frame", frame)
                # cv2.waitKey(0)

                # save = os.path.join(save_path,'%s.jpg'%str(i))
                # cv2.imwrite(save,frame)
                # print('saved')
                # i+=1

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