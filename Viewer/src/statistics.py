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
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setStyleSheet(" margin:0px; border:1px solid rgb(130, 135, 144); ")
        # self.setup_plot()

    def setup_plot(self, colors):
        """ set up and update defect counter """

        if colors is None:
            return

        x = range(len(self.classes))
        bar_graph = pg.BarGraphItem(x=x,
                                    height=self.incidences,
                                    width=0.8,
                                    brushes=[colors[cl] for cl in x],
                                    title='Defect Counter')

        self.plot_widget.addItem(bar_graph)

        for i, incidence in enumerate(self.incidences):

            label = pg.TextItem(text=f'{incidence}',  # f'{self.classes[i]}: {incidence}',
                                color='w',
                                anchor=(0.5, 0))
            label.setPos(i, incidence)
            self.plot_widget.addItem(label)

    def get_classes(self, classes):
        self.classes = classes

    def get_incidences(self, incidences):
        self.incidences = incidences