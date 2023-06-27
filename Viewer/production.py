from collections import deque


class Buffer:
    def __init__(self):
        self.buffer = deque()

    def queue(self, item: any):
        self.buffer.append(item)

    def dequeue(self) -> any:
        if len(self.buffer) > 0:
            return self.buffer.popleft()
        else:
            raise IndexError(f'Buffer is empty: {len(self.buffer)}')

    def is_empty(self) -> bool:
        return len(self.buffer) == 0


def main():
    buffer = Buffer()

    for i in range(0, 35, 7):
        buffer.queue(i)

    while not buffer.is_empty():
        print(buffer.dequeue())
    else:
        print(f'Buffer is empty: {buffer.is_empty()}')


if __name__ == '__main__':
    main()

