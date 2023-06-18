import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()
        self.classes_names = []
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Class', 'Color', 'Threshold'])
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addStretch()
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_classes_names_view(self, classes_names):
        """ update the available classes upon loading the model based on classes.names"""

        self.classes_names = classes_names
        self.table.setRowCount(len(self.classes_names))

        for row, (name, color, thre) in enumerate(self.classes_names):
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            color_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 1, color_item)

            thre_item = QTableWidgetItem(thre)
            # thre_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 2, thre_item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
