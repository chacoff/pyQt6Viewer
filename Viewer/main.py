import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices
import sys
import numpy
from imageview import ImageView
from imageinfo import ImageInfo


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = 0

        # Panel classes
        self.panel_view = ImageView()
        self.panel_info = ImageInfo()
        self.setWindowTitle('Seams Viewer')

        # toolbar
        toolbar = self.addToolBar('File')
        browse_action = QAction("Browse", self)
        browse_action.triggered.connect(self.browse_folder)
        browse_action.setShortcut('o')
        process_action = QAction("Process", self)
        process_action.setShortcut('p')
        model_action = QAction("Model", self)
        model_action.triggered.connect(self.browse_model)
        model_action.setShortcut('m')
        previous_action = QAction("< Previous", self)
        previous_action.triggered.connect(self.show_previous_image)
        previous_action.setShortcut('a')
        next_action = QAction("Next >", self)
        next_action.triggered.connect(self.show_next_image)
        next_action.setShortcut('d')
        toolbar.addAction(browse_action)
        toolbar.addAction(process_action)
        toolbar.addAction(model_action)
        toolbar.addAction(previous_action)
        toolbar.addAction(next_action)
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
                height: 20px;
                margin: 2px;
                padding: 2px;
            }

            QSlider::groove:horizontal {
                border: none;
                background-color: #D0D0D0;
                height: 20px;
            }

            QSlider::handle:horizontal {
                background-color: #606060;
                border: none;
                width: 35px;
                height: 35px;
                margin: -5px 0;
                border-radius: 5px;
            }
        """)

        # main container layout
        layout = QHBoxLayout()

        # layout to contain image viewer and image tools such as the slider
        image_view_layout = QVBoxLayout()
        image_view_layout.addWidget(self.panel_view, 5)
        image_view_layout.addWidget(brightness_slider, 2)

        w_slider = QWidget()
        w_slider.setLayout(image_view_layout)

        layout.addWidget(w_slider, 5)
        layout.addWidget(self.panel_info, 1)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def browse_folder(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Choose Folder", 'C:\\Defects\\3220\\Seams')

        if not folder_path:
            return

        dir = QDir(folder_path)
        dir.setNameFilters(['*.bmp', '*.png'])
        dir.setSorting(QDir.SortFlag.Name)

        self.image_files = [dir.absoluteFilePath(file_name) for file_name in dir.entryList()]

        if self.image_files:
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def browse_model(self):
        model_path = QFileDialog.getOpenFileName(self, 'Choose Onnx Model', '', 'Onnx files (*.onnx)')

        if not model_path:
            return

        model_name = QFileInfo(model_path[0]).baseName()
        self.panel_info.update_model_name(f'model: {model_name}')

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.panel_view.display_image(self.filename())
            self.panel_info.update_image_name(QFileInfo(self.filename()).baseName())

    def filename(self):
        return self.image_files[self.current_image_index]


if __name__ == '__main__':

    app = QApplication(sys.argv)

    image_window = MainWindow()

    #palette = image_window.palette()
    #palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
    #image_window.setPalette(palette)

    image_window.show()
    image_window.showMaximized()
    sys.exit(app.exec())
