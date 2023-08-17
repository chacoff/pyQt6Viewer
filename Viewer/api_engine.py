""" https://github.com/BlueMirrors/Yolov5-ONNX
based on that repo implementation, which is also based in the original ultralytics
basically i took the repo and i made available parameters such as score, confidence and iou
J.
"""

import cv2
from cvuMaster.cvu.detector.yolov5 import Yolov5 as Yolov5Onnx


class YoloV5OnnxSeams:

    def __init__(self):
        super().__init__()
        self.drawing = False
        self.device = 'cpu'  # possibility of gpu
        self.weight = None
        self.input_image_path = None
        self.output_image = None
        self.preds = None

    def process_image(self, classes: any, weight: any, input_image: any, conf: list, iou: list):

        """
        :param classes: a list with all the classes
        :param weight: a reference of the model since is loaded at the very beginning while starting the app
        :param input_image: a MAT image
        :param conf: list of confidence threshold for inference
        :param iou: list of iou threshold for NMS
        :return: predictions preds contaning bbox, class_name, confidence and instance id
        """

        model = Yolov5Onnx(classes=classes,
                           backend="onnx",
                           weight=weight,
                           device=self.device,
                           conf=conf,
                           iou=iou)

        self.preds = model(input_image)

        # drawing is only meant for local usage since all drawings should happen in the Qt interface
        if self.drawing:
            self.preds.draw(input_image)
            self.output_image = input_image

    def return_predictions(self):
        return self.preds

