from PySide2.QtWidgets import (
    QVBoxLayout,
)

import wezel
from wezel import widgets

class PlotDisplay(wezel.gui.MainWidget):
    """
    GUI for displaying a 4D numpy array
    """

    def __init__(self, *args, **kwargs): 
        super().__init__()
        self.initUI()
        self.setPlot(*args, **kwargs)

    def initUI(self):

        # Widgets
        self.plot = widgets.PlotCurve()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.plot)
        self.setLayout(layout)

    def setPlot(self, x, y, 
            xlabel='x-axis', ylabel='y-axis',
            xlim=None, ylim=None,
        ):
        self.x = x
        self.y = y
        self.plot.setXlabel(xlabel)
        self.plot.setYlabel(ylabel)
        self.plot.setXlim(xlim)
        self.plot.setYlim(ylim)
        self.plot.setData(x, y)

    def set_xlabel(self, label):
        self.plot.setXlabel(label)

    def set_ylabel(self, label):
        self.plot.setYlabel(label)

    def draw(self):
        self.plot.setData(self.x, self.y)














