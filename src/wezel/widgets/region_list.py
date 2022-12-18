from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QWidget, 
    QComboBox, QToolBar, 
    QHBoxLayout, QVBoxLayout,
    QPushButton)

from wezel import icons, widgets

class RegionList(QWidget):
    """Manages a list of regions on the same underlay series"""

    def __init__(self, layout='Horizontal'):
        super().__init__()
        self.seriesCanvas = None
        self._defineWidgets()
        self._defineConnections()
        if layout=='Vertical':
            self._defineLayoutVertical()
        elif layout == 'Horizontal':
            self._defineLayout()

    def _defineWidgets(self):
        self.comboBox = QComboBox()
        self.comboBox.setDuplicatesEnabled(False)
        self.comboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.comboBox.setToolTip("List of regions")
        self.comboBox.setEditable(True)
        self.comboBox.setInsertPolicy(QComboBox.InsertAtCurrent)
        self.comboBox.setDuplicatesEnabled(True)
        self.comboBox.setEnabled(False)
        self.comboBox.setFixedWidth(115)
        #self.btnLoad = QPushButton()
        self.btnLoad = QAction()
        self.btnLoad.setToolTip('Load new ROIs')
        self.btnLoad.setIcon(QIcon(icons.application_import))
        #self.btnNew = QPushButton() 
        self.btnNew = QAction() 
        self.btnNew.setToolTip('Create a new ROI')
        self.btnNew.setIcon(QIcon(icons.plus))
        #self.btnDelete = QPushButton() 
        self.btnDelete = QAction() 
        self.btnDelete.setToolTip('Delete the current ROI')
        self.btnDelete.setIcon(QIcon(icons.minus))
        self.btnDelete.setEnabled(False)

    def _defineLayoutVertical(self):
        column = QVBoxLayout()
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self.comboBox, alignment=Qt.AlignLeft)
        #row = QHBoxLayout()
        #row.setContentsMargins(0, 0, 0, 0)
        #row.setSpacing(0)
        row = QToolBar()
        row.addAction(self.btnLoad)
        row.addAction(self.btnNew)
        row.addAction(self.btnDelete)
        column.addWidget(row)
        self.setLayout(column)

    def _defineLayout(self):
        btns = QToolBar()
        btns.addWidget(self.btnLoad)
        btns.addWidget(self.btnNew)
        btns.addWidget(self.btnDelete)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(btns, alignment=Qt.AlignLeft)
        # layout.addWidget(self.btnLoad, alignment=Qt.AlignLeft)
        # layout.addWidget(self.btnNew, alignment=Qt.AlignLeft)
        # layout.addWidget(self.btnDelete, alignment=Qt.AlignLeft)
        layout.addWidget(self.comboBox, alignment=Qt.AlignLeft)
        self.setLayout(layout)

    def setView(self):
        regions = self.seriesCanvas.regionNames()
        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        self.comboBox.addItems(regions)
        self.comboBox.setEnabled(regions != [])
        if regions != []:
            i = self.seriesCanvas.currentIndex()
            self.comboBox.setCurrentIndex(i)
            self.currentIndex = i
        self.comboBox.blockSignals(False)
        self.btnDelete.setEnabled(regions != [])

    def _defineConnections(self):
        self.comboBox.currentIndexChanged.connect(self.currentIndexChanged)
        self.comboBox.editTextChanged.connect(lambda text: self.editTextChanged(text))
        self.btnLoad.triggered.connect(self._loadRegion)
        self.btnNew.triggered.connect(self._newRegion)
        self.btnDelete.triggered.connect(self._deleteRegion)

    def currentIndexChanged(self):
        self.currentIndex = self.comboBox.currentIndex()
        self.seriesCanvas.setCurrentRegion(self.currentIndex)

    def editTextChanged(self, text):
        if self.currentIndex == self.comboBox.currentIndex():
            self.seriesCanvas.setCurrentRegionName(text)
            self.setView()

    def setSeriesCanvas(self, seriesCanvas):
        self.seriesCanvas = seriesCanvas
        self.setView()

    def _newRegion(self):
        self.seriesCanvas.addRegion()
        self.setView()
        
    def _deleteRegion(self): # deletes it from the list 
        self.seriesCanvas.removeCurrentRegion()
        self.setView()
        
    def _loadRegion(self):
        self.seriesCanvas.loadRegion()
        self.setView()