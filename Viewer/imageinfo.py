import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.model_name = QLabel('model: *.onnx')
        self.model_n_classes = QLabel('Number of classes: xx')

        title_model = QLabel("Model")
        title_model.setStyleSheet('''QLabel {font-size: 22px; font-weight: bold; color: #606060; padding: 2px;}''')

        layout = QVBoxLayout()
        layout.addWidget(title_model)
        layout.addWidget(self.model_name)
        layout.addWidget(self.model_n_classes)
        layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
            }

            QLabel {
                color: #333333;
                font-size: 16px;
                padding: 2px;
            }
        """)

        self.setLayout(layout)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)