#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ffmpeg
import cv2
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
#https://ffmpeg.org/documentation.html
#https://www.jianshu.com/p/3c8c4a892f3c
#https://kkroening.github.io/ffmpeg-python/

#stream = ffmpeg.input('./xiao_li_yu.mp4')
#stream = ffmpeg.hflip(stream)
#stream = ffmpeg.output(stream, 'output.mp4',  b='100k',vcodec='libx265')
#ffmpeg.run(stream)

class video_coding:
    def __init__(self,videoSource):
        self.cap = cap = cv2.VideoCapture(videoSource)
        self.videoOut = None
        frames_num = cap.get(7)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = cap.get(3)
        height = cap.get(4)
        print("frames_num:%d\nfps:%d\nsize%s"%(frames_num,fps,(width, height)))
        
    def setVideoOut(self,videoOut):
        self.videoOut = videoOut

    def vf2img(self,nums):
        for num in range(nums):
            ret = False
            # take a frame from the video file
            try:
                ret, frame = self.cap.read()
            except:
                pass
	    
            # if read not success, break the loop and exit
            if ret != True:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()

            img_file = './imgs/img%.4d.jpg'% num
            cv2.imwrite(img_file,frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    def img2vf(self,video_bitrate):
        # Note that the serial number of the picture file in this place is right-aligned and zero-filled
        process = (
            ffmpeg.input('./imgs/img%4d.jpg',f='image2')
            .output(self.videoOut, video_bitrate =video_bitrate,vcodec='libx264',r =25,pix_fmt='yuv420p')#img2vf(self)
            .overwrite_output()
            .run_async(pipe_stdin=True,quiet= True)
        )
        process.communicate()
        print('which frame:',self.cap.get(cv2.CAP_PROP_POS_FRAMES),'End of encoding')

def main():
    videoMaxNum = 1
    # videoSource = './xiao_li_yu.mp4'
    videoSource = 0
    vc = video_coding(videoSource)

    for videoIdx in range(videoMaxNum):
        # videoOut = 'vvv.mp4'
        videoOut = './videos/{}.mp4'.format(str(videoIdx))
        vc.setVideoOut(videoOut)
        num = 100
        vc.vf2img(num)
        video_bitrate = '100k'
        vc.img2vf(video_bitrate)


if __name__ == '__main__':
    main()

