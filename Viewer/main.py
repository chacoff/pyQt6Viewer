import abc
import os
import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, \
    QHBoxLayout, QFileDialog, QMainWindow, QSlider, QStatusBar, QMessageBox, QGridLayout, QDialog, QCheckBox, QComboBox
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
from timeit import default_timer as timer
from imageview import ImageView, Annotation
from imageinfo import ImageInfo
from api_engine import YoloV5OnnxSeams
import os
import pandas as pd
from src.matrix import create_matrix
import sqlite3
import onnxruntime
from src.production_config import XMLConfig
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Config
        config = XMLConfig(f'{os.getcwd()}\\src\\production_config.xml')

        self.image_files = []
        self.current_image_name = '0000.bmp'
        self.current_image_index = 0
        self.folder_path = None
        self._model = None
        self.model_path = None
        self.classes_names_raw = config.get_classes_colors_thres()
        self.classes = []
        self.classes_color = []
        self.classes_thre = []
        self.classes_iou = []
        self.counters = [0]  # counter for the instances of defect detection
        self.matrix_dict = {}
        self.matrix_csv = self.unique_file(f'{os.getcwd()}\\matrix\\current_matrix_1.csv')
        self.matrix_img = self.unique_file(f'{os.getcwd()}\\matrix\\confusion_matrix_1.png')

        self.default_folder = str(config.get_value('Viewer', 'default_dataset'))
        self.default_model = str(config.get_value('Viewer', 'default_model'))
        self.annotation_list: list = []

        # DB-sqlite
        self.db_name = self.unique_db()
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS seams_processor
                          (FileName TEXT PRIMARY KEY,
                          Ground_truth TEXT,
                          Predict TEXT,
                          Seams INTEGER, 
                          Beam INTEGER, 
                          Souflure INTEGER, 
                          Hole INTEGER,
                          Water INTEGER,
                          Bin INTEGER,
                          Dataset INTEGER)''')

        # Model name
        self.model_name = QLabel('Model: *.onnx')
        self.model_name.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #606060;}''')

        self.inference_time = QLabel('Inference time: 0.00 ms')
        self.inference_time.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #FF8040;}''')

        self.image_number_title = QLabel('0/00000')
        self.image_number_title.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #606060;}''')
        self.image_name_title = QLabel('*.bmp')
        self.image_name_title.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #606060;}''')

        self.model_prediction_label = QLabel('prediction: ')
        self.model_prediction_label.setStyleSheet('''QLabel {font-size: 20px; font-weight: bold; color: #606060;}''')

        self.ground_truth_label = QLabel('ground truth: ')
        self.ground_truth_label.setStyleSheet('''QLabel {font-size: 20px; font-weight: bold; color: #FF8040;}''')

        # Panel Py-classes
        self.panel_view = ImageView()
        self.panel_info = ImageInfo()
        self.inference = YoloV5OnnxSeams()
        self.setWindowTitle('Seams Processor Viewer - v1.01j - RDEsch')

        # toolbar
        self.toolbar = self.addToolBar('Menu')
        browse_action = QAction("Browse Images", self)  # QIcon('')
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('w')
        browse_action.setToolTip('(w) - Select a folder with images')
        self.annotations_action = QAction("Load Annotations", self)
        self.annotations_action.triggered.connect(self._load_annotations)
        self.annotations_action.setShortcut('l')
        self.annotations_action.setToolTip('(l) - Load CVAT-polygons: Annotations xml')
        self.annotations_action.setDisabled(True)
        self.hide_annotations_action = QAction("Hide Annotations", self)
        self.hide_annotations_action.setShortcut('h')
        self.hide_annotations_action.setToolTip('(h) - Show/Hide CVAT-polygons')
        self.hide_annotations_action.setDisabled(True)
        self.hide_annotations_action.setCheckable(True)
        self.hide_annotations_action.setChecked(True)
        self.hide_annotations_action.toggled.connect(self._toggle_annotations)
        first_im_action = QAction("<< First Image", self)
        first_im_action.triggered.connect(self.show_first_image)
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        previous_action.setToolTip('(a) Goes to the previous image')
        center_image_action = QAction('Reset Zoom', self)
        center_image_action.triggered.connect(self.panel_view.setImageinCenter)
        center_image_action.setShortcut('c')
        center_image_action.setToolTip('(c) Center the image and fullfill the available space')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        next_action.setToolTip('(d) Goes to the next image')
        last_im_action = QAction("Last Image >>", self)
        last_im_action.triggered.connect(self.show_last_image)
        reset_brightness = QAction('Reset Brightness', self)
        reset_brightness.triggered.connect(self.reset_brightness)
        reset_brightness.setShortcut('b')
        reset_brightness.setToolTip('(b) Reset the brightness of the image to its original level')
        self.model_action = QAction(QIcon('includes/model_32.png'), '(m) Load a model', self)  # QAction("Model", self)
        self.model_action.triggered.connect(self.browse_model)
        self.model_action.setShortcut('m')
        self.model_action.setToolTip('(m) - Load a model for classification')
        self.process_action = QAction(QIcon('includes/process_32.png'), '(o) Yes', self)  # QAction("Process", self)
        self.process_action.triggered.connect(self.process_image)
        self.process_action.setShortcut('p')
        self.process_action.setToolTip('(p) - Process an images')
        self.model_is_ok_action = QAction(QIcon('includes/da_32.png'), '(o) Yes', self)
        self.model_is_ok_action.triggered.connect(self.model_is_ok)
        self.model_is_ok_action.setShortcut('o')
        self.model_is_ok_action.setToolTip('(o) - You agree with the classification of the model')
        self.model_is_not_ok_action = QAction(QIcon('includes/net_32.png'), '(n) No', self)
        self.model_is_not_ok_action.triggered.connect(self.model_is_not_ok)
        self.model_is_not_ok_action.setShortcut('n')
        self.model_is_not_ok_action.setToolTip('(n) - You disagree with the classificatino of the model')
        self.delete_image_action = QAction(QIcon('includes/trash_32.png'), '(t) Flag to delete', self)
        self.delete_image_action.triggered.connect(self._toggle_delete_image)
        self.delete_image_action.setShortcut('t')
        self.delete_image_action.setToolTip('(t) - Flag the image for further deleting')
        self.open_matrix_action = QAction(QIcon('includes/matrix_32.png'), 'Build confusion matrix', self)
        self.open_matrix_action.triggered.connect(self.open_matrix_image)
        self.open_matrix_action.setShortcut('x')
        self.open_matrix_action.setToolTip('(x) - Generate a Confusion Matrix with the current classifications')
        self.add_to_dataset_action = QAction(QIcon('includes/server_32.png'), '(s) Flag to add in dataset', self)
        self.add_to_dataset_action.triggered.connect(self._add_to_dataset)
        self.add_to_dataset_action.setShortcut('s')
        self.add_to_dataset_action.setToolTip('(s) - Flag the image as an Image of Interest')
        # Loading buttons
        self.toolbar.addAction(browse_action)
        self.toolbar.addAction(self.annotations_action)
        self.toolbar.addAction(self.hide_annotations_action)
        self.toolbar.widgetForAction(self.hide_annotations_action).setFixedWidth(135)
        self.toolbar.addSeparator()
        # Actions buttons
        self.toolbar.addAction(first_im_action)
        self.toolbar.addAction(previous_action)
        self.toolbar.addAction(center_image_action)
        self.toolbar.addAction(next_action)
        self.toolbar.addAction(last_im_action)
        self.toolbar.addAction(reset_brightness)
        self.toolbar.addSeparator()
        # Statistics buttons
        self.toolbar.addAction(self.model_action)
        self.toolbar.addAction(self.process_action)
        self.toolbar.addAction(self.model_is_ok_action)
        self.toolbar.addAction(self.model_is_not_ok_action)
        self.toolbar.addAction(self.delete_image_action)
        self.toolbar.addAction(self.add_to_dataset_action)
        self.toolbar.addAction(self.open_matrix_action)
        self.toolbar.setStyleSheet('''
            QToolBar {
                border: 1px;
                spacing: 6px;
                margin-top: 6px;
                padding-top: 4px;
            }

            QToolBar QToolButton {
                font-size: 14px;
                background-color: #d3d3d3;
                padding: 6px;
                border: none;
                border-radius: 4px;
                color: #333333;
            }

            QToolBar QToolButton:hover {
                background-color: #c0c0c0;
            }

            QToolBar QToolButton:pressed {
                background-color: #a8a8a8;
            }
        ''')
        self.toolbar.setMovable(False)

        # Brightness slider
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setSingleStep(2)
        self.brightness_slider.valueChanged.connect(self.brightness_slider_handler)  # self.panel_view.set_brightness
        self.brightness_slider.setValue(0)
        self.brightness_slider.setStyleSheet("""
            QSlider {
                height: 18px;
                margin: 1px;
                padding: 1px;
            }

            QSlider::groove:horizontal {
                border: none;
                background-color: #D0D0D0;
                height: 18px;
            }

            QSlider::handle:horizontal {
                background-color: #606060;
                border: none;
                width: 28px;
                height: 28px;
                margin: -3px 0;
                border-radius: 5px;
            }
        """)

        # Images slider
        self.images_slider = QSlider(Qt.Orientation.Horizontal)
        self.images_slider.setMinimum(0)
        self.images_slider.setSingleStep(1)
        self.images_slider.valueChanged.connect(self.image_slider_handler)
        self.images_slider.setValue(0)
        self.images_slider.setStyleSheet("""
                    QSlider {
                        height: 18px;
                        margin: 1px;
                        padding: 1px;
                    }

                    QSlider::groove:horizontal {
                        border: none;
                        background-color: #D0D0D0;
                        height: 18px;
                    }

                    QSlider::handle:horizontal {
                        background-color: #606060;
                        border: none;
                        width: 28px;
                        height: 28px;
                        margin: -3px 0;
                        border-radius: 5px;
                    }
                """)

        # Container with 2 horizontal panels
        layout_2panels = QHBoxLayout()

        # Main vertical container to set a header with model name
        main_vertical_layout = QVBoxLayout()

        header = QGridLayout()

        # header
        header.addWidget(self.model_name, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.inference_time, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        header.addWidget(self.image_number_title, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.image_name_title, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        header.addWidget(self.model_prediction_label, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.ground_truth_label, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        main_vertical_layout.addItem(header)

        # the 2 panels are the horizontal panel with the image viewer and the panel info
        main_vertical_layout.addLayout(layout_2panels)
        main_vertical_layout.setContentsMargins(16, 16, 16, 16)

        # layout to contain image viewer and image tools such as the slider
        image_view_layout = QVBoxLayout()

        image_view_layout.addWidget(self.panel_view, 6)

        bright_block = QHBoxLayout()
        bright_block.setContentsMargins(0, 0, 0, 0)  # Set margins to zero
        bright_block.addWidget(self.brightness_slider, 6)
        self.bright_label = QLabel('0 %')
        self.bright_label.setStyleSheet('''QLabel {font-size: 12px; font-weight: bold; color: #606060;}''')
        self.bright_label.setFixedSize(80, 20)
        self.bright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bright_block.addWidget(self.bright_label, 0)
        b_block = QWidget()
        b_block.setLayout(bright_block)

        image_block = QHBoxLayout()
        image_block.setContentsMargins(0, 0, 0, 0)  # Set margins to zero
        image_block.addWidget(self.images_slider, 6)
        self.imag_label = QLabel('0/0')
        self.imag_label.setStyleSheet('''QLabel {font-size: 12px; font-weight: bold; color: #606060;}''')
        self.imag_label.setFixedSize(80, 20)
        self.imag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_block.addWidget(self.imag_label, 0)
        i_block = QWidget()
        i_block.setLayout(image_block)

        # big add-on
        annotations_checkbox = QComboBox()
        annotations_checkbox.addItems(['Processing mode', 'Segmentation annotations', 'YoloV5 annotations'])
        annotations_checkbox.currentIndexChanged.connect(self.selection_change)
        self.mode = 0
        # big add-on

        image_view_layout.addWidget(b_block, 0)  # self.brightness_slider
        image_view_layout.addWidget(i_block, 0)  # self.images_slider

        _menu = QHBoxLayout()
        _menu.setContentsMargins(0, 0, 0, 0)
        _menu.addWidget(self.toolbar)
        _menu.addWidget(annotations_checkbox)  # big add-on
        w_menu = QWidget()
        w_menu.setLayout(_menu)

        image_view_layout.addWidget(w_menu)
        image_view_layout.setContentsMargins(0, 0, 0, 0)

        w_slider = QWidget()
        w_slider.setLayout(image_view_layout)

        layout_2panels.addWidget(w_slider, 5)
        layout_2panels.addWidget(self.panel_info, 1)

        w = QWidget()
        w.setLayout(main_vertical_layout)
        self.setCentralWidget(w)
        self.statusBar().showMessage('Ready')

    def selection_change(self, state: int) -> None:
        if state == 1:  # state=1 is annotations segmentation
            self.toggle_toolbar(annotations=True)
            self.mode = 1
        elif state == 2:  # state=2 is yolo bbox
            self.toggle_toolbar(annotations=True)
            self.mode = 2
        else:
            self.toggle_toolbar(annotations=False)
            self.mode = 0

    def toggle_toolbar(self, annotations: bool):
        if annotations:  # Qt.CheckState.Checked
            self.annotations_action.setDisabled(False)
            self.hide_annotations_action.setDisabled(False)
            self.model_action.setDisabled(True)
            self.process_action.setDisabled(True)
            self.model_is_ok_action.setDisabled(True)
            self.model_is_not_ok_action.setDisabled(True)
            self.delete_image_action.setDisabled(True)
            self.add_to_dataset_action.setDisabled(True)
            self.open_matrix_action.setDisabled(True)
            if self.classes == [] and self.classes_color == [] and self.classes_thre == [] and self.classes_iou == []:
                self.read_classes_colors_thresholds()
        else:
            self.annotations_action.setDisabled(True)
            self.hide_annotations_action.setDisabled(True)
            self.model_action.setDisabled(False)
            self.process_action.setDisabled(False)
            self.model_is_ok_action.setDisabled(False)
            self.model_is_not_ok_action.setDisabled(False)
            self.delete_image_action.setDisabled(False)
            self.add_to_dataset_action.setDisabled(False)
            self.open_matrix_action.setDisabled(False)

    def _load_annotations(self) -> None:

        if self.folder_path is None:
            return

        def classes_encoder(_label) -> int:

            classes_encoding: dict = {
                'Seams': 0,
                'Beam': 1,
                'Souflure': 2,
                'Hole': 3,
                'Water': 4
            }
            return classes_encoding[_label]

        if self.mode == 1:
            root = ET.parse(f'{self.folder_path}\\annotations.xml').getroot()
            meta = root.findall("image")

            self.annotation_list = []
            for _image in meta:
                _name: str = str(_image.attrib["name"])

                if _name == self.current_image_name:
                    object_metas = _image.findall("polygon")

                    for bbox in object_metas:
                        label = bbox.attrib['label']
                        points = bbox.attrib['points'].split(';')
                        annotation = Annotation(points, label, self.classes_color[classes_encoder(label)])
                        self.annotation_list.append(annotation)

            self.hide_annotations_action.setChecked(True)
            self.panel_view.draw_annotations(self.annotation_list)

        elif self.mode == 2:
            _yolo_annotation = os.path.splitext(self.current_image_name)[0]+'.txt'
            self.panel_view.draw_yolo_annotation(self.folder_path,
                                                 self.current_image_name,
                                                 _yolo_annotation,
                                                 self.classes_color)
        else:
            pass

    def _toggle_annotations(self, checked: bool) -> None:
        if not self.annotation_list:
            self.error_box('No annotations', 'Load annotations before attempting to Show/Hide them')
            return

        self.hide_annotations_action.setText('Hide Annotations' if checked else 'Show Annotations')
        self.panel_view.show_hide_items(checked)

    def model_is_ok(self):
        """
            X-axis reference to update the vector self.counters_classification
            Seams Ground 0
            NoSeams Ground 1
            Seams Prediction 2
            NoSeams Prediction 3
        """
        ground_truth = self.user_classification('Ok')
        self.update_db('Ground_truth', ground_truth)
        self.write_in_csv(ground_truth)
        self.panel_info.update_statistics(self.classes, self.classes_color, self.db_name)
        self.ground_truth_label.setText(f'ground truth: {ground_truth}')

    def model_is_not_ok(self):
        """
            X-axis reference to update the vector self.counters_classification
            Seams Ground 0
            NoSeams Ground 1
            Seams Prediction 2
            NoSeams Prediction 3
        """
        ground_truth = self.user_classification('NotOk')
        self.update_db('Ground_truth', ground_truth)
        self.write_in_csv(ground_truth)
        self.panel_info.update_statistics(self.classes, self.classes_color, self.db_name)
        self.ground_truth_label.setText(f'ground truth: {ground_truth}')

    def user_classification(self, user):
        """ handles most of the interactions from the user while classifying the ground truth """

        if self.current_image_name not in self.matrix_dict:
            self.error_box('Image not processed', 'You need to launch the process of this image before !')
            return

        ground_truth = self.ground_t_calculator(self.matrix_dict[self.current_image_name], user)

        return ground_truth

    def write_in_csv(self, ground_t):

        if self.current_image_name not in self.matrix_dict:
            return

        new_file = not os.path.exists(self.matrix_csv)

        if new_file:
            df = pd.DataFrame(columns=['FileName', 'Ground_truth', 'Predict'])
        else:
            df = pd.read_csv(self.matrix_csv)

        if self.current_image_name in df['FileName'].to_list():
            df = df.drop(df[df['FileName'] == self.current_image_name].index)

        data = [self.current_image_name, ground_t, self.matrix_dict[self.current_image_name]]
        new_line = pd.DataFrame([data], columns=['FileName', 'Ground_truth', 'Predict'])
        df = pd.concat([df, new_line], ignore_index=True)
        df.to_csv(self.matrix_csv, index=False)

    def open_matrix_image(self):

        if create_matrix(self.matrix_img, self.matrix_csv):

            # Charger l'image en utilisant QImage
            image = QImage(self.matrix_img)

            # Convertir l'image en QPixmap
            pixmap = QPixmap.fromImage(image)

            # Créer une fenêtre de dialogue
            dialog = QDialog(self)
            dialog.setWindowTitle("Confusion Matrix")
            dialog.setModal(True)

            # Créer un QLabel pour afficher l'image dans la fenêtre de dialogue
            label = QLabel(dialog)
            label.setPixmap(pixmap.scaled(900, 898, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            # Créer un layout et un widget pour contenir le QLabel
            layout = QGridLayout(dialog)
            widget = QWidget(dialog)
            layout.addWidget(label)
            widget.setLayout(layout)

            dialog.setLayout(layout)
            dialog.show()
        else:
            self.error_box('Oopsie!', 'Error while creating confusion matrix: Not enough data to analyze')

    def _toggle_delete_image(self) -> None:
        """ flag to toggle the delete image status """
        value = self._read_field_value('Bin')

        if value is None:  # the field doesn't exist yet
            return

        self.update_db('Bin', not value)

    def _add_to_dataset(self) -> None:
        """ flag the image to be add in the dataset as an important image """

        value = self._read_field_value('Dataset')

        if value is None:
            return

        self.update_db('Dataset', not value)

    def _read_field_value(self, field: any) -> any:
        """ read the field value in the DB"""

        sq0 = f'SELECT {field} FROM seams_processor WHERE FileName = ?'
        sq1 = sq0

        self.cursor.execute(sq1, (self.current_image_name, ))

        result = self.cursor.fetchone()

        return result[0] if result is not None else None

    def set_status_bar(self):
        """ set the status bar with some information about the current image
        sets title in the header about the current image and predictions
        sets the global current_image_name
        """

        self.current_image_name = QFileInfo(self.filename()).fileName()
        self.image_name_title.setText(self.current_image_name)
        self.image_number_title.setText(f'{self.current_image_index + 1} of {len(self.image_files)} ')
        self.model_prediction_label.setText('prediction: ')
        self.ground_truth_label.setText('ground truth: ')

        message = f'{self.current_image_index + 1} of {len(self.image_files)} - ' \
                  f'{self.current_image_name} - ' \
                  f'{self.panel_view.channel}x{self.panel_view.height}x{self.panel_view.width} in ' \
                  f'{self.folder_path}'

        self.imag_label.setText(f'{self.current_image_index + 1}/{len(self.image_files)}')
        self.statusBar().showMessage(message)

    def browse_folder(self):
        default = self.default_folder

        self.folder_path = QFileDialog.getExistingDirectory(self, "Choose Folder", default)

        if not self.folder_path:
            return

        q_dir = QDir(self.folder_path)
        q_dir.setNameFilters(['*.bmp', '*.png', '*.jpg'])
        q_dir.setSorting(QDir.SortFlag.Name)

        self.image_files = [q_dir.absoluteFilePath(file_name) for file_name in q_dir.entryList()]

        if self.image_files:
            self.current_image_index = 0
            self.panel_view.display_image(self.filename())
            self.images_slider.setValue(0)
            self.images_slider.setMaximum(len(self.image_files)-1)
            self.bright_label.setText(f'0 %')
            self.brightness_slider.setValue(0)
            self.set_status_bar()

    def browse_model(self):
        default = self.default_model
        cancel_proof = self.model_path

        _model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', default, 'Onnx files (*.onnx)')
        self.model_path = _model_path[0]
        model_name = QFileInfo(_model_path[0]).fileName()

        if self.model_path == '':
            self.model_path = cancel_proof
            return

        self.update_model_name(f'Model: {model_name}')
        if self.classes == [] and self.classes_color == [] and self.classes_thre == [] and self.classes_iou == []:
            self.read_classes_colors_thresholds()
        # load model in memory immediately
        self._load_model(self.model_path, 'cpu')

    def _load_model(self, weight: str, device: str) -> None:
        """Internally loads ONNX, it is available device cpu or gpu """

        if device == 'cpu':
            self._model = onnxruntime.InferenceSession(weight, providers=["CPUExecutionProvider"])
            return

        if device == 'gpu':
            self._model = onnxruntime.InferenceSession(weight, providers=['CUDAExecutionProvider'])
            return

    def read_classes_colors_thresholds(self) -> None:

        self.panel_info.update_classes_names_view(self.classes_names_raw)

        for row, (name, color, thre, iou) in enumerate(self.classes_names_raw):
            self.classes.append(name)
            self.classes_color.append(color)
            self.classes_thre.append(thre)
            self.classes_iou.append(iou)

    def get_all_confidences(self) -> list:
        """ column (2) from panel info corresponde to the confidences """
        _all_confs = self.panel_info.get_thres_item(2)
        _all_confs = [x / 100 for x in _all_confs]

        return _all_confs

    def get_all_ious(self) -> list:
        """ column (3) from panel info corresponde to the IOUs """
        _all_ious = self.panel_info.get_thres_item(3)
        _all_ious = [x / 100 for x in _all_ious]

        return _all_ious

    def process_image(self):
        """ process the image will trigger the statistic counters and will start filling
        the dictionary self.matrix_dict storing all the images already processed
        """

        _confs = self.get_all_confidences()
        _ious = self.get_all_ious()

        if not self.folder_path:
            self.error_box('Folder Path', 'Please load a folder with images in BMP or PNG')
            return

        if not self.model_path:
            self.error_box('Model Path', 'Please load an ONNX model before to process')
            return

        self.insert_into_db()  # insert into DB the existing image

        frame = self.panel_view.image_cvmat  # gets the current image on the scene

        # Actual processing >> sending self._model loaded in the memory instead of the string self.model_path
        t0 = timer()
        self.inference.process_image(self.classes, self._model, frame, conf=_confs, iou=_ious)
        predictions = self.inference.return_predictions()
        t1 = timer()
        self.update_inference_time(t1-t0)

        self.panel_view.draw_boxes_and_labels(predictions, self.classes_color)
        self.statistics_counter(predictions)
        self.panel_info.update_statistics(self.classes, self.classes_color, self.db_name)

    def insert_into_db(self):
        """ insert into the db every image process, the rest of the fields are later on updated """

        self.cursor.execute("SELECT COUNT(*) FROM seams_processor WHERE FileName = ?", (self.current_image_name,))
        result = self.cursor.fetchone()[0]

        if result != 0:
            return

        sql = '''
            INSERT OR REPLACE INTO seams_processor (
                    FileName, 
                    Ground_truth, 
                    Predict, 
                    Seams, 
                    Beam, 
                    Souflure, 
                    Hole,
                    Water,
                    Bin,
                    Dataset
            ) VALUES (
                    ?, 
                    ?, 
                    ?, 
                    ?, 
                    ?, 
                    ?, 
                    ?, 
                    ?,
                    ?,
                    ?
            )'''

        self.cursor.execute(sql, (self.current_image_name,
                                  'None',
                                  'None',
                                  0,
                                  0,
                                  0,
                                  0,
                                  0,
                                  0,
                                  0))
        self.conn.commit()

    def update_db(self, field: any, value: any):
        """ update rows according the field of interest and the current_image_name """

        sq0 = f'UPDATE seams_processor SET {field} = ? WHERE FileName = ?'
        sql = sq0

        self.cursor.execute(sql, (value, self.current_image_name))
        self.conn.commit()

    def statistics_counter(self, predictions):
        """
        statistic counters for object instances and image classification

        the graph for ground truth matrix is pre defined like this:
            Seams Ground 0
            NoSeams Ground 1
            Seams Prediction 2
            NoSeams Prediction 3

        X-axis reference to update the vector self.counters_classification
        """

        self.counters = [0] * len(self.classes)  # updates counter's length according the number of classes
        for prediction in predictions:
            class_id = prediction.class_id
            self.counters[class_id] += 1
            self.update_db(prediction.class_name, self.counters[class_id])
    
        # Final classification of the model, Seams if there is at least one seams detected
        classification = [c.class_name for c in predictions if c.class_name == 'Seams']

        if len(classification) == 0:  # it means no seams where detected in the beam
            # here's the first time the image is included in self.matrix_dict
            self.matrix_dict[self.current_image_name] = "NoSeams"
            self.model_prediction_label.setText(f'prediction: NoSeams')
            self.update_db('Predict', 'NoSeams')
        else:
            self.matrix_dict[self.current_image_name] = "Seams"
            self.model_prediction_label.setText(f'prediction: Seams')
            self.update_db('Predict', 'Seams')

    def brightness_slider_handler(self, value):
        self.bright_label.setText(f'{value} %')
        self.panel_view.set_brightness(value)

    def image_slider_handler(self, value):
        """ move fast between images inside of a folder """

        if not self.folder_path:
            self.error_box('Folder Path', 'Please load a folder with images in BMP or PNG')
            return

        if value <= len(self.image_files)-1:
            self.current_image_index = value
            self.panel_view.display_image(self.filename())
            self.update_inference_time(0.0)
            self.set_status_bar()
            self.annotation_list = []

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.panel_view.display_image(self.filename())
            self.update_inference_time(0.0)
            self.images_slider.setValue(self.current_image_index)
            self.set_status_bar()
            self.annotation_list = []

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.panel_view.display_image(self.filename())
            self.update_inference_time(0.0)
            self.images_slider.setValue(self.current_image_index)
            self.set_status_bar()
            self.annotation_list = []

    def show_first_image(self):
        """ show first image in the folder_path """
        if self.folder_path is None:
            return

        self.current_image_index = 0
        self.panel_view.display_image(self.filename())
        self.update_inference_time(0.0)
        self.images_slider.setValue(self.current_image_index)
        self.set_status_bar()
        self.annotation_list = []

    def show_last_image(self):
        """ show last image in the folder_path"""
        if self.folder_path is None:
            return

        self.current_image_index = len(self.image_files) - 1
        self.panel_view.display_image(self.filename())
        self.update_inference_time(0.0)
        self.images_slider.setValue(self.current_image_index)
        self.set_status_bar()
        self.annotation_list = []

    def reset_brightness(self):
        """ reset slider and brightness """
        if self.folder_path is None:
            return

        self.bright_label.setText('0/0')
        self.brightness_slider.setValue(0)
        self.panel_view.set_brightness(0)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)

    def update_inference_time(self, t):
        label = 'Inference time: %.2f ms' % (t * 1000.0)
        self.inference_time.setText(label)

    def filename(self):
        return self.image_files[self.current_image_index]

    def error_box(self, title, message):
        dlg = QMessageBox(self)
        icon = QIcon('includes/cat.png')
        dlg.setIconPixmap(icon.pixmap(64, 64))
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.exec()

    @staticmethod
    def ground_t_calculator(a: str, b: str) -> str:
        """ based on the model output classification and the user Ok and NotOk,
        returns the ground truth. The target is to avoid confusing the user to write Seams/NoSeams
        and instead, just accept or reject the output classification

            a = prediction.class_id
            b = ground_truth class_id
            Model Seams, Ok> Seams <> 0 0 = 0
            Model Seams, NotOk > NoSeams <> 0 1 = 1
            Model NoSeams, Ok> NoSeams <> 1 0 = 1
            Model NoSeams, NotOK> Seams <> 1 1 = 0
        """

        if a == 'Seams' and b == 'Ok':
            return 'Seams'
        elif a == 'Seams' and b == 'NotOk':
            return 'NoSeams'
        elif a == 'NoSeams' and b == 'Ok':
            return 'NoSeams'
        elif a == 'NoSeams' and b == 'NotOk':

            return 'Seams'
        else:
            raise ValueError("Invalid input values")

    @staticmethod
    def unique_file(path):
        root, ext = os.path.splitext(path)
        root = root.rsplit("_", 1)[0]
        k = 1

        while os.path.exists(path):
            path = f'{root}_{str(k)}{ext}'
            k += 1

        return path

    @staticmethod
    def unique_db() -> str:
        """ one database per session """
        # TODO @pierrick, ideally will be to have 1 database only, no csv file, only one database and remember each
        # TODO session to generate confusion matrix per session and of tha accumulate
        folder = './matrix'  # Current directory
        extension = '.db'
        existing_databases = [file for file in os.listdir(folder) if file.endswith(extension)]
        next_number = len(existing_databases) + 1

        return f'{folder}/seams_processor_{next_number}{extension}'


if __name__ == '__main__':
    app = QApplication(sys.argv)

    image_window = MainWindow()
    image_window.setWindowIcon(QIcon('./includes/object.ico'))
    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
