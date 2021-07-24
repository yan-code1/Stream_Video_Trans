import cv2
import queue
import subprocess as sp
import threading
import os

OUTPUT = 'rtmp://localhost:1935/live/test'
SIZE = (640,480)
class StreamPush():
    def __init__(self ,outputSource = OUTPUT ,sizeWanted = SIZE):
        self.max_size = 1
        self.frameQueue = queue.Queue()

        # ffmpeg config
        self.outputSource = outputSource
        self.command = ['ffmpeg',
        '-y',
        '-f', 'video4linux',
        '-s', "{}x{}".format(SIZE[0], SIZE[1]),
        '-i', '/dev/video0',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv',
        self.outputSource]
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)  # init pipe

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
        threadList = [threading.Thread(target=self.image_push, args=())]
        for t in threadList:
            t.start()

streamPush = StreamPush()
# streamPush.pushStart()