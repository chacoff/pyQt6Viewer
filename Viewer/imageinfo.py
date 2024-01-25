from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, \
    QFileDialog, QMainWindow, QSlider, QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, QPointF, QDir, QSize, pyqtSignal, QFileInfo, QUrl
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QPainter, QPalette, QAction, QDesktopServices, QColor, QIcon
import sys
import numpy
from src.statistics import StatisticsPlot, ClassificationPlot
import sqlite3
import pandas as pd


class ImageInfo(QWidget):

    def __init__(self):
        super().__init__()

        self.db_name = 'seams_processor.db'
        self.classes_names = []
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Class', 'Color', 'Thres', 'iou'])
        self.table.verticalHeader().setVisible(False)

        # detection statistics per instance
        self.stats = StatisticsPlot()
        self.stats.setup_plot(None)

        # detection statistics according classification
        self.class_plot = ClassificationPlot()
        self.class_plot.setup_plot()

        layout = QVBoxLayout()
        layout.addWidget(self.table, 2)
        layout.addWidget(self.stats.plot_widget, 2)
        layout.addWidget(self.class_plot.plot_widget, 2)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    @staticmethod
    def get_data_from_db(db_name) -> [list, list]:
        """" gets all data from the database and return 2 lists to plot """

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT Predict, Ground_truth, Seams, Beam, Souflure, Hole, Water FROM seams_processor")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['Ground_truth', 'Predict', 'Seams', 'Beam', 'Souflure', 'Hole', 'Water'])
        cursor.close()
        conn.close()

        ground_seams = df['Ground_truth'].isin(['Seams']).sum()
        ground_noseams = df['Ground_truth'].isin(['NoSeams']).sum()

        predict_seams = df['Predict'].isin(['Seams']).sum()
        predict_noseams = df['Predict'].isin(['NoSeams']).sum()

        y_axis = [predict_seams,
                  predict_noseams,
                  ground_seams,
                  ground_noseams]

        seams_sum = df['Seams'].sum()
        beams_sum = df['Beam'].sum()
        souflure_sum = df['Souflure'].sum()
        hole_sum = df['Hole'].sum()
        water_sum = df['Water'].sum()

        incidences = [seams_sum, beams_sum, souflure_sum, hole_sum, water_sum]

        return y_axis, incidences

    def update_statistics(self, classes, colors, db_name):
        """ updates the plot with statistics from the DB """

        y_axis, incidences = self.get_data_from_db(db_name)

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

        for row, (name, color, thre, iou) in enumerate(self.classes_names):
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

            iou_item = QTableWidgetItem(iou)
            # thre_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 3, iou_item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def get_thres_item(self, column) -> list:
        """ get threshold from all rows """

        threshold_values = []
        for row in range(self.table.rowCount()):
            thre_item = self.table.item(row, column)
            if thre_item is not None:
                thre_data = thre_item.text()
                threshold_values.append(float(thre_data))

        return threshold_values
