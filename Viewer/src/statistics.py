from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
import pyqtgraph as pg


class StatisticsPlot(QWidget):
    def __init__(self):
        super().__init__()
        self.classes = []
        self.incidences = []

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        # self.setCentralWidget(self.plot_widget)
        self.plot_widget.hideAxis('left')
        self.plot_widget.hideAxis('right')
        self.plot_widget.getAxis('bottom').setTicks([list(enumerate(self.classes))])
        self.plot_widget.setMouseEnabled(x=False, y=False)

        # self.setup_plot()

    def setup_plot(self, colors):

        brushes = (253, 127, 63)
        bar_graph = pg.BarGraphItem(x=range(len(self.classes)), height=self.incidences, width=0.8, brush=brushes)
        self.plot_widget.addItem(bar_graph)

        for i, incidence in enumerate(self.incidences):
            label = pg.TextItem(text=f'{self.classes[i]}: {incidence}', color='w', anchor=(0.5, 0))
            label.setPos(i, incidence)
            self.plot_widget.addItem(label)

    def get_classes(self, classes):
        self.classes = classes

    def get_incidences(self, incidences):
        self.incidences = incidences
