from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import ( 
    QLabel, 
)

from PySide2.QtGui import QImage, QPixmap
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from wezel import icons

class ImageLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        self.setData(icons.wezel)
        
    def setData(self, file):
        self.im = QPixmap(file).scaledToWidth(512)
        self.setPixmap(self.im)


class MatplotLib(QLabel):

    def __init__(self):
        super().__init__()
        self.setScaledContents(True)
        
    def setData(self, fig):
        canvas = FigureCanvas(fig)
        canvas.draw()
        width, height = fig.figbbox.width, fig.figbbox.height
        img = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
        self.im = QPixmap(img).scaledToWidth(512)
        self.setPixmap(self.im)


