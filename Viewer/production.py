from collections import deque
from threading import Lock, Thread
import socket
import sys


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
    def __init__(self, buff):
        self._buffer = buff
        self._host: str = '127.0.0.1'
        self._port: int = 1302
        self._socket: any = None
        self.data: any = None
        self._thread = Thread(target=self.open)

    def start(self):
        self._thread.start()

    def open(self) -> any:
        """ open the socket and receive data """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(1)

        print("Server listening on {}:{}".format(self._host, self._port))

        while True:
            client_socket, client_address = self._socket.accept()
            self.data = client_socket.recv(4096)

            if not self.data:
                print('data is empty')
            else:
                self._buffer.queue(self.data)

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

    def start(self):
        self._thread.start()

    def run(self):
        # TODO: alexandre said do not fuck the thread, but instead, stop it properly otherwise will delete everything
        while True:
            try:
                item = self._buffer.dequeue()
                print(f'item to process: {item.decode()}')

                # processing ....
                item = item.decode()
                print(f'item after process: {item}')

            except IndexError:
                pass


def main():
    buffer = Buffer()
    server = TCP(buffer)
    process = Process(buffer)

    server.start()
    process.start()


if __name__ == '__main__':

    main()
    sys.exit(0)

