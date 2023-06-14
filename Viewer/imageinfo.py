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

        self.model_name = QLabel('model: *.onnx')

        title_model = QLabel("Model")
        title_model.setStyleSheet('''QLabel {font-size: 22px; font-weight: bold; color: #606060;}''')

        classes = self.read_classes_file('includes\\classes.names')

        table = QTableWidget()
        table.setColumnCount(3)
        table.setRowCount(len(classes))
        table.setHorizontalHeaderLabels(['Class', 'Color', 'Threshold'])
        table.verticalHeader().setVisible(False)

        for row, (name, color, thre) in enumerate(classes):
            # Set the name in the left column
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 0, name_item)

            # Set the color in the right column
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            color_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 1, color_item)

            thre_item = QTableWidgetItem(thre)
            # thre_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(row, 2, thre_item)

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(title_model)
        layout.addWidget(self.model_name)
        layout.addWidget(table)
        layout.addStretch()
        self.setLayout(layout)

    def update_model_name(self, model_name):
        self.model_name.setText(model_name)

    def read_classes_file(self, classes_file_path):
        classes = []
        with open(classes_file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                name, color, thre = line.strip().split(',')
                color = color.split(';')
                r, g, b = map(int, color)
                classes.append((name, QColor(r, g, b), thre))
        return classes