import cv2
from mtcnn.mtcnn import MTCNN
import tensorflow as tf
detector = MTCNN()

# video = cv2.VideoCapture('rtsp://192.168.2.86/user=test&password=123&channel=1&stream=0.sdp')
video = cv2.VideoCapture('1.mp4')

    
if (video.isOpened() == False):
    print("Web Camera not detected")
while (True):
    ret, frame = video.read()
    if ret == True:
        location = detector.detect_faces(frame)
        if len(location) > 0:
            for face in location:
                x, y, width, height = face['box']
                x2, y2 = x + width, y + height
                cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 255), 4)
        cv2.imshow("Output",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

video.release()
cv2.destroyAllWindows()