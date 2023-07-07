from collections import deque
from threading import Lock, Thread
import socket
import sys
import pickle
import cv2
import numpy as np
from YoloV5_Onnx_detect import YoloV5OnnxSeams
import onnxruntime
from timeit import default_timer as timer
from src.production_config import XMLConfig


class Buffer:
    def __init__(self):
        self._buffer: any = deque()
        self._mutex = Lock()

    def __len__(self) -> int:
        with self._mutex:
            return len(self._buffer)

    def queue(self, item: any) -> None:
        with self._mutex:
            self._buffer.append(item)

    def dequeue(self) -> any:
        with self._mutex:
            if self._buffer:
                return self._buffer.popleft()
            else:
                raise IndexError('Buffer is empty. Cannot dequeue')

    def is_empty(self) -> bool:
        return len(self._buffer) == 0


class TCP:
    """ server """
    def __init__(self, buff, params):
        self._buffer = buff
        self._host: str = str(params.get_value('TcpSocket', 'ip_to_listen'))
        self._port: int = int(params.get_value('TcpSocket', 'port_to_listen'))
        self._socket: any = None
        self.data: any = None
        self._thread = Thread(target=self.open)
        self.buffer_size: int = int(params.get_value('TcpSocket', 'buffer_size'))  # an estimation from 4096*3000*3+28
        self.header_size: int = int(params.get_value('TcpSocket', 'header_size'))

        self.not_interest_profiles: list = params.get_value('Production', 'profile_not_of_interest').split(',')

        self.image_dict = {
            'profile': None,
            'campaign': None,
            'id': None,
            'mat_image': None,
        }

    def start(self):
        self._thread.start()

    def open(self) -> any:
        """ open the socket and receive data """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(1)

        print("Server listening on {}:{}".format(self._host, self._port))

        i = 1
        while True:
            client_socket, client_address = self._socket.accept()
            self.data = client_socket.recv(self.buffer_size)

            if len(self.data) < self.header_size:
                print(f'data is empty: {len(self.data)} < {self.buffer_size}')
            else:
                print(f'Data received and queued: Image {i}, total size: {len(self.data)}')
                self._buffer.queue([self.data, i])
                i += 1

            # try:
            #     while True:
            #         self.data = client_socket.recv(1024)
            #
            #         if not self.data:
            #             print('no data')
            #             break
            #
            #         self._buffer.queue(self.data)
            #
            # except ConnectionResetError:
            #     print('Connection error')

            client_socket.close()

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            print('Server stopped')


class Process:
    def __init__(self, buff, params):
        self._buffer = buff
        self._thread = Thread(target=self.run)
        self.header_size: int = int(params.get_value('TcpSocket', 'header_size'))
        self._model:any = None
        self._load_model(str(params.get_value('Model', 'model_path')),
                         str(params.get_value('Model', 'device')))
        self.classes: list = params.get_value('Model', 'output_classes').split(',')
        self.inference = YoloV5OnnxSeams()

    def start(self):
        self._thread.start()

    def run(self):
        # TODO: alexandre said do not fuck the thread, but instead, stop it properly otherwise will delete everything

        while True:
            try:
                data = self._buffer.dequeue()
                item = data[0]

                full_msg = b''
                full_msg += item
                body_size = len(item[self.header_size:])

                if len(full_msg) - self.header_size == body_size:
                    header = f'image {data[1]} : ' + item[:self.header_size].decode('utf-8')
                    segments = header.split('_')
                    name = '_'.join(segments[:-2])
                    width = int(segments[-2])
                    height = int(segments[-1])
                    depth = 3

                    # image_received = pickle.loads(full_msg[self.header_size:])
                    image_received = full_msg[self.header_size:]

                    nparr = np.frombuffer(image_received, np.uint8)
                    img_np = nparr.reshape((height, width, depth)).astype('uint8')  # 2-d numpy array\n",

                    t0 = timer()
                    self.inference.process_image(self.classes, self._model, img_np)
                    predictions = self.inference.return_predictions()
                    t1 = timer()
                    print(f'Inference time: %.2f ms' % ((t1-t0) * 1000.0))
                    print(predictions)

                    # image_resized = self.resize_im(img_np, scale_percent=0.25)
                    # cv2.putText(image_resized, name, (12, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (5, 7, 255), 2)
                    # cv2.imshow('window', image_resized)
                    # cv2.waitKey(0)

                else:
                    print(f'problems with length = {len(full_msg)} - {self.header_size} == {body_size}:')

            except IndexError:
                pass

    @staticmethod
    def resize_im(image: np.array, scale_percent: float) -> np.array:
        """ single resize with a factor of any input image """
        width = int(image.shape[1] * scale_percent)
        height = int(image.shape[0] * scale_percent)
        dim = (width, height)
        image_resized = cv2.resize(image, dim)

        return image_resized

    def _load_model(self, weight: str, device: str) -> None:
        """Internally loads ONNX, it is available device cpu or gpu """

        if device == 'cpu':
            self._model = onnxruntime.InferenceSession(weight, providers=["CPUExecutionProvider"])
            return

        if device == 'gpu':
            self._model = onnxruntime.InferenceSession(weight, providers=['CUDAExecutionProvider'])
            return


def main():
    config = XMLConfig('./src/production_config.xml')
    buffer = Buffer()
    server = TCP(buffer, config)
    process = Process(buffer, config)

    server.start()
    process.start()


if __name__ == '__main__':

    main()
    sys.exit(0)

