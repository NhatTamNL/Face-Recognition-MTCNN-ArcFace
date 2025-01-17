from keras.models import load_model
from mtcnn import MTCNN
from my_utils import alignment_procedure
# from tensorflow.keras.preprocessing import image
from keras_preprocessing import image
import ArcFace
import cv2
import numpy as np
import pandas as pd
import argparse

'''rtsp://192.168.2.86/user=test&password=123&channel=1&stream=0.sdp'''

######################
class_names = [
    'Chandel', 'Joey', 'Monica', 'Phoebe', 'Rachel', 'Ross'
]
######################

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--source", type=str, required=True,
                help="path to Video or webcam")
ap.add_argument("-m", "--model", type=str, required=True,
                help="path to saved .h5 model, eg: dir/model.h5")
ap.add_argument("-c", "--conf", type=float, default=0.9,
                help="min prediction conf (0<conf<1)")

args = vars(ap.parse_args())
source = args["source"]
path_saved_model = args["model"]
threshold = args["conf"]

if source.isnumeric():
    source = int(source)

# Load saved FaceRecognition Model
face_rec_model = load_model(path_saved_model, compile=True)

# Load MTCNN
detector = MTCNN()

# Load ArcFace Model
arcface_model = ArcFace.loadModel()
# arcface_model.load_weights("arcface_weights.h5")
target_size = arcface_model.layers[0].input_shape[0][1:3]

cap = cv2.VideoCapture(source)
count = 0

while True:
    success, img = cap.read()
    count +=10
    cap.set(cv2.CAP_PROP_POS_FRAMES,count)
    if not success:
        print('[INFO] Error with Camera')
        break

    detections = detector.detect_faces(img)
    if len(detections) > 0:
        for detect in detections:
            right_eye = detect['keypoints']['right_eye']
            left_eye = detect['keypoints']['left_eye']
            bbox = detect['box']
            xmin, ymin, xmax, ymax = int(bbox[0]), int(bbox[1]), \
                    int(bbox[2]+bbox[0]), int(bbox[3]+bbox[1])
            norm_img_roi = alignment_procedure(img, left_eye, right_eye, bbox)

            img_resize = cv2.resize(norm_img_roi, target_size)
            # what this line doing? must?
            img_pixels = image.img_to_array(img_resize)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_norm = img_pixels/255  # normalize input in [0, 1]
            img_embedding = arcface_model.predict(img_norm)[0]

            data = pd.DataFrame([img_embedding], columns=np.arange(512))

            predict = face_rec_model.predict(data)[0]
            # print(predict)
            if max(predict) > threshold:
                pose_class = class_names[predict.argmax()]
            else:
                pose_class = 'Unkown Person'
            
            # Show Result
            cv2.rectangle(
                img, (xmin, ymin), (xmax, ymax),
                (0, 255, 0), 2
            )
            cv2.putText(
                img, f'{pose_class}',
                (xmin, ymin-10), cv2.FONT_HERSHEY_PLAIN,
                2, (255, 0, 255), 2
            )

    else:
        print('[INFO] Eyes Not Detected!!')

    cv2.imshow('Output Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
print('[INFO] Inference on Videostream is Ended...')
