import cv2
import numpy as np


class YoloV5sSeams:

	def __init__(self):
		super().__init__()
		self.input_width = 768
		self.input_height = 768
		self.score_threshold = 0.05
		self.nms_threshold = 0.20
		self.confidence_threshold = 0.15

	def pre_process(self, input_image, net):
		""" creates a 4D blob from an image and sets the input to the network,
		runs the forward pass and gets the outputs layers """

		blob = cv2.dnn.blobFromImage(input_image, 1/255, (self.input_width, self.input_height), swapRB=True, crop=False)
		# blob_alex = blob.reshape(blob.shape[2], blob.shape[3]*blob.shape[1], 1)
		net.setInput(blob)

		output_layers = net.getUnconnectedOutLayersNames()
		outputs = net.forward(output_layers)
		# print(outputs[0].shape)

		return outputs

	def post_process(self, input_image, outputs, classes):
		""" clean up the raw yolo results using the score thresholds and NMS"""

		class_ids = []
		confidences = []
		boxes = []

		# Rows
		rows = outputs[0].shape[1]

		image_height, image_width = input_image.shape[:2]

		# Resizing factor ->
		x_factor = image_width / self.input_width
		y_factor = image_height / self.input_height

		# Iterate through 25200 detections.
		for r in range(rows):
			row = outputs[0][0][r]
			confidence = row[4]

			# Discard bad detections and continue.
			if confidence >= self.confidence_threshold:
				classes_scores = row[5:]

				# Get the index of max class score.
				class_id = np.argmax(classes_scores)

				# Continue if the class score is above threshold.
				if classes_scores[class_id] > self.score_threshold:
					confidences.append(confidence)
					class_ids.append(class_id)

					cx, cy, w, h = row[0], row[1], row[2], row[3]

					left = int((cx - w / 2) * x_factor)
					top = int((cy - h / 2) * y_factor)
					width = int(w * x_factor)
					height = int(h * y_factor)

					box = np.array([left, top, width, height])
					boxes.append(box)

		# NMS to supress redundant overlapping boxes with lower confidences.
		indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)

		return indices, class_ids, confidences, boxes
