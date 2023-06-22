import concurrent.futures
import queue


def process_item(item):
    # Perform some processing on the item
    processed_item = item * 1

    # Simulate some delay in processing
    import time
    time.sleep(0.3)

    return processed_item


def main():
    input_queue = queue.Queue()
    output_queue = queue.Queue()

    # Enqueue items
    input_queue.put(1)
    input_queue.put(2)
    input_queue.put(3)
    input_queue.put(4)
    input_queue.put(5)

    def process_queue_item(item):
        processed_item = process_item(item)
        output_queue.put(processed_item)

    # Start processing items concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while not input_queue.empty():
            item = input_queue.get()
            executor.submit(process_queue_item, item)

    executor.shutdown()

    while not output_queue.empty():
        processed_item = output_queue.get()
        print(processed_item)


if __name__ == '__main__':
    main()



# def draw_label(input_image, label, left, top):
#     text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)
#     dim, baseline = text_size[0], text_size[1]
#     cv2.rectangle(input_image, (left, top), (left + dim[0], top + dim[1] + baseline), (0, 0, 0), cv2.FILLED);
#     cv2.putText(input_image, label, (left, top + dim[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1, cv2.LINE_AA)
#
#
# yolo = YoloV5sSeams()
#
# with open('../Viewer/src/classes.names', 'rt') as f:
#     classes = f.read().rstrip('\n').split('\n')
#
# #  @jaime: classes.names contains also color and threshold split by ',' and dropping rollprints
# classes = [x.split(',')[0] for x in classes][:-1]
# frame = cv2.imread('C:/Defects/3220/Seams/00_2080_030830_TX022083.png')
#
# net = cv2.dnn.readNetFromONNX('../Viewer/src/best_exp18_768_5c_onnx7.onnx')  # weights to cv2.dnn
#
# detections = yolo.pre_process(frame, net)
# input_image = frame.copy()
# indices, class_ids, confidences, boxes = yolo.post_process(input_image, detections, classes)
#
# for i in indices:
#     box = boxes[i]
#     left = box[0]
#     top = box[1]
#     width = box[2]
#     height = box[3]
#     cv2.rectangle(input_image, (left, top), (left + width, top + height), (255, 178, 50), 3 * 1)
#     label = "{}:{:.2f}".format(classes[class_ids[i]], confidences[i])
#     draw_label(input_image, label, left, top)
#
# t, _ = net.getPerfProfile()
# label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
#
# cv2.putText(input_image, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)
# cv2.imshow('Output', input_image)
# # cv2.imwrite('output.png', input_image)
# cv2.waitKey(0)