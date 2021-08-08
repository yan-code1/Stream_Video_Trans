import ffmpeg
INPUT = 'http://ivi.bupt.edu.cn/hls/cctv1hd.m3u8'
OUTPUT = 'rtmp://localhost:1935/live/sss1'
SIZE = (640,480)
class StreamPush():
    def __init__(self,inputSourse = INPUT ,outputSource = OUTPUT ,sizeWanted = SIZE):

        self.width,self.height = sizeWanted
        self.fps = 50
        self.outputSource = outputSource
        self.VideoReadProcess = (
            ffmpeg
                .input(inputSourse)
                .output(
                outputSource,
                listen=1,
                r = str(self.fps),
                pix_fmt='yuv420p',
                f='flv',
                s="{}x{}".format(self.width, self.height)
                ).global_args("-re")  # argument to act as a live stream
        )
    def pushStart(self):
        self.VideoReadProcess.run()

streamPush = StreamPush()
streamPush.pushStart()
