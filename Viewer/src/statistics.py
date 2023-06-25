from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg


class StatisticsPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.classes = []
        self.incidences = []

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('right')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setStyleSheet(" margin:0px; border:1px solid rgb(130, 135, 144); ")

    def setup_plot(self, colors):
        """ set up and update defect instance counter """

        if colors is None:
            return

        self.plot_widget.clear()

        x = range(len(self.classes))
        bar_graph = pg.BarGraphItem(x=x,
                                    height=self.incidences,
                                    width=0.8,
                                    brushes=[colors[cl] for cl in x],
                                    title='Defect Counter')

        self.plot_widget.addItem(bar_graph)

        for i, incidence in enumerate(self.incidences):

            counter = pg.TextItem(text=f'{incidence}',  # f'{self.classes[i]}: {incidence}',
                                color='w',
                                anchor=(0.5, 0))
            counter.setPos(i, incidence)
            self.plot_widget.addItem(counter)

        x_axis_labels = [pg.TextItem(text=class_, anchor=(0.5, 0), color='#828790') for class_ in self.classes]
        for i, label in enumerate(x_axis_labels):
            label.setPos(i, 0)
            self.plot_widget.addItem(label)

    def get_classes(self, classes):
        self.classes = classes

    def get_incidences(self, incidences):
        self.incidences = incidences


class ClassificationPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.x_axis = []
        self.y_axis = []

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('right')
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setStyleSheet(" margin:0px; border:1px solid rgb(130, 135, 144); ")

    def setup_plot(self):
        """" plot the predictions and user ground truth """

        self.plot_widget.clear()

        x = range(len(self.x_axis))
        bar_graph = pg.BarGraphItem(x=x,
                                    height=self.y_axis,
                                    width=0.8,
                                    brushes=['#F8BA7C', '#F8BA7C', '#FF8811', '#FF8811'],
                                    title='Classification')

        self.plot_widget.addItem(bar_graph)

        for i, classification in enumerate(self.y_axis):

            counter = pg.TextItem(text=f'{classification}',
                                  color='w',
                                  anchor=(0.5, 0))
            counter.setPos(i, classification)
            self.plot_widget.addItem(counter)

        x_axis_labels = [pg.TextItem(text=x_ax, anchor=(0.5, 0), color='#828790') for x_ax in self.x_axis]

        for i, label in enumerate(x_axis_labels):
            label.setPos(i, 0)
            self.plot_widget.addItem(label)

    def get_x_axis(self, x_axis):
        self.x_axis = x_axis

    def get_y_axis(self, y_axis):
        self.y_axis = y_axis
