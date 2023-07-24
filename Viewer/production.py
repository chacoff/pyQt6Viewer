from collections import deque
from threading import Lock, Thread
import socket
import sys
from typing import Dict, Union
import cv2
import numpy as np
from YoloV5_Onnx_detect import YoloV5OnnxSeams
import onnxruntime
from timeit import default_timer as timer
from src.production_config import XMLConfig
import pyodbc
from datetime import datetime
import copy
import os
import ast
import time


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
            return self._buffer.popleft()

    def is_empty(self) -> bool:
        with self._mutex:
            return len(self._buffer) == 0


class TCP:
    """ server """
    def __init__(self, buff, params):
        self._buffer = buff
        self._host: str = str(params.get_value('TcpSocket', 'ip_to_listen'))
        self._port: int = int(params.get_value('TcpSocket', 'port_to_listen'))
        self._socket: any = None
        self.data: bytes = b''
        self._thread = None  # Thread(target=self.open)
        self.is_running = False
        self.buffer_size: int = int(params.get_value('TcpSocket', 'buffer_size'))  # an estimation from 4096*3000*3+40
        self.header_size: int = int(params.get_value('TcpSocket', 'header_size'))

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._thread = Thread(target=self.open)
            self._thread.start()

    def stop(self):
        self.is_running = False

    def open(self) -> any:
        """ open the socket and receive data """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(1)
        print("Server listening on {}:{}".format(self._host, self._port))

        while self.is_running:
            try:
                client_socket, client_address = self._socket.accept()
            except OSError:
                pass
            self.on_connect(client_address)

            try:
                while self.is_running:
                    try:
                        self.data = self.data + client_socket.recv(self.buffer_size-len(self.data))
                    except OSError:
                        self.on_disconnect()

                    if not self.data:
                        break

                    if len(self.data) != self.buffer_size:
                        print(f'data is not completed: {len(self.data)} < {self.buffer_size}')
                        continue

                    # print(f'Data received and queued - Message total size: {len(self.data)}')
                    self._buffer.queue(copy.deepcopy(self.data))
                    self.data = b''

            except ConnectionResetError:
                client_socket.close()
                self.on_close()

    def on_connect(self, peer) -> None:
        self.is_running = True
        print(f"MSC connected: {peer}")

    def on_disconnect(self) -> None:
        # self.is_running = False
        print("MSC disconnected")

    def on_close(self) -> None:
        if self._socket is not None:
            self._socket.close()
        self.on_disconnect()
        self.start()


class Process:
    def __init__(self, buff, buff_images, params):
        self._buffer = buff
        self._buffer_images = buff_images
        self._thread = Thread(target=self.run)
        self.header_size: int = int(params.get_value('TcpSocket', 'header_size'))
        self._model: any = None
        self._load_model(str(params.get_value('Model', 'model_path')),
                         str(params.get_value('Model', 'device')))
        self.classes: list = params.get_value('Model', 'output_classes').split(',')
        self.classes_to_save: list = params.get_value('Model', 'classes_to_save').split(',')
        self.interest_profiles: list = params.get_value('Production', 'profile_of_interest').split(',')
        self.not_interest_profiles: list = params.get_value('Production', 'profile_not_of_interest').split(',')
        self.inference = YoloV5OnnxSeams()
        self.base_saving_folder: str = str(params.get_value('Production', 'saving_folder'))
        self.save_all_images = ast.literal_eval(params.get_value('Production', 'save_all_images'))

        # current info
        self.current_image_info: Dict[str, Union[str, str, str, int, str, int, int, int]] = {
            'name': None,
            'profile': None,
            'campaign': None,
            'beam_id': None,
            'position': None,
            'n_images': 0,  # number of images of one beam defined as beam_id or ID_TM_PART
            'Seams': 0,
            'Hole': 0,
        }
        self.last_beam_id: int = 915599

        # DB
        self.conn_string = 'DRIVER={SQL Server};' \
                           'SERVER=AZR-SQL-MIAUT;' \
                           'DATABASE=SEAMS_DETECTIONS;' \
                           'UID=SEAMS-DETECT_Publisher;' \
                           'PWD=AMseams2023Q3'

        self.conn = pyodbc.connect(self.conn_string)

        self.cursor = self.conn.cursor()

    def start(self):
        self._thread.start()

    def run(self):
        while True:
            try:
                data = self._buffer.dequeue()

                mat_image, mat_org = self.decode_payload(data, self.header_size, debug=False)

                if str(self.current_image_info['profile']) in self.not_interest_profiles:
                    print('%s: Profile of no interest' % self.current_image_info['profile'])
                else:
                    t0 = timer()
                    self.inference.process_image(self.classes, self._model, mat_image, conf=0.22, iou=0.15)
                    predictions = self.inference.return_predictions()
                    t1 = timer()

                    classification = self.classifier(predictions)
                    process_msg = f'{classification} - inference time: %.2f ms' % ((t1-t0) * 1000.0)

                    if self.current_image_info["profile"] != '00000':
                        self.db_job(process_msg)  # skip database inserting if there is no MES information

                    payload = [mat_org,
                               classification,
                               self.current_image_info["profile"],
                               self.current_image_info["campaign"],
                               self.current_image_info["beam_id"],
                               self.current_image_info["n_images"],
                               False]  # flag to save in low quality

                    if self.save_all_images:
                        payload[6] = True  # flag to save in low quality
                        self.classes_to_save.append('Beam')  # it also saves now Beam only images

                    if self.current_image_info['profile'] in self.interest_profiles and classification in self.classes_to_save:
                        self._buffer_images.queue(payload)

            except IndexError:
                # no data to process
                time.sleep(0.100)

    def db_insert(self) -> None:
        """ insert the information of a new beam as soon as we scan the first image """

        _id = self.db_beam_info_max_id()
        _now = datetime.now()
        _seams: int = self.current_image_info.get("Seams")
        _images: int = self.current_image_info.get("n_images")
        _beam_id: int = self.current_image_info.get("beam_id")
        _profile: str = self.current_image_info.get("profile")
        _campaign: int = self.current_image_info.get("campaign")

        insert_query = f"INSERT INTO dbo.BEAM_INFO (" \
                       f"seamsCount, " \
                       f"imageCount, " \
                       f"seamsRate, " \
                       f"dateTime, " \
                       f"ID_TM_PART, " \
                       f"GRP_MONT, " \
                       f"NUM_MONT, " \
                       f"LONG_L1DD, " \
                       f"FL_MSG_TRAITE, " \
                       f"NBRE_DEFT, " \
                       f"ID) " \
                       f"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        _rate: float = round(_seams / _images, 3)
        self.cursor.execute(insert_query, (_seams, _images, _rate, _now, _beam_id, _profile, _campaign, 0, 0, 0, _id))
        self.conn.commit()

        # self.cursor.close()
        # self.conn.close()

    def db_update(self) -> None:
        """ DB is updated once the next Beam is coming, i.e., once we finished to scanned the previous beam"""
        _id_tm_part: int = self.last_beam_id
        _grp_mont: str = self.current_image_info.get('profile')
        _num_mont: int = self.current_image_info.get('campaign')
        _seams_count: int = self.current_image_info.get('Seams')
        _image_count: int = self.current_image_info.get('n_images')
        _seams_rate: float = round(_seams_count / _image_count, 3)

        sql_query = f"""UPDATE [SEAMS_DETECTIONS].[dbo].[BEAM_INFO] SET seamsCount = ?, imageCount = ?, seamsRate = ? 
        WHERE ID_TM_PART = ? AND GRP_MONT = ? AND NUM_MONT = ?"""

        self.cursor.execute(sql_query, (_seams_count, _image_count, _seams_rate, _id_tm_part, _grp_mont, _num_mont))
        self.conn.commit()

    def db_beam_info_max_id(self) -> int:
        query = "SELECT max(ID) as max from [SEAMS_DETECTIONS].[dbo].[BEAM_INFO]"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        max_value = (result.max + 1)

        # self.cursor.close()
        # self.conn.close()

        return max_value

    def db_consult(self) -> int:
        """ return the last ID_TM_PART on the database"""
        query = """
                    SELECT TOP 1
                    [ID_TM_PART]
                    FROM [SEAMS_DETECTIONS].[dbo].[BEAM_INFO]
                    ORDER BY [dateTime] DESC
                    """

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        beam_id: int = 115599 # default init value
        for row in rows:
            beam_id = row[0]  # ID_TM_PART

        # self.cursor.close()
        # self.conn.close()

        return beam_id

    def db_job(self, msg: str) -> None:

        if self.current_image_info['beam_id'] == self.last_beam_id:
            print(f'Update ID_TM_PART: {self.current_image_info.get("beam_id")} -- '
                  f'{msg} - '
                  f'n_images: {self.current_image_info.get("n_images")} - '
                  f'seams: {self.current_image_info.get("Seams")} - '
                  f'hole: {self.current_image_info.get("Hole")}')
            # self.db_update()
        else:
            self.last_beam_id = self.current_image_info['beam_id']
            print(f'>> Insert ID_TM_PART: {self.current_image_info.get("beam_id")} -- '
                  f'{msg} - '
                  f'n_images: {self.current_image_info.get("n_images")} - '
                  f'seams: {self.current_image_info.get("Seams")} - '
                  f'hole: {self.current_image_info.get("Hole")}')
            self.db_insert()

    def classifier(self, preds) -> str:
        """ classify the image to one single class and update counters """

        if self.current_image_info['beam_id'] != self.last_beam_id:
            if self.current_image_info['n_images'] != 0:
                self.db_update()  # once before resetting the counters and if n_images = 0 it means is the first beam
            self.current_image_info['n_images'] = 0
            self.current_image_info['Seams'] = 0
            self.current_image_info['Hole'] = 0

        classif_hole = [c.class_name for c in preds if c.class_name == 'Hole']
        classif_seams = [c.class_name for c in preds if c.class_name == 'Seams']

        if classif_hole:
            self.current_image_info['Hole'] += 1
            self.current_image_info['n_images'] += 1
            return 'Hole'

        if classif_seams:
            self.current_image_info['Seams'] += 1
            self.current_image_info['n_images'] += 1
            return 'Seams'

        self.current_image_info['n_images'] += 1
        return 'Beam'

    def decode_payload(self, item: bytes, header_size: int, debug: bool = False) -> any:
        """
        Decode the incoming message from bytes
            :param item: the payload in bytes
            :param header_size: typically is 38 and looks like this: ZH026_3260_154200_TX39406066_4096_3000
            :param debug: bool to write or not an image
            :return: a numpy array 3d (Mat image) for inference and the original image in 1d
        """
        full_msg = b''
        full_msg += item
        body_size = len(item[header_size:])  # for the Seams Camera Baumer HXG20 is 4096x300x3 = 36864000

        if len(full_msg) - header_size == body_size:

            header = item[:header_size].decode('utf-8')
            segments = header.split('_')
            name = '_'.join(segments[:-2])  # profile_campaign_beamID_position
            profile = str(segments[0])  # GRP_MONT
            campaign = str(segments[1])  # NOM_MONT
            beam_id = str(segments[2])  # ID_TM_PART
            position = str(segments[3])
            width = int(segments[4])
            height = int(segments[5])
            depth = int(segments[6])

            # image_received = pickle.loads(full_msg[self.header_size:])
            image_received = full_msg[header_size:]
            nparr = np.frombuffer(image_received, np.uint8)
            img_np = nparr.reshape((height, width, depth)).astype('uint8')  # 2-d numpy array\n",

            img_np_3d = cv2.merge((img_np, img_np, img_np)) if depth == 1 else img_np

            if debug:
                cv2.putText(img_np_3d, name, (12, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (5, 7, 255), 2)
                cv2.imwrite(f'{name}.bmp', img_np_3d)

            self.current_image_info['name'] = name
            self.current_image_info['profile'] = profile
            self.current_image_info['campaign'] = campaign
            self.current_image_info['beam_id'] = beam_id
            self.current_image_info['position'] = position

            return img_np_3d, img_np
        else:
            print(f'problems with length = {len(full_msg)} - {header_size} == {body_size}:')
            return

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


class SavingImages:
    def __init__(self, buff_img, params):
        self._buffer_image = buff_img
        self._thread = Thread(target=self.run)
        self.base_saving_folder: str = str(params.get_value('Production', 'saving_folder'))

    def start(self):
        self._thread.start()

    def run(self):
        while True:
            try:
                data = self._buffer_image.dequeue()
                mat, classe, profile, campaign, beam_id, n_images, image_quality = data

                if profile == '00000':  # it means no MES information
                    _time = datetime.now()
                    filename = f'{profile}_' \
                               f'{campaign}_' \
                               f'{beam_id}_' \
                               f'{_time.strftime("%Y_%m_%d_%H%M%S")}.bmp'
                else:
                    filename = f'{profile}_' \
                                f'{campaign}_' \
                                f'{beam_id}_' \
                                f'WEB00{n_images}.bmp'

                full_path = os.path.join(self.base_saving_folder,
                                         profile,
                                         campaign,
                                         classe)

                if not os.path.exists(full_path):
                    os.makedirs(full_path)

                full_name = os.path.join(full_path, filename)
                if not image_quality:
                    cv2.imwrite(full_name, mat)
                else:
                    cv2.imwrite(full_name, mat, [cv2.IMWRITE_JPEG_QUALITY, 20])
                time.sleep(0.010)
            except IndexError:
                # nothing to save
                time.sleep(0.100)


def main():
    config = XMLConfig('./src/production_config.xml')

    buffer = Buffer()
    buffer_images = Buffer()

    server = TCP(buffer, config)
    process = Process(buffer, buffer_images, config)
    saving = SavingImages(buffer_images, config)

    server.start()
    process.start()
    saving.start()


if __name__ == '__main__':

    main()
    sys.exit(0)

