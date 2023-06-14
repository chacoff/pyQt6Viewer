import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices
import sys
import numpy


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.model_name = QLabel('model: *.onnx')
        self.image_name_label = QLabel('image name')

        layout = QVBoxLayout()
        layout.addWidget(self.model_name)
        layout.addWidget(self.image_name_label)

        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
            }

            QLabel {
                color: #333333;
                font-size: 18px;
                padding: 10px;
            }
        """)

        self.setLayout(layout)

    def update_image_name(self, image_name):
        self.image_name_label.setText(image_name)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)