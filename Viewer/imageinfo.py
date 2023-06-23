import cv2
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy
from src.statistics import StatisticsPlot, ClassificationPlot


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.classes_names = []
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Class', 'Color', 'Threshold'])
        self.table.verticalHeader().setVisible(False)

        # detection statistics per instance
        self.stats = StatisticsPlot()
        self.stats.setup_plot(None)

        # detection statistics according classification
        self.class_plot = ClassificationPlot()
        self.class_plot.setup_plot()

        image_logo = QLabel()
        image_logo.setPixmap(QPixmap.fromImage(QImage("includes/logoAM.png")))

        layout = QVBoxLayout()
        layout.addWidget(self.table, 2)
        layout.addWidget(self.stats.plot_widget, 2)
        layout.addWidget(self.class_plot.plot_widget, 2)
        layout.addStretch(1)
        # layout.addWidget(image_logo, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def update_statistics(self, classes, incidences, colors, y_axis):
        """ updates the plot with statistics of single ocurrences """

        self.stats.get_classes(classes)
        self.stats.get_incidences(incidences)
        self.stats.setup_plot(colors)

        self.class_plot.get_x_axis(['Seams\nGround', 'NoSeams\nGround', 'Seams\nPrediction', 'NoSeams\nPrediction'])
        self.class_plot.get_y_axis(y_axis)
        self.class_plot.setup_plot()

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
