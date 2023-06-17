import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy
from imageview import ImageView
from imageinfo import ImageInfo
from src.yolov5_seams import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = 0
        self.folder_path = None
        self.model_path = None
        self.net = None
        self.classes = None

        # Model name
        self.model_name = QLabel('Model: *.onnx')
        self.model_name.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #606060;}''')

        self.inference_time = QLabel('Inference time: 0.00 ms')
        self.inference_time.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #FF8040;}''')

        # Panel Py-classes
        self.panel_view = ImageView()
        self.panel_info = ImageInfo()
        self.inference = YoloV5sSeams()
        self.setWindowTitle('Seams Viewer')

        # toolbar
        toolbar = self.addToolBar('Menu')
        browse_action = QAction("Browse", self)  # QIcon('')
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('o')
        process_action = QAction("Process", self)
        process_action.triggered.connect(self.process_image)
        process_action.setShortcut('p')
        model_action = QAction("Model", self)
        model_action.triggered.connect(self.browse_model)
        model_action.setShortcut('m')
        firstIm_action = QAction("<< First Image", self)
        firstIm_action.triggered.connect(self.show_first_image)
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        center_image_action = QAction('Reset Zoom', self)
        center_image_action.triggered.connect(self.panel_view.setImageinCenter)
        center_image_action.setShortcut('c')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        lastIm_action = QAction("Last Image >>", self)
        lastIm_action.triggered.connect(self.show_last_image)
        reset_brightness = QAction('Reset Brightness', self)
        reset_brightness.triggered.connect(self.reset_brightness)
        reset_brightness.setShortcut('b')
        toolbar.addAction(browse_action)
        toolbar.addAction(model_action)
        toolbar.addAction(process_action)
        toolbar.addSeparator()
        toolbar.addAction(firstIm_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(center_image_action)
        toolbar.addAction(next_action)
        toolbar.addAction(lastIm_action)
        toolbar.addAction(reset_brightness)
        toolbar.setStyleSheet('''
            QToolBar {
                background-color: #f2f2f2;
                border: 1px;
                spacing: 6px;
                margin-top: 6px;
                padding-top: 4px;
            }

            QToolBar QToolButton {
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
        toolbar.setMovable(False)

        # Brightness slider
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setSingleStep(2)
        self.brightness_slider.valueChanged.connect(self.panel_view.set_brightness)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setStyleSheet("""
            QSlider {
                background-color: #D0D0D0;
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
        main_vertical_layout.addWidget(self.model_name)
        main_vertical_layout.addWidget(self.inference_time)
        main_vertical_layout.addLayout(layout_2panels)
        main_vertical_layout.setContentsMargins(16, 16, 16, 16)

        # layout to contain image viewer and image tools such as the slider
        image_view_layout = QVBoxLayout()

        image_view_layout.addWidget(self.panel_view, 6)
        image_view_layout.addWidget(self.brightness_slider, 1)
        image_view_layout.addWidget(toolbar, 1)
        image_view_layout.setContentsMargins(0, 0, 0, 0)

        w_slider = QWidget()
        w_slider.setLayout(image_view_layout)

        layout_2panels.addWidget(w_slider, 5)
        layout_2panels.addWidget(self.panel_info, 1)

        w = QWidget()
        w.setLayout(main_vertical_layout)
        self.setCentralWidget(w)
        self.statusBar().showMessage('Ready')

    def set_status_bar(self):
        message = f'{self.current_image_index + 1} of {len(self.image_files)} - ' \
                  f'{QFileInfo(self.filename()).fileName()} - ' \
                  f'{self.panel_view.channel}x{self.panel_view.height}x{self.panel_view.width} in ' \
                  f'{self.folder_path}'
        self.statusBar().showMessage(message)

    def browse_folder(self):
        default = 'C:\\Defects\\3220\\Seams'
        self.folder_path = QFileDialog.getExistingDirectory(self, "Choose Folder", default)

        if not self.folder_path:
            return

        dir = QDir(self.folder_path)
        dir.setNameFilters(['*.bmp', '*.png'])
        dir.setSorting(QDir.SortFlag.Name)

        self.image_files = [dir.absoluteFilePath(file_name) for file_name in dir.entryList()]

        if self.image_files:
            self.panel_view.display_image(self.filename())
            self.set_status_bar()

    def browse_model(self):
        default = '.\\src'
        model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', default, 'Onnx files (*.onnx)')

        if not model_path:
            return

        self.model_path = model_path[0]
        model_name = QFileInfo(model_path[0]).fileName()
        self.update_model_name(f'Model: {model_name}')

        # load immediately in memory ... Alexandre will love it
        self.net = cv2.dnn.readNet(self.model_path)
        self.classes = self.load_classes_names()

    @staticmethod
    def load_classes_names():
        with open('src\\classes.names', 'rt') as f:
            classes = f.read().rstrip('\n').split('\n')

        """ @jaime: because my classes.names contains also color and threshold split by ',' and i am dropping rollprints
        because there is only 5 classes for the moment """
        classes = [x.split(',')[0] for x in classes][:-1]
        return classes

    def process_image(self):
        if not self.folder_path:
            self.error_box('Folder Path', 'Please load a folder with images in BMP or PNG')
            return

        if not self.model_path:
            self.error_box('Model Path', 'Please load an ONNX model before to process')
            return

        frame = self.panel_view.image_cvmat
        detections = self.inference.pre_process(frame, self.net)
        img = self.inference.post_process(frame.copy(), detections, self.classes)
        t, _ = self.net.getPerfProfile()
        self.update_inference_time(t)

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.panel_view.display_image(self.filename())
            self.update_inference_time(0.0)
            self.set_status_bar()

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.panel_view.display_image(self.filename())
            self.update_inference_time(0.0)
            self.set_status_bar()

    def show_first_image(self):
        """ show first image in the folder_path """
        if self.folder_path is None:
            return

        self.current_image_index = 0
        self.panel_view.display_image(self.filename())
        self.update_inference_time(0.0)
        self.set_status_bar()

    def show_last_image(self):
        """ show last image in the folder_path"""
        if self.folder_path is None:
            return

        self.current_image_index = len(self.image_files) - 1
        self.panel_view.display_image(self.filename())
        self.update_inference_time(0.0)
        self.set_status_bar()

    def reset_brightness(self):
        """ reset slider and brightness """
        if self.folder_path is None:
            return

        self.brightness_slider.setValue(0)
        self.panel_view.set_brightness(0)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)

    def update_inference_time(self, t):
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv2.getTickFrequency())
        self.inference_time.setText(label)

    def filename(self):
        return self.image_files[self.current_image_index]

    def error_box(self, title, message):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.exec()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image_window = MainWindow()
    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
