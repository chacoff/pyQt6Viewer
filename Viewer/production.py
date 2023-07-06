from collections import deque
from threading import Lock, Thread
import socket
import sys
import pickle
import cv2
import numpy as np


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
    def __init__(self, buff):
        self._buffer = buff
        self._host: str = '127.0.0.1'
        self._port: int = 1302
        self._socket: any = None
        self.data: any = None
        self._thread = Thread(target=self.open)
        self.buffer_size = 36864200
        self.header_size = 38

    def start(self):
        self._thread.start()

    def open(self) -> any:
        """ open the socket and receive data """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(1)

        print("Server listening on {}:{}".format(self._host, self._port))

        i=1
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
    def __init__(self, buff):
        self._buffer = buff
        self._thread = Thread(target=self.run)
        self.header_size = 38

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

                    image_resized = self.resize_im(img_np, scale_percent=0.25)
                    cv2.putText(image_resized, name, (12, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (5, 7, 255), 2)

                    cv2.imshow('window', image_resized)
                    cv2.waitKey(0)

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


def main():
    buffer = Buffer()
    server = TCP(buffer)
    process = Process(buffer)

    server.start()
    process.start()


if __name__ == '__main__':

    main()
    sys.exit(0)

