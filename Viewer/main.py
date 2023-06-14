import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy
from imageview import ImageView
from imageinfo import ImageInfo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = 0
        self.folder_path = None

        # Panel classes
        self.panel_view = ImageView()
        self.panel_info = ImageInfo()
        self.setWindowTitle('Seams Viewer')

        # toolbar
        toolbar = self.addToolBar('Menu')
        browse_action = QAction("Browse", self)  # QIcon('')
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('o')
        process_action = QAction("Process", self)
        process_action.setShortcut('p')
        model_action = QAction("Model", self)
        model_action.triggered.connect(self.browse_model)
        model_action.setShortcut('m')
        firstIm_action = QAction("<< First Image", self)
        firstIm_action.triggered.connect(self.show_first_image)
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        lastIm_action = QAction("Last Image >>", self)
        lastIm_action.triggered.connect(self.show_last_image)
        toolbar.addAction(browse_action)
        toolbar.addAction(process_action)
        toolbar.addAction(model_action)
        toolbar.addAction(firstIm_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(next_action)
        toolbar.addAction(lastIm_action)
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
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setMinimum(-100)
        brightness_slider.setMaximum(100)
        brightness_slider.setSingleStep(2)
        brightness_slider.valueChanged.connect(self.panel_view.set_brightness)
        brightness_slider.setValue(0)
        brightness_slider.setStyleSheet("""
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

        # main container layout
        layout = QHBoxLayout()

        # layout to contain image viewer and image tools such as the slider
        image_view_layout = QVBoxLayout()
        image_view_layout.addWidget(self.panel_view, 5)
        image_view_layout.addWidget(brightness_slider, 2)
        image_view_layout.addWidget(toolbar, 1)

        w_slider = QWidget()
        w_slider.setLayout(image_view_layout)

        layout.addWidget(w_slider, 5)
        layout.addWidget(self.panel_info, 1)

        w = QWidget()
        w.setLayout(layout)
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
        default = 'C:\\Users\\gomezja\\PycharmProjects\\201_SeamsModel\\runs\\onnx_testedModels'
        model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', default, 'Onnx files (*.onnx)')

        if not model_path:
            return

        model_name = QFileInfo(model_path[0]).baseName()
        self.panel_info.update_model_name(f'model: {model_name}')

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.panel_view.display_image(self.filename())
            self.set_status_bar()

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.panel_view.display_image(self.filename())
            self.set_status_bar()

    def show_first_image(self):
        if self.folder_path is None:
            return

        self.current_image_index = 0
        self.panel_view.display_image(self.filename())
        self.set_status_bar()

    def show_last_image(self):
        if self.folder_path is None:
            return

        self.current_image_index = len(self.image_files) - 1
        self.panel_view.display_image(self.filename())
        self.set_status_bar()

    def filename(self):
        return self.image_files[self.current_image_index]


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image_window = MainWindow()
    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
