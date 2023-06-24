import os
import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, \
    QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QMessageBox, QGridLayout, QDialog
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
from timeit import default_timer as timer
from imageview import ImageView
from imageinfo import ImageInfo
from YoloV5_Onnx_detect import YoloV5OnnxSeams
import os
import pandas as pd
from Matrix import create_matrix


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = 0
        self.folder_path = None
        self.model_path = None
        self.net = None
        self.classes = []
        self.classes_color = []
        self.classes_thre = []
        self.counters = [0]
        self.counters_classification = [0] * 4
        self.alex = True  # fast mode for desperators
        self.matrix_dict = {}
        self.matrix_csv = self.unique_file('matrix/current_matrix.csv')
        self.matrix_img = self.unique_file('matrix/confusion_matrix.png')
        self.user_flag = False

        # Model name
        self.model_name = QLabel('Model: *.onnx')
        self.model_name.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #606060;}''')

        self.inference_time = QLabel('Inference time: 0.00 ms')
        self.inference_time.setStyleSheet('''QLabel {font-size: 18px; font-weight: bold; color: #FF8040;}''')

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
        self.setWindowTitle('Seams Processor Viewer - v1.00j - RDEsch')

        # toolbar
        toolbar = self.addToolBar('Menu')
        browse_action = QAction("Browse", self)  # QIcon('')
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('w')
        process_action = QAction("Process", self)
        process_action.triggered.connect(self.process_image)
        process_action.setShortcut('p')
        model_action = QAction("Model", self)
        model_action.triggered.connect(self.browse_model)
        model_action.setShortcut('m')
        first_im_action = QAction("<< First Image", self)
        first_im_action.triggered.connect(self.show_first_image)
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        center_image_action = QAction('Reset Zoom', self)
        center_image_action.triggered.connect(self.panel_view.setImageinCenter)
        center_image_action.setShortcut('c')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        last_im_action = QAction("Last Image >>", self)
        last_im_action.triggered.connect(self.show_last_image)
        reset_brightness = QAction('Reset Brightness', self)
        reset_brightness.triggered.connect(self.reset_brightness)
        reset_brightness.setShortcut('b')
        model_is_ok = QAction(QIcon('includes/da_32.png'), 'Yes', self)
        model_is_ok.triggered.connect(self.model_is_ok)
        model_is_ok.setShortcut('o')
        model_is_not_ok = QAction(QIcon('includes/net_32.png'), 'No', self)
        model_is_not_ok.triggered.connect(self.model_is_not_ok)
        model_is_not_ok.setShortcut('n')
        open_matrix = QAction(QIcon('includes/matrix_32.png'), 'Open Matrix', self)
        open_matrix.triggered.connect(self.open_matrix_image)
        # Loading buttons
        toolbar.addAction(browse_action)
        toolbar.addAction(model_action)
        toolbar.addAction(process_action)
        toolbar.addSeparator()
        # Actions buttons
        toolbar.addAction(first_im_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(center_image_action)
        toolbar.addAction(next_action)
        toolbar.addAction(last_im_action)
        toolbar.addAction(reset_brightness)
        toolbar.addSeparator()
        # Statistics buttons
        toolbar.addAction(model_is_ok)
        toolbar.addAction(model_is_not_ok)
        toolbar.addAction(open_matrix)
        toolbar.setStyleSheet('''
            QToolBar {
                background-color: #f2f2f2;
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

        header = QGridLayout()

        # header
        header.addWidget(self.model_name, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.inference_time, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.image_name_title, 0, 1, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.model_prediction_label, 0, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self.ground_truth_label, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        main_vertical_layout.addItem(header)

        # the 2 panels are the horizontal panel with the image viewer and the panel info
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

    def model_is_ok(self):
        """
            X-axis reference to update the vector self.counters_classification
            Seams Ground 0
            NoSeams Ground 1
            Seams Prediction 2
            NoSeams Prediction 3
        """
        current_image_name = QFileInfo(self.filename()).fileName()
        ground_truth = self.user_classification(current_image_name, 'Ok')
        self.write_in_csv(ground_truth)
        self.panel_info.update_statistics(self.classes, self.counters, self.classes_color, self.counters_classification)
        self.ground_truth_label.setText(f'ground truth: {ground_truth}')

    def model_is_not_ok(self):
        """
            X-axis reference to update the vector self.counters_classification
            Seams Ground 0
            NoSeams Ground 1
            Seams Prediction 2
            NoSeams Prediction 3
        """
        current_image_name = QFileInfo(self.filename()).fileName()
        ground_truth = self.user_classification(current_image_name, 'NotOk')
        self.write_in_csv(ground_truth)
        self.panel_info.update_statistics(self.classes, self.counters, self.classes_color, self.counters_classification)
        self.ground_truth_label.setText(f'ground truth: {ground_truth}')

    def user_classification(self, current_image_name, user):
        """ handles most of the interactions from the user while classifying the ground truth """

        if current_image_name not in self.matrix_dict:
            self.error_box('Image not processed', 'You need to launch the process of this image before !')
            return

        ground_truth = self.ground_t_calculator(self.matrix_dict[current_image_name], user)

        if not self.user_flag:
            if ground_truth == 'Seams':
                self.counters_classification[0] += 1
            elif ground_truth == 'NoSeams':
                self.counters_classification[1] += 1
            self.user_flag = True

        return ground_truth

    def write_in_csv(self, ground_t):
        current_image_name = QFileInfo(self.filename()).fileName()

        if current_image_name not in self.matrix_dict:
            return

        new_file = not os.path.exists(self.matrix_csv)

        if new_file:
            df = pd.DataFrame(columns=['FileName', 'Ground_truth', 'Predict'])
        else:
            df = pd.read_csv(self.matrix_csv)

        if current_image_name in df['FileName'].to_list():
            df = df.drop(df[df['FileName'] == current_image_name].index)

        data = [current_image_name, ground_t, self.matrix_dict[current_image_name]]
        new_line = pd.DataFrame([data], columns=['FileName', 'Ground_truth', 'Predict'])
        df = pd.concat([df, new_line], ignore_index=True)
        df.to_csv(self.matrix_csv, index=False)

    def open_matrix_image(self):
        create_matrix(self.matrix_img, self.matrix_csv)

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

    def set_status_bar(self):
        """ set the status bar with some information about the current image
        set title in the header about the current image and predictions
        """

        self.image_name_title.setText(QFileInfo(self.filename()).fileName())
        self.model_prediction_label.setText('prediction: ')
        self.ground_truth_label.setText('ground truth: ')

        message = f'{self.current_image_index + 1} of {len(self.image_files)} - ' \
                  f'{QFileInfo(self.filename()).fileName()} - ' \
                  f'{self.panel_view.channel}x{self.panel_view.height}x{self.panel_view.width} in ' \
                  f'{self.folder_path}'
        self.statusBar().showMessage(message)

    def browse_folder(self):
        default = 'C:\\Users\\gomezja\\PycharmProjects\\201_SeamsModel\\dataset\\dev'

        if self.alex:
            self.folder_path = default
        else:
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

        if self.alex:
            model_path = os.path.join('c:\\','Users','gomezja', 'PycharmProjects', '202_SeamsProcessing','Viewer', 'src', 'best_exp2_Small_v2_768_5c.onnx')
            self.model_path = model_path
            model_name = model_path.split('\\')[-1]
        else:
            model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', default, 'Onnx files (*.onnx)')
            self.model_path = model_path[0]
            model_name = QFileInfo(model_path[0]).fileName()

        if not model_path:
            return

        self.update_model_name(f'Model: {model_name}')
        self.read_classes_file()

    def read_classes_file(self):
        """ classes.names contains also color and threshold """
        classes_names_raw = []
        with open('src\\classes.names', 'rt') as file:
            lines = file.readlines()
            for line in lines:
                name, color, thre = line.strip().split(',')
                color = color.split(';')
                r, g, b = map(int, color)
                classes_names_raw.append((name, QColor(r, g, b), thre))

            # @jaime: i am dropping rollprints because there is only 5 classes for the moment
            classes_names_raw = classes_names_raw[:-1]
            self.panel_info.update_classes_names_view(classes_names_raw)

            for row, (name, color, thre) in enumerate(classes_names_raw):
                self.classes.append(name)
                self.classes_color.append(color)
                self.classes_thre.append(thre)

            self.counters = [0] * len(self.classes)  # updates counter's length according the number of classes

    def process_image(self):
        """ process the image will trigger the statistic counters and will start filling
        the dictionary self.matrix_dict storing all the images already processed
        """

        if not self.folder_path:
            self.error_box('Folder Path', 'Please load a folder with images in BMP or PNG')
            return

        if not self.model_path:
            self.error_box('Model Path', 'Please load an ONNX model before to process')
            return

        frame = self.panel_view.image_cvmat  # gets the current image on the scene

        # Actual new processing
        t0 = timer()
        self.inference.process_image(self.classes, self.model_path, frame)
        predictions = self.inference.return_predictions()
        t1 = timer()
        self.update_inference_time(t1-t0)

        self.panel_view.draw_boxes_and_labels(predictions, self.classes_color)
        self.statistics_counter(predictions)
        self.panel_info.update_statistics(self.classes, self.counters, self.classes_color, self.counters_classification)

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

        current_image_name = QFileInfo(self.filename()).fileName()

        if current_image_name not in self.matrix_dict:
            self.user_flag = False
            for prediction in predictions:
                class_id = prediction.class_id
                self.counters[class_id] += 1
    
                # if class_id == 1:
                #     self.mydict[os.path.split(self.filename())[1][:]] = "NoSeams"
                # elif class_id == 0:
                #     self.mydict[os.path.split(self.filename())[1][:]] = "Seams"
    
            # Final classification of the model, Seams if there is at least one seams detected
            classification = [c.class_name for c in predictions if c.class_name == 'Seams']
            
            if len(classification) == 0:  # it means no seams where detected in the beam
                # here's the first time the image is included in self.matrix_dict
                self.matrix_dict[current_image_name] = "NoSeams"
                self.model_prediction_label.setText(f'prediction: NoSeams')
                self.counters_classification[3] += 1
            else:
                self.matrix_dict[current_image_name] = "Seams"
                self.model_prediction_label.setText(f'prediction: Seams')
                self.counters_classification[2] += 1

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
    def ground_t_calculator(a, b):
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
        k = 1

        while os.path.exists(path):
            path = root + '(' + str(k) + ')' + ext
            k += 1

        return path


if __name__ == '__main__':
    app = QApplication(sys.argv)

    image_window = MainWindow()
    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
