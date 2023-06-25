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
        # @TODO unused for the moment since all these are hardcode
        self.input_width = 768
        self.input_height = 768
        self.score_threshold = 0.20
        self.nms_threshold = 0.20
        self.confidence_threshold = 0.20

        self.drawing = False
        self.device = 'cpu'  # possibility of gpu
        self.weight = None
        self.input_image_path = None
        self.output_image = None
        self.preds = None

    def process_image(self, classes, weight, input_image):
        """ input_image is a CV Mat image
        preds are an object with all predictions containing
        bbox, class_name, confidence and instance id
        """
        model = Yolov5Onnx(classes=classes,
                           backend="onnx",
                           weight=weight,
                           device=self.device)

        self.preds = model(input_image)

        # drawing is only meant for local usage since all drawings should happen in the Qt interface
        if self.drawing:
            self.preds.draw(input_image)
            self.output_image = input_image

    def return_predictions(self):
        return self.preds


if __name__ == "__main__":
    """ local usage """

    device = 'cpu'  # cpu or gpu
    weight = './src/best_exp_Nano_v2_768_5c.onnx'
    input_image = 'C:/Users/gomezja/PycharmProjects/201_SeamsModel/dataset/dev/ZH026_2060_009560_TX000021.png'
    output_image = 'test1.png'
    classes = ['Seams', 'Beam', 'Souflure', 'Hole', 'Water']

    input_image = cv2.imread(input_image)

    inference = YoloV5OnnxSeams()
    inference.process_image(classes, weight, input_image)
    predictions = inference.return_predictions()
    print(predictions)

    # activate drawing to pass properly the image
    # cv2.imwrite(output_image, inference.output_image)

    for i in range(len(predictions)):
        print(predictions[i].class_id)
        print(predictions[i].class_name)
        print(predictions[i].bbox)
        print(predictions[i].confidence)

    for attr, value in predictions.__dict__.items():
        print(attr, value)
