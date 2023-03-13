import math
import numpy as np
from matplotlib.path import Path as MplPath
import cv2 as cv2
import skimage
from scipy import ndimage as ndi

from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtWidgets import QAction, QMenu, QActionGroup
from PySide2.QtGui import QPixmap, QCursor, QIcon, QColor, QPen

from wezel import canvas, icons


class MaskMove(canvas.FilterItem):
    """Painting or erasing tool.
    """
    def __init__(self):
        super().__init__()
        pixMap = QPixmap(icons.arrow_move)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.icon = QIcon(pixMap)
        self.toolTip = 'Move mask'
        self.text = 'Move mask'
        self.setActionPick()

    def hoverMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.update() 
        cnvs = self.scene().parent()
        cnvs.mousePositionMoved.emit(self.x, self.y)   

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            self.x0 = self.x
            self.y0 = self.y
            self.bin0 = item.bin()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.update()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.moveMask() 
        cnvs = self.scene().parent() 
        cnvs.mousePositionMoved.emit(self.x, self.y)
 
    def moveMask(self):
        cnvs = self.scene().parent() 
        item = cnvs.maskItem
        if item is None:
            return
        bin = ndi.shift(self.bin0, [self.x-self.x0, self.y-self.y0], order=0, mode='grid-wrap')
        item.setBin(bin)
        item.setDisplay()


class MaskBrush(canvas.FilterItem):
    """Painting or erasing tool.
    """
    def __init__(self, brushSize=3, mode="paint"):
        super().__init__()
        self.brushSize = brushSize
        self.setMode(mode)
        self.setActionPick()

    def setMode(self, mode):
        self.mode = mode
        if mode == "paint":
            pixMap = QPixmap(icons.paint_brush)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Paint brush'
            self.text = 'Paint brush'
        elif mode == "erase":
            pixMap = QPixmap(icons.eraser)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Eraser'
            self.text = 'Eraser'
        self.icon = QIcon(pixMap)

    def paint(self, painter, option, widget):
        """Abstract method - must be overridden."""
        if self.x is None:
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        w = int((self.brushSize - 1)/2)
        painter.drawRect(
            self.x-w, 
            self.y-w, 
            self.brushSize, 
            self.brushSize)

    def hoverMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.update() 
        cnvs = self.scene().parent()
        cnvs.mousePositionMoved.emit(self.x, self.y)   

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            self.paintPixels()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.update()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.paintPixels() 
        cnvs = self.scene().parent() 
        cnvs.mousePositionMoved.emit(self.x, self.y)
 
    def paintPixels(self):
        cnvs = self.scene().parent() 
        item = cnvs.maskItem
        if item is None:
            return
        w = int((self.brushSize - 1)/2)
        for x in range(self.x-w, self.x+w+1, 1):
            if 0 <= x < item.bin().shape[0]:
                for y in range(self.y-w, self.y+w+1, 1):
                    if 0 <= y < item.bin().shape[1]:
                        item.setPixel(x, y, self.mode=="paint")
        item.update()

    def contextMenu(self):
        return self.actionPick.menu()
       
    def setOptions(self, brushSize):
        self.brushSize = brushSize
        self.pick()

    def menuOptions(self):
        menu = QMenu()
        menu.triggered.connect(lambda action: self.setOptions(action.option))
        actionGroup = QActionGroup(menu)
        settings = {
            '1 pixel': 1,
            '3 pixels': 3,
            '5 pixels': 5,
            '7 pixels': 7,
            '9 pixels': 9,
            '11 pixels': 11,
            '21 pixels': 21,
            '31 pixels': 31,
        }
        for text, value in settings.items():
            action = QAction(text)
            action.option = value
            action.setCheckable(True)
            action.setChecked(value == self.brushSize)
            actionGroup.addAction(action)
            menu.addAction(action)
        return menu


class MaskPenSet(canvas.FilterSet):
    def __init__(self, mode='draw'):
        super().__init__()
        self.filters = [
            MaskPenFreehand(mode=mode),
            MaskPenPolygon(mode=mode),
            MaskPenRectangle(mode=mode),
            MaskPenCircle(mode=mode),
            MaskPenContour(mode=mode),
            MaskPenAllContours(mode=mode),
        ]
        self.icon = self.filters[0].icon
        self.text = self.filters[0].text
        self.current = self.filters[0]
        self.setActionPick()


class MaskPen(canvas.FilterItem):

    def __init__(self, mode='draw'):
        super().__init__()
        self.setMode(mode)
        self.setActionPick()

    def setMode(self, mode):
        self.mode = mode
        if mode == "draw":
            pixMap = QPixmap(icons.pencil)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Draw'
            self.text = 'Draw'
        elif mode == "cut":
            pixMap = QPixmap(icons.cutter)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Cut'
            self.text = 'Cut'
        elif mode == "catch":
            pixMap = QPixmap(icons.lifebuoy)
            self.cursor = QCursor(pixMap, hotX=8, hotY=8)
            self.toolTip = 'Catch'
            self.text = 'Catch'
        self.icon = QIcon(pixMap)


class MaskPenFreehand(MaskPen):
    """Freehand region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode)
        self.iconInSet = QIcon(icons.layer_shape_curve)
        self.textInSet = 'Freehand'
        self.path = None
        # self.xc = None
        # self.yc = None
        
    def paint(self, painter, option, widget):
        if self.path is None: 
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        position = self.path[0]
        p1 = QPointF(position[0], position[1])
        for position in self.path[1:]:
            p2 = QPointF(position[0], position[1])
            painter.drawLine(p1, p2)
            p1 = p2
        position = self.path[0]
        p2 = QPointF(position[0], position[1])
        painter.drawLine(p1, p2)

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            position = [event.pos().x(), event.pos().y()]
            self.path = [position]

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.path is not None:
                self.fillPath()
                self.path = None

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            position = [event.pos().x(), event.pos().y()]
            if self.path is not None:
                if position != self.path[-1]:
                    self.path.append(position)
                    self.update()

    def fillPath(self):
        if len(self.path) == 0: 
            return
        item = self.scene().parent().maskItem
        if item is None:
            return
        bin = np.zeros(item.bin().shape, dtype=bool)
        rr, cc = skimage.draw.polygon([p[0]-0.5 for p in self.path], [p[1]-0.5 for p in self.path], item.bin().shape)
        bin[rr, cc] = True
        if self.mode == "draw":
            item.setBin(np.logical_or(item.bin(), bin))
        elif self.mode == "cut":
            item.setBin(np.logical_and(item.bin(), np.logical_not(bin)))
        elif self.mode == "catch":
            item.setBin(np.logical_and(item.bin(), bin))
        item.setDisplay()
        

class MaskPenPolygon(MaskPenFreehand):
    """Polygon region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)
        self.iconInSet = QIcon(icons.layer_shape_polygon)
        self.textInSet = 'Polygon'

    def hoverMoveEvent(self, event):
        if self.path is not None:
            self.path[-1] = [event.pos().x(), event.pos().y()]
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.update()
        super().hoverMoveEvent(event) 

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            position = [event.pos().x(), event.pos().y()]
            if self.path is None:
                self.path = [position, position]
            else:
                self.path[-1] = position
                self.path.append(position)

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if self.path is not None:
            self.path[-1] = [event.pos().x(), event.pos().y()]
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.update()
    
    def mouseDoubleClickEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.path is not None:
                item = self.scene().parent().maskItem
                if item is None:
                    return
                item.extend()
                self.path[-1] = [event.pos().x(), event.pos().y()]
                self.fillPath()
                #item = self.scene().parent().maskItem
                item.update()
                self.path = None


class MaskPenRectangle(MaskPenFreehand):
    """Rectangle region drawing tool.
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)
        self.iconInSet = QIcon(icons.layer_shape)
        self.textInSet = 'Rectangle'
        self.corner1 = None
        self.corner2 = None
        self.xc = None
        self.yc = None

    def initialize(self):
        # Called by the canvas after the filter is set to a scene
        # And when a new image is set to the scene
        item = self.scene().parent().imageItem
        if item is None:
            return
        set_attributes = False
        if self.xc is None:
            set_attributes = True
        elif self.xc.shape != item._array.shape:
            set_attributes = True
        if set_attributes:
            nx, ny = item._array.shape[0], item._array.shape[1]
            x, y = np.arange(0.5, 0.5+nx), np.arange(0.5, 0.5+ny)
            self.xc, self.yc = np.meshgrid(x, y, indexing='ij')

    def paint(self, painter, option, widget):
        if self.corner2 is None: 
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        x = [self.corner1[0], self.corner2[0]]
        y = [self.corner1[1], self.corner2[1]]
        rect = QRectF(min(x), min(y), max(x)-min(x), max(y)-min(y))
        painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            self.corner1 = [event.pos().x(), event.pos().y()]

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.corner2 = [event.pos().x(), event.pos().y()]
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.update()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.corner2 is not None:
                self.fillRect()
                self.corner1 = None
                self.corner2 = None

    def fillRect(self):
        item = self.scene().parent().maskItem
        if item is None:
            return
        x = [self.corner1[0], self.corner2[0]]
        y = [self.corner1[1], self.corner2[1]]
        rectx = np.logical_and(min(x) <= self.xc, self.xc <= max(x))
        recty = np.logical_and(min(y) <= self.yc, self.yc <= max(y))
        rect = np.logical_and(rectx, recty)
        if self.mode == "draw":
            item.setBin(np.logical_or(item.bin(), rect))
        elif self.mode == "cut":
            item.setBin(np.logical_and(item.bin(), np.logical_not(rect)))
        elif self.mode == "catch":
            item.setBin(np.logical_and(item.bin(), rect))
        item.setDisplay()


class MaskPenCircle(MaskPenFreehand):
    """Rectangle region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)
        self.iconInSet = QIcon(icons.layer_shape_ellipse)
        self.textInSet = 'Circle'
        self.center = None
        self.radius = None
        self.xc = None
        self.yc = None

    def initialize(self):
        # Called by the canvas after the filter is set to a scene
        # And when a new image is set to the scene
        item = self.scene().parent().imageItem
        if item is None:
            return
        set_attributes = False
        if self.xc is None:
            set_attributes = True
        elif self.xc.shape != item._array.shape:
            set_attributes = True
        if set_attributes:
            nx, ny = item._array.shape[0], item._array.shape[1]
            x, y = np.arange(0.5, 0.5+nx), np.arange(0.5, 0.5+ny)
            self.xc, self.yc = np.meshgrid(x, y, indexing='ij')

    def paint(self, painter, option, widget):
        if self.center is None: 
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        center = QPointF(self.center[0], self.center[1])
        painter.drawEllipse(center, self.radius, self.radius)

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            self.center = [event.pos().x(), event.pos().y()]
            self.radius = 0

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            dx = event.pos().x() - self.center[0]
            dy = event.pos().y() - self.center[1]
            self.radius = math.sqrt(dx**2 + dy**2)
            item.update()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.center is not None:
                self.fillCircle()
                self.center = None

    def fillCircle(self):
        item = self.scene().parent().maskItem
        if item is None:
            return
        d_sq = (self.xc-self.center[0])**2 + (self.yc-self.center[1])**2
        if self.mode == "draw":
            item.setBin(np.logical_or(item.bin(), d_sq <= self.radius**2))
        elif self.mode == "cut":
            item.setBin(np.logical_and(item.bin(), d_sq > self.radius**2))
        elif self.mode == "catch":
            item.setBin(np.logical_and(item.bin(), d_sq <= self.radius**2))
        item.setDisplay()


class MaskPenContour(MaskPenFreehand):
    """Rectangle region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)
        self.iconInSet = QIcon(icons.layer_shape_round)
        self.textInSet = 'Contour'
        self.contour = None

    def paint(self, painter, option, widget):
        if self.contour is None: 
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        position = self.contour[0,:]
        p1 = QPointF(position[0]+0.5, position[1]+0.5)
        n = self.contour.shape[0]
        for i in range(n)[1:]:
            position = self.contour[i,:]
            p2 = QPointF(position[0]+0.5, position[1]+0.5)
            painter.drawLine(p1, p2)
            p1 = p2
        position = self.contour[0,:]
        p2 = QPointF(position[0]+0.5, position[1]+0.5)
        painter.drawLine(p1, p2)

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            self.contour = self.findContour()
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            item.update()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.contour = self.findContour()
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.update()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.contour is not None:
                self.fillContour()
                self.contour = None

    def findContour(self):
        item = self.scene().parent().imageItem
        if item is None:
            return
        array = item._array
        nx, ny = array.shape
        if (self.x < 0) or (self.y < 0) or (self.x > nx-1) or (self.y > ny-1):
            return
        contours = skimage.measure.find_contours(array, level=array[self.x, self.y])
        # Extract only the contour that goes through the current position
        for contour in contours:
            n = contour.shape[0]
            for i in range(n):
                p = contour[i,:]
                if (p[0] == self.x) and (p[1] == self.y):
                    return contour

    def fillContour(self):
        item = self.scene().parent().maskItem
        if item is None:
            return
        bin = np.zeros(item.bin().shape, dtype=bool)
        rr, cc = skimage.draw.polygon(self.contour[:, 0], self.contour[:, 1], item.bin().shape)
        bin[rr, cc] = True
        if self.mode == "draw":
            item.setBin(np.logical_or(item.bin(), bin))
        elif self.mode == "cut":
            item.setBin(np.logical_and(item.bin(), np.logical_not(bin)))
        elif self.mode == "catch":
            item.setBin(np.logical_and(item.bin(), bin))
        item.setDisplay()


class MaskPenAllContours(MaskPenFreehand):
    """Rectangle region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)
        self.iconInSet = QIcon(icons.layer_shape_round)
        self.textInSet = 'All contours'
        self.contours = None

    def paint(self, painter, option, widget):
        if self.contours is None: 
            return
        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)
        for contour in self.contours:
            position = contour[0,:]
            p1 = QPointF(position[0]+0.5, position[1]+0.5)
            n = contour.shape[0]
            for i in range(n)[1:]:
                position = contour[i,:]
                p2 = QPointF(position[0]+0.5, position[1]+0.5)
                painter.drawLine(p1, p2)
                p1 = p2
            position = contour[0,:]
            p2 = QPointF(position[0]+0.5, position[1]+0.5)
            painter.drawLine(p1, p2)

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            self.contours = self.findContours()
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            item.update()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.contours = self.findContours()
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.update()

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.contours is not None:
                self.fillContours()
                self.contours = None

    def findContours(self):
        item = self.scene().parent().imageItem
        if item is None:
            return
        array = item._array
        nx, ny = array.shape
        if (self.x < 0) or (self.y < 0) or (self.x > nx-1) or (self.y > ny-1):
            return
        item = self.scene().parent().maskItem
        if item is None:
            return
        if item.bin() is None:
            return skimage.measure.find_contours(array, level=array[self.x, self.y])
        elif item.bin().any():
            return skimage.measure.find_contours(array, level=array[self.x, self.y], mask=item.bin())
        else:
            return skimage.measure.find_contours(array, level=array[self.x, self.y])

    def fillContours(self):
        item = self.scene().parent().maskItem
        if item is None:
            return
        bin = np.zeros(item.bin().shape, dtype=bool)
        for contour in self.contours:
            rr, cc = skimage.draw.polygon(contour[:, 0], contour[:, 1], item.bin().shape)
            bin[rr, cc] = True
        if self.mode == "draw":
            item.setBin(np.logical_or(item.bin(), bin))
        elif self.mode == "cut":
            item.setBin(np.logical_and(item.bin(), np.logical_not(bin)))
        elif self.mode == "catch":
            item.setBin(np.logical_and(item.bin(), bin))
        item.setDisplay()


class MaskThreshold(canvas.FilterItem):
    """Create mask by thresholding an image"""
    def __init__(self):
        super().__init__()
        pixMap = QPixmap(icons.controller_d_pad)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.toolTip = 'Threshold'
        self.text = 'Threshold'
        self.icon = QIcon(pixMap)
        self.setActionPick()

    def initialize(self):
        item = self.scene().parent().imageItem
        if item is None:
            return
        self.center, self.width = item._center, item._width
        self.array = item._array
        self.min = np.amin(self.array)
        self.max = np.amax(self.array)
        self.range = self.max-self.min
        #self.setData()

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.buttons()
        if button == Qt.LeftButton:
            d = event.screenPos() - event.lastScreenPos()
            self.window(d.x(), d.y())

    def mouseReleaseEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.update()

    def window(self, dx, dy):
        """Change intensity and contrast"""

        item = self.scene().parent().maskItem
        if item is None:
            return
       
        # Move 1024 to change the center over the full range
        # Speed is faster further away from the center of the range
        center = self.center 
        v0 = self.range/512
        a0 = 1.0/64
        vy = v0 + a0*abs((center - (self.min+self.range/2.0)))
        center = center - vy * dy
        self.center = center

        # Changing the width is faster at larger widths
        width = self.width
        v0 = self.range/512
        a0 = 1.0/64
        vx = v0 + a0*width
        width = width + vx * dx
        self.width = width if width>1 else 1

        # Update display
        min, max = self.center-self.width/2, self.center+self.width/2
        threshold = np.logical_and(min<=self.array, self.array<=max)
        item.setBin(threshold)
        item.setDisplay()


class MaskPaintByNumbers(MaskBrush):

    def setMode(self, mode):
        self.mode = mode
        if mode == "paint":
            pixMap = QPixmap(icons.paint_brush__plus)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Paint by numbers'
            self.text = 'Paint by numbers'
        elif mode == "erase":
            pixMap = QPixmap(icons.eraser__plus)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Erase by numbers'
            self.text = 'Erase by numbers'
        self.icon = QIcon(pixMap)

    def paintPixels(self):
        item = self.scene().parent().maskItem
        if item is None:
            return
        array = self.scene().parent().imageItem._array
        min = max = None 
        w = int((self.brushSize - 1)/2)
        for x in range(self.x-w, self.x+w+1, 1):
            if 0 <= x < item.bin().shape[0]:
                for y in range(self.y-w, self.y+w+1, 1):
                    if 0 <= y < item.bin().shape[1]:
                        #v = self.array[x,y]
                        v = array[x,y]
                        if min is None:
                            min = max = v
                        else:
                            if v < min:
                                min = v
                            if v > max:
                                max = v
        if min is None or max is None:
            return
        if self.mode == 'paint':
            #inrange = np.logical_and(min <= self.array, self.array <= max)
            inrange = np.logical_and(min <= array, array <= max)
            item.setBin(np.logical_or(item.bin(), inrange))
        else:
            #inrange = np.logical_or(self.array < min, max < self.array)
            inrange = np.logical_or(array < min, max < array)
            item.setBin(np.logical_and(item.bin(), inrange))
        item.setDisplay()


class MaskRegionGrowing(MaskBrush):

    def __init__(self, tolerance=5.0, mode='paint'):
        self.tolerance = tolerance
        super().__init__(mode=mode)

    def setMode(self, mode):
        self.mode = mode
        if mode == "paint":
            pixMap = QPixmap(icons.paint_brush__arrow)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Paint by growing..'
            self.text = 'Paint by growing..'
        elif mode == "erase":
            pixMap = QPixmap(icons.eraser__arrow)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Erase by growing..'
            self.text = 'Erase by growing..'
        self.icon = QIcon(pixMap)

    def paintPixels(self):
        # Get range of values under brush
        item = self.scene().parent().maskItem
        if item is None:
            return
        array = self.scene().parent().imageItem._array
        # Build a seed list of all pixels under the brush
        # and find minimum and maximum value over the seeds
        seed = []
        min = max = None 
        w = int((self.brushSize - 1)/2)
        for x in range(self.x-w, self.x+w+1, 1):
            if 0 <= x < item.bin().shape[0]:
                for y in range(self.y-w, self.y+w+1, 1):
                    if 0 <= y < item.bin().shape[1]:
                        seed.append([x,y])
                        #v = self.array[x,y]
                        v = array[x,y]
                        if min is None:
                            min = max = v
                        else:
                            if v < min:
                                min = v
                            elif v > max:
                                max = v
        if min is None or max is None:
            return
        # Find the range of values with the given tolerance
        center = (max+min)/2
        width = self.tolerance*(max-min)/2
        max, min = center+width, center-width
        # Grow region to include all pixels in the same range
        if self.mode == 'paint':
            canvas.utils.region_grow_add(array, item.bin(), seed, min, max)
        else:
            canvas.utils.region_grow_remove(array, item.bin(), seed, min, max)
        item.setDisplay()


    def setOptions(self, option):
        if 'tolerance' in option:
            self.tolerance = option['tolerance']
        elif 'size' in option:
            self.brushSize = option['size']
        self.pick()


    def menuOptions(self):
        menu = QMenu()
        menu.triggered.connect(lambda action: self.setOptions(action.option))

        actionGroup = QActionGroup(menu)
        options = {
            'Seed size: 1 pixel': 1,
            'Seed size: 3 pixels': 3,
            'Seed size: 5 pixels': 5,
            'Seed size: 7 pixels': 7,
            'Seed size: 9 pixels': 9,
            'Seed size: 11 pixels': 11,
            'Seed size: 21 pixels': 21,
            'Seed size: 31 pixels': 31,
        }
        for text, value in options.items():
            action = QAction(text)
            action.option = {'size': value}
            action.setCheckable(True)
            action.setChecked(value == self.brushSize)
            actionGroup.addAction(action)
            menu.addAction(action)

        self.addSeparator(menu)

        actionGroup = QActionGroup(menu)
        options = {
            'Tolerance: 1.0': 1.0,
            'Tolerance: 2.0': 2.0,
            'Tolerance: 3.0': 3.0,
            'Tolerance: 4.0': 4.0,
            'Tolerance: 5.0': 5.0,
            'Tolerance: 6.0': 6.0,
            'Tolerance: 7.0': 7.0,
            'Tolerance: 8.0': 8.0,
            'Tolerance: 9.0': 9.0,
            'Tolerance: 10.0': 10.0,
        }
        for text, value in options.items():
            action = QAction(text)
            action.option = {'tolerance': value}
            action.setCheckable(True)
            action.setChecked(value == self.tolerance)
            actionGroup.addAction(action)
            menu.addAction(action)

        return menu


class MaskDilate(canvas.FilterItem):
    """Dilate mask
    """
    def __init__(self, kernelSize=3):
        super().__init__()
        self.setKernel(kernelSize)
        self.mode = 'draw'
        pixMap = QPixmap(icons.arrow_out)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.toolTip = 'Dilate'
        self.text = 'Dilate'
        self.setActionPick()
        
    def setKernel(self, kernelSize):
        self.kernelSize = kernelSize
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.kernelSize, self.kernelSize))

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        item = self.scene().parent().maskItem
        if item is None:
            return
        if event.button() == Qt.LeftButton:
            bin = item.bin()
            if bin is None:
                return
            p = [self.x, self.y]
            if bin[p[0],p[1]]:
                bin = canvas.utils.dilate_cluster(bin, p, self.kernel, mode=self.mode)
                item.extend()
                item.setBin(bin)
                item.setDisplay()
        
    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())

    def setOptions(self, option):
        if 'size' in option:
            self.setKernel(option['size'])
        if 'mode' in option:
            self.mode = option['mode']
        self.pick()

    def menuOptions(self):
        menu = QMenu()
        menu.triggered.connect(lambda action: self.setOptions(action.option))

        actionGroup = QActionGroup(menu)
        options = {
            '3 pixels': 3,
            '5 pixels': 5,
            '7 pixels': 7,
            '9 pixels': 9,
            '11 pixels': 11,
            '21 pixels': 21,
            '31 pixels': 31,
        }
        for text, value in options.items():
            action = QAction(text)
            action.option = {'size': value}
            action.setCheckable(True)
            action.setChecked(value == self.kernelSize)
            actionGroup.addAction(action)
            menu.addAction(action)

        self.addSeparator(menu)

        actionGroup = QActionGroup(menu)
        options = {
            'Draw': 'draw',
            'Cut': 'cut',
            'Rescue': 'rescue',
        }
        icon = [
            QIcon(icons.pencil), 
            QIcon(icons.cutter), 
            QIcon(icons.lifebuoy),
        ]
        i=0
        for text, value in options.items():
            action = QAction(text)
            action.option = {'mode': value}
            action.setCheckable(True)
            action.setChecked(value == self.mode)
            action.setIcon(icon[i])
            i+=1
            actionGroup.addAction(action)
            menu.addAction(action)

        return menu

    def contextMenu(self):
        return self.actionPick.menu()


class MaskShrink(MaskDilate):
    """Erode Button
    """
    def __init__(self, kernelSize=3):
        super().__init__(kernelSize=kernelSize)
        pixMap = QPixmap(icons.arrow_in)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.toolTip = 'Shrink'
        self.text = 'Shrink'
        self.setActionPick()

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        item = self.scene().parent().maskItem
        if item is None:
            return
        if event.button() == Qt.LeftButton:
            bin = item.bin()
            if bin is None:
                return
            p = [self.x, self.y]
            if bin[p[0],p[1]]:
                bin = canvas.utils.erode_cluster(bin, p, self.kernel, mode=self.mode)
                item.extend()
                item.setBin(bin)
                item.setDisplay()


class MaskOpen(MaskDilate):
    """
    Open Button (remove bright spots)
    """
    def __init__(self, kernelSize=3):
        super().__init__(kernelSize=kernelSize)
        pixMap = QPixmap(icons.minus_small_circle)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.toolTip = 'Remove bright spots'
        self.text = 'Remove bright spots'
        self.setActionPick()

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        item = self.scene().parent().maskItem
        if item is None:
            return
        if event.button() == Qt.LeftButton:
            bin = item.bin()
            p = [self.x, self.y]
            if bin is None:
                if self.mode == 'draw':
                    bin = self._grow_from(p)
                    self._open(p, bin)
            else:
                if bin[p[0],p[1]]:
                    self._open(p, bin, split=True)
                elif self.mode == 'draw':
                    cluster = self._grow_from(p)
                    cluster = canvas.utils.open_cluster(cluster, p, self.kernel, mode=self.mode)
                    bin = np.logical_or(bin, cluster.astype(np.bool8))
                    item = self.scene().parent().maskItem
                    if item is None:
                        return
                    item.extend()
                    item.setBin(bin)
                    item.setDisplay()

    def _grow_from(self, p):
        item = self.scene().parent().imageItem
        if item is None:
            return
        array = item._array
        return canvas.utils.pick_cluster(array, p)

    def _open(self, p, bin, split=False):
        if np.count_nonzero(bin) > 0:
            bin = canvas.utils.open_cluster(bin, p, self.kernel, mode=self.mode, split=split)
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            item.setBin(bin)
            item.setDisplay()
            

class MaskClose(MaskDilate):
    """
    Close Button (remove dark spots)
    """
    def __init__(self, kernelSize=3):
        super().__init__(kernelSize=kernelSize)
        pixMap = QPixmap(icons.plus_small_white)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=8, hotY=8)
        self.toolTip = 'Remove dark spots'
        self.text = 'Remove dark spots'
        self.setActionPick()

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        item = self.scene().parent().maskItem
        if item is None:
            return
        if event.button() == Qt.LeftButton:
            bin = item.bin()
            p = [self.x, self.y]
            if bin is None:
                if self.mode == 'draw':
                    bin = self._grow_from(p)
                    self._close(p, bin)
            else:
                if bin[p[0],p[1]]:
                    self._close(p, bin)
                elif self.mode == 'draw':
                    cluster = self._grow_from(p)
                    cluster = canvas.utils.close_cluster(cluster, p, self.kernel, mode=self.mode)
                    bin = np.logical_or(bin, cluster.astype(np.bool8))
                    item = self.scene().parent().maskItem
                    if item is None:
                        return
                    item.extend()
                    item.setBin(bin)
                    item.setDisplay()

    def _grow_from(self, p):
        item = self.scene().parent().imageItem
        if item is None:
            return
        array = item._array
        return canvas.utils.pick_cluster(array, p)

    def _close(self, p, bin):
        if np.count_nonzero(bin) > 0:
            item = self.scene().parent().maskItem
            if item is None:
                return
            bin = canvas.utils.close_cluster(bin, p, self.kernel, mode=self.mode)
            item.extend()
            item.setBin(bin)
            item.setDisplay()


class MaskWand(canvas.FilterItem):
    """
    Close then open
    """
    def __init__(self, brightKernelSize=1, darkKernelSize=1):
        super().__init__()
        self.setBrightKernel(brightKernelSize)
        self.setDarkKernel(darkKernelSize)
        self.mode = 'draw'
        pixMap = QPixmap(icons.wand)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=0, hotY=16)
        self.toolTip = 'Remove spots'
        self.text = 'Remove spots'
        self.setActionPick()

    def setDarkKernel(self, kernelSize):
        self.darkKernelSize = kernelSize
        if kernelSize == 1:
            self.darkKernel = None
        else:
            self.darkKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernelSize, kernelSize))

    def setBrightKernel(self, kernelSize):
        self.brightKernelSize = kernelSize
        if kernelSize == 1:
            self.brightKernel = None
        else:
            self.brightKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernelSize, kernelSize))

    def setOptions(self, option):
        if 'dark size' in option:
            self.setDarkKernel(option['dark size'])
        elif 'bright size' in option:
            self.setBrightKernel(option['bright size'])
        elif 'mode' in option:
            self.mode = option['mode']
        self.pick()

    def menuOptions(self):
        menu = QMenu()
        menu.triggered.connect(lambda action: self.setOptions(action.option))

        actionGroup = QActionGroup(menu)
        options = {
            'Do not remove dark spots': 1,
            'Remove dark spots less than 3 pixels': 3,
            'Remove dark spots less than 5 pixels': 5,
            'Remove dark spots less than 7 pixels': 7,
            'Remove dark spots less than 9 pixels': 9,
            'Remove dark spots less than 11 pixels': 11,
            'Remove dark spots less than 21 pixels': 21,
            'Remove dark spots less than 31 pixels': 31,
        }
        for text, value in options.items():
            action = QAction(text)
            action.option = {'dark size': value}
            action.setCheckable(True)
            action.setChecked(value == self.darkKernelSize)
            actionGroup.addAction(action)
            menu.addAction(action)

        self.addSeparator(menu)

        actionGroup = QActionGroup(menu)
        options = {
            'Do not remove bright spots': 1,
            'Remove bright spots less than 3 pixels': 3,
            'Remove bright spots less than 5 pixels': 5,
            'Remove bright spots less than 7 pixels': 7,
            'Remove bright spots less than 9 pixels': 9,
            'Remove bright spots less than 11 pixels': 11,
            'Remove bright spots less than 21 pixels': 21,
            'Remove bright spots less than 31 pixels': 31,
        }
        for text, value in options.items():
            action = QAction(text)
            action.option = {'bright size': value}
            action.setCheckable(True)
            action.setChecked(value == self.brightKernelSize)
            actionGroup.addAction(action)
            menu.addAction(action)

        self.addSeparator(menu)

        actionGroup = QActionGroup(menu)
        options = {
            'Draw': 'draw',
            'Cut': 'cut',
            'Rescue': 'rescue',
        }
        icon = [
            QIcon(icons.pencil), 
            QIcon(icons.cutter), 
            QIcon(icons.lifebuoy),
        ]
        i=0
        for text, value in options.items():
            action = QAction(text)
            action.option = {'mode': value}
            action.setCheckable(True)
            action.setChecked(value == self.mode)
            action.setIcon(icon[i])
            i+=1
            actionGroup.addAction(action)
            menu.addAction(action)

        return menu

    def contextMenu(self):
        return self.actionPick.menu()

    def mouseMoveEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())

    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        item = self.scene().parent().maskItem
        if item is None:
            return
        if event.button() == Qt.LeftButton:
            bin = item.bin()
            p = [self.x, self.y]
            if bin is None:
                if self.mode == 'draw':
                    bin = self._grow_from(p)
                    self._close_open(p, bin)
            else:
                if bin[p[0],p[1]]:
                    self._close_open(p, bin, split=True)
                elif self.mode == 'draw':
                    cluster = self._grow_from(p)
                    cluster = canvas.utils.open_cluster(cluster, p, self.brightKernel, mode=self.mode)
                    cluster = canvas.utils.close_cluster(cluster, p, self.darkKernel, mode=self.mode)
                    bin = np.logical_or(bin, cluster.astype(np.bool8))
                    item = self.scene().parent().maskItem
                    if item is None:
                        return
                    item.extend()
                    item.setBin(bin)
                    item.setDisplay()

    def _grow_from(self, p):
        item = self.scene().parent().imageItem
        if item is None:
            return
        array = item._array
        return canvas.utils.pick_cluster(array, p)

    def _close_open(self, p, bin, split=False):
        if np.count_nonzero(bin) > 0:
            bin = canvas.utils.open_cluster(bin, p, self.brightKernel, mode=self.mode, split=split)
            bin = canvas.utils.close_cluster(bin, p, self.darkKernel, mode=self.mode)
            item = self.scene().parent().maskItem
            if item is None:
                return
            item.extend()
            item.setBin(bin)
            item.setDisplay()         


class MaskKidneyEdgeDetection(canvas.FilterItem):

    def __init__(self):
        super().__init__()
        pixMap = QPixmap(icons.wand)
        self.icon = QIcon(pixMap)
        self.cursor = QCursor(pixMap, hotX=0, hotY=16)
        self.toolTip = 'Pick a kidney'
        self.text = 'Kidney picker'
        self.setActionPick()


    def mousePressEvent(self, event):
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            cnvs = self.scene().parent()
            if cnvs.imageItem is None:
                return
            array = cnvs.imageItem._array
            item = cnvs.maskItem
            if item is None:
                return
            pixelSize = cnvs.parent().sliders.image.PixelSpacing # Hack!!! Some filters need access to geometry!
            pixels = canvas.utils.kidneySegmentation(array, self.y, self.x, pixelSize)
            if pixels is not None:
                item.extend()
                item.setBin(np.logical_or(item.bin(), pixels.astype(np.bool8)))
                item.setDisplay()

