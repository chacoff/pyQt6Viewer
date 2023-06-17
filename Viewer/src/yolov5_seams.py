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

		blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (self.input_width, self.input_height), [0, 0, 0], 1, crop=False)

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

		# Resizing factor ->  @TODO @jaime: to do again!
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


if __name__ == '__main__':
	""" uncomment for local usage """
	#
	# def draw_label(input_image, label, left, top):
	# 	text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
	# 	dim, baseline = text_size[0], text_size[1]
	# 	cv2.rectangle(input_image, (left, top), (left + dim[0], top + dim[1] + baseline), (0, 0, 0), cv2.FILLED);
	# 	cv2.putText(input_image, label, (left, top + dim[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
	#
	# yolo = YoloV5sSeams()
	#
	# with open('classes.names', 'rt') as f:
	# 	classes = f.read().rstrip('\n').split('\n')
	#
	# """ @jaime: because my classes.names contains also color and threshold split by ',' and i am dropping rollprints
	# because there is only 5 classes for the moment """
	#
	# classes = [x.split(',')[0] for x in classes][:-1]
	# frame = cv2.imread('C:/Defects/3220/Seams/00_2080_030830_TX022083.png')
	#
	# net = cv2.dnn.readNet('best_exp18_768_5c_onnx7.onnx')  # weights to cv2.dnn
	#
	# detections = yolo.pre_process(frame, net)
	# input_image = frame.copy()
	# indices, class_ids, confidences, boxes = yolo.post_process(input_image, detections, classes)
	#
	# for i in indices:
	# 	box = boxes[i]
	# 	left = box[0]
	# 	top = box[1]
	# 	width = box[2]
	# 	height = box[3]
	# 	cv2.rectangle(input_image, (left, top), (left + width, top + height), (255, 178, 50), 3 * 1)
	# 	label = "{}:{:.2f}".format(classes[class_ids[i]], confidences[i])
	# 	draw_label(input_image, label, left, top)
	#
	# t, _ = net.getPerfProfile()
	# label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
	#
	# cv2.putText(input_image, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)
	# cv2.imshow('Output', input_image)
	# cv2.imwrite('output.png', input_image)
	# cv2.waitKey(0)
