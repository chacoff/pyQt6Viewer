import concurrent.futures
import queue
import time


class QueueImages:
    def __init__(self):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

    def process_queue_item(self, item: int = 0):
        """ method to dispatch the new incoming images """
        processed_item = self.__process_item(item)
        self.output_queue.put(processed_item)

    @staticmethod
    def __process_item(item) -> float:
        """ private method for processing """
        processed_item = item * 5
        time.sleep(0.3)

        return processed_item


def main():
    q = QueueImages()

    q.input_queue.put(5)
    q.input_queue.put(6)
    q.input_queue.put(7)
    q.input_queue.put(8)
    q.input_queue.put(9)
    q.input_queue.put(10)
    q.input_queue.put(11)
    q.input_queue.put(12)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while not q.input_queue.empty():
            item = q.input_queue.get()
            executor.submit(q.process_queue_item, item)

    executor.shutdown()

    while not q.output_queue.empty():
        processed_item = q.output_queue.get()
        print(f'output: {processed_item}')

    print('no more')


if __name__ == '__main__':
    main()
