
from PySide2.QtWidgets import QVBoxLayout

import wezel
from wezel import widgets, canvas


class SeriesDisplay(wezel.gui.MainWidget):

    def __init__(self, series=None):
        super().__init__()

        self.setupUI()
        self.setSeries(series)

    def setupUI(self):

        # Toolbar
        self.toolBarClass = canvas.ToolBar

        # Widgets
        self.sliders = widgets.SeriesSliders()
        self.canvas = canvas.SeriesCanvas(self)

        # Connections
        self.sliders.valueChanged.connect(self.slidersChanged)
        self.canvas.arrowKeyPress.connect(lambda arrow: self.arrowKeyPress(arrow))
        self.canvas.mousePositionMoved.connect(
            lambda x, y: self.series().status.pixelValue(x,y,self.canvas.array())
        )

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.canvas)
        layout.addWidget(self.sliders)
        self.setLayout(layout)


    def setToolBar(self, toolBar):
        super().setToolBar(toolBar)
        self.canvas.fitItem()

    def setToolBarState(self):
        self.toolBar.setWidget(self.canvas)

    def setActive(self, active):
        #super().setActive(active)
        if not active:
            self.canvas.saveMask()

    def closeEvent(self, event):
        newSeries = self.canvas._model.saveRegions()
        if newSeries:
            self.databaseUpdated.emit()

    def series(self):
        return self.canvas._model._series
        
    def setSeries(self, series):
        if series is None:
            return
        if series.instances() == []:
            self.setError('Series ' + series.label() + ' is empty. \n\n Nothing to show here..')
            return
        self.sliders.setData(series)
        self.canvas._model._series = series
        image = self.sliders.image
        if image is None:
            return
        image.read()
        array = image.array()
        if array is None:
            self.setError('Series ' + series.label() + ' does not contain images. \n\n Nothing to show here..')
            image.clear()
            return
        self.canvas.setArray(
            array,
            image.SOPInstanceUID, 
            image.WindowCenter, 
            image.WindowWidth, 
            image.colormap,
        )
        image.clear()

    def slidersChanged(self):
        image = self.sliders.image
        if image is None:
            self.canvas.setBlank()
            return
        image.read()
        self.canvas.changeArray(
            image.array(), 
            image.SOPInstanceUID, 
            image.WindowCenter, 
            image.WindowWidth, 
            image.colormap,
        )
        image.clear()
        
    def arrowKeyPress(self, key):
        image_before = self.sliders.image
        self.sliders.move(key=key)
        image_after = self.sliders.image
        if image_after != image_before:
            if image_after is None:
                return
            image_after.read()
            self.canvas.changeArray(
                image_after.array(), 
                image_after.SOPInstanceUID, 
                image_after.WindowCenter, 
                image_after.WindowWidth, 
                image_after.colormap,
            )
            image_after.clear()