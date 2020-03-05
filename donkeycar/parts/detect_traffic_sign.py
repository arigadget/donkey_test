"""
detect_traffic_sign.py
Classes to detect traffic sign using tpu.
"""
class DetectTS():
    # Function to read labels from text files.
    def ReadLabelFile(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        ret = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            ret[int(pair[0])] = pair[1].strip()
        return ret

    def __init__(self, model_path=None, label_path=None):
        from edgetpu.detection.engine import DetectionEngine
        #Webcam
        import time
        import cv2

        self.image_w = 160
        self.image_h = 120
        self.image_d = 3
        self.framerate = 20

        # initialize the camera and stream
        # /dev/video0
        fn_video = 1
        self.camera = cv2.VideoCapture(fn_video)

        print('WebCamera loaded.. .warming camera')
        time.sleep(2)

        # Initialize engine.
        #print('load traffic sign model')
        self.engine = DetectionEngine(model_path)
        self.labels = self.ReadLabelFile(label_path)
        
        self.on = True
        self.traffic_sign = None

    def inference_traffic_sign(self, image):
        import time
        import numpy
        from PIL import Image

        # Run inference
        pilImg = Image.fromarray(numpy.uint8(image))
        start_time = time.perf_counter()
        ans = self.engine.detect_with_image(pilImg, threshold=0.8, keep_aspect_ratio=True,
                                          relative_coord=False, top_k=1)
        end_time =  time.perf_counter()
        #print('Inference time:{:.7}'.format(end_time - start_time))

        # Display result.
        self.traffic_sign = None
        if ans:
            for obj in ans:
                if self.labels:
                    #print(self.labels[obj.label_id],'   ',obj.score)
                    self.traffic_sign = self.labels[obj.label_id]
                    print('detect: ', self.traffic_sign)

    def update(self):
        import cv2
        while self.on:
            ret, frame = self.camera.read()
            if ret == True: 
                self.traffic_sign = None
                height, width, channels = frame.shape[:3]
                #print("width: " + str(width))
                #print("height: " + str(height))
                frame = cv2.resize(frame, dsize=(320, 240))
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.inference_traffic_sign(self.frame)
            for i in range (5):
                img = self.camera.read()   
    
        self.camera.release()

    def run_threaded(self):
        return self.traffic_sign

    def shutdown(self):
        import time
        self.on = False
        print('Stopping inference')
        time.sleep(.5)
        del(self.camera)
