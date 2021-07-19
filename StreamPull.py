import cv2
# import threading
# import dlib
# import imutils
# from imutils import face_utils

SmtpUrl = "rtmp://localhost:1935/live/test"
cap = cv2.VideoCapture(SmtpUrl)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
size = (width, height)
print("size: ",size)
print("FPS: ",fps)
while True:
    try:
        ret, image = cap.read()

        while ret:
            # frame = imutils.resize(image, width=600)
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # rects = detector(gray, 0)
            # for rect in rects:
            #     shape = predictor(gray, rect)
            #     # shape = face_utils.shape_to_np(shape)
            #     target = shape[targetStart:targetEnd]
            #     targetHull = cv2.convexHull(target)
            #     cv2.drawContours(frame, [targetHull], -1, (0, 255, 0), 1)
            #     cv2.putText(frame, "target", (target[0][0], target[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Frame", image)
            cv2.waitKey(int(1000 / int(fps)))  # delay
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                break
            ret, image = cap.read()
    except:

        pass

