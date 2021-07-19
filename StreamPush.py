
import cv2
import queue
import subprocess as sp
import threading
import os

INPUT = 'http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8'
OUTPUT = 'rtmp://localhost:1935/live/test'
class StreamPush():
    def __init__(self,inputSourse = INPUT ,outputSource = OUTPUT):
        # source config
        self.cap = cv2.VideoCapture(inputSourse)         # stream media source
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
        self.outVideo = cv2.VideoWriter('./saveVideo.avi', self.fourcc, self.fps, (self.width, self.height))
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        # self.capReset(25,(640,480))

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

    def capReset(self, FPS, SIZE):
        # size
        WIDTH, HEIGHT = SIZE
        self.width = WIDTH
        self.height = HEIGHT
        self.fps = FPS
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        # FPS  default:600
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        # solve delay problem
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

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
        # 抽帧压入q队列
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
# import cv2
# import threading
# import time
#
#
# # import win32gui,win32con
#
#
# class Producer(threading.Thread):
#     """docstring for Producer"""
#
#     def __init__(self, rtmp_str):
#
#         super(Producer, self).__init__()
#
#         self.rtmp_str = rtmp_str
#
#         # 通过cv2中的类获取视频流操作对象cap
#         self.cap = cv2.VideoCapture(self.rtmp_str)
#
#         # 调用cv2方法获取cap的视频帧（帧：每秒多少张图片）
#         # fps = self.cap.get(cv2.CAP_PROP_FPS)
#         self.fps = self.cap.get(cv2.CAP_PROP_FPS)
#         print(self.fps)
#
#         # 获取cap视频流的每帧大小
#         self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         self.size = (self.width, self.height)
#         print(self.size)
#
#         # 定义编码格式mpge-4
#         self.fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', '2')
#
#         # 定义视频文件输入对象
#         self.outVideo = cv2.VideoWriter('saveDir1.avi', self.fourcc, self.fps, self.size)
#
#     def run(self):
#
#         print('in producer')
#
#         ret, image = self.cap.read()
#
#         while ret:
#             # if ret == True:
#
#             self.outVideo.write(image)
#
#             cv2.imshow('video', image)
#
#             cv2.waitKey(int(1000 / int(self.fps)))  # 延迟
#
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 self.outVideo.release()
#
#                 self.cap.release()
#
#                 cv2.destroyAllWindows()
#
#                 break
#
#             ret, image = self.cap.read()
#
#
# if __name__ == '__main__':
#     print('run program')
#     # rtmp_str = 'rtmp://live.hkstv.hk.lxdns.com/live/hks'  # 经测试，已不能用。可以尝试下面两个。
#     # rtmp_str = 'rtmp://media3.scctv.net/live/scctv_800'  # CCTV
#     rtmp_str = 'http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8'  # 湖南卫视
#
#     producer = Producer(rtmp_str)  # 开个线程
#     producer.start()

# # _*_ coding:utf-8 _*_
#
#
# '''
#
# python3
#
# opencv
#
# ffmpeg
#
# rtmp 推流视频直播pipe:: Invalid argumentb
#
# '''
#
# import cv2
#
# import subprocess
#
# import shlex
#
#
# # ffmpeg 推流
#
# class FfmpegRemp(object):
#
#     def __init__(self, rtmpfile, videoid):
#
#         self.rtmpUrl = "rtmp://127.0.0.1:1935/" + rtmpfilertsp://localhost:8888/live.sdp
#
#         self.video_stream_path = videoid
#
#         self.WIDTH = 640
#
#         self.HEIGHT = 420
#
#         self.FPS = 30.0
#
#         self.stat = True
#
#     def open_opencv(self):
#
#         cap = cv2.VideoCapture(self.video_stream_path, cv2.CAP_DSHOW)
#
#         # 设置摄像头设备分辨率
#
#
#
#         return cap
#
#     def open_ffmpeg(self):
#
#         cap = self.open_opencv()
#
#         fps = int(cap.get(cv2.CAP_PROP_FPS))
#
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#
#         # ffmpeg command
#
#         command = ['./ffmpeg.exe',
#
#                    '-y',
#
#                    '-f', 'rawvideo',
#
#                    '-vcodec', 'rawvideo',
#
#                    '-pix_fmt', 'bgr24',
#
#                    '-s', "{}x{}".format(width, height),
#
#                    '-r', str(fps),
#
#                    '-i', '-',
#
#                    '-c:v', 'libx264',
#
#                    '-pix_fmt', 'yuv420p',
#
#                    '-preset', 'ultrafast',
#
#                    '-f', 'flv',
#
#                    self.rtmpUrl]
#
#         # print(command)
#
#         # 管道配置
#
#         # self.p = sp.Popen(command, stdin=sp.PIPE, shell=True)
#
#         p = subprocess.Popen(command, stdin=subprocess.PIPE)
#
#         # read webcamera
#
#         print(cap.isOpened())
#
#         while (cap.isOpened()):
#
#             ret, frame = cap.read()
#
#             if not ret:
#
#                 print("Opening camera is failed")
#
#                 break
#
#             elif not self.stat:
#
#                 p.kill()
#
#                 print("停止推流")
#
#                 break
#
#             p.stdin.write(frame.tostring())
#
#     # 关闭直播
#
#     def close_ffmpeg(self):
#
#         self.stat = False
#
#         self.open_ffmpeg()
#
#
# if __name__ == "__main__":
#     # run_opencv_camera()
#
#     fr = FfmpegRemp("Live003", './video.mp4')
#
#     fr.open_ffmpeg()
