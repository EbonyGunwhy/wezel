from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import (
    QWidget, 
    QMainWindow, 
    QAction, 
    QMenu, 
    QMenuBar, 
    QDockWidget, 
    QMessageBox) 
from PySide2.QtGui import QIcon

import dbdicom as db
import wezel
import sys


# Examples of style sheets
# https://doc.qt.io/qtforpython/overviews/stylesheet-examples.html
# 



STYLESHEET = """
    QWidget {
        background-color: #1E1E1E;
        color: #DCDCDC;
    }

    QMenuBar {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenuBar::item {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenu {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenu::item {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QTabWidget {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QTabWidget::pane {
        border: 1px solid #3F3F3F;
        background-color: #2C2C2C;
    }

    QTabWidget::tab-bar {
        left: 5px; /* move to the right by 5px */
    }

    QTabBar::tab {
        background-color: #2C2C2C;
        color: #DCDCDC;
        padding: 5px;
        border: 1px solid #3F3F3F;
        border-bottom-color: #2C2C2C; /* same as pane color */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    QTabBar::tab:selected {
        background-color: #3F3F3F;
    }

    """


SMALLSTYLESHEET = """

    QMenuBar {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenuBar::item {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenu {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QMenu::item {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QTabWidget {
        background-color: #2C2C2C;
        color: #DCDCDC;
    }

    QTabWidget::pane {
        border: 1px solid #3F3F3F;
        background-color: #2C2C2C;
    }

    QTabWidget::tab-bar {
        left: 5px; /* move to the right by 5px */
    }

    QTabBar::tab {
        background-color: #2C2C2C;
        color: #DCDCDC;
        padding: 5px;
        border: 1px solid #3F3F3F;
        border-bottom-color: #2C2C2C; /* same as pane color */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }

    QTabBar::tab:selected {
        background-color: #3F3F3F;
    }

    """


class Main(QMainWindow):

    def __init__(self, wzl, project=None): 
        """
        Initialize the Wezel class and its attributes.
        
        Parameters:
            wzl (object): An instance of the wezel class.
        
        Attributes:
            wezel (object): An instance of the wezel class, passed as an argument.
            dialog (object): An instance of the Dialog class from the wezel.widgets module.
            status (object): An instance of the StatusBar class from the wezel.widgets module.
            toolBar (dict): A dictionary to store the toolbar widgets.
            toolBarDockWidget (QDockWidget): A QDockWidget instance to hold the toolbar.
            treeView (None): Placeholder for the treeview widget.
            treeViewDockWidget (QDockWidget): A QDockWidget instance to hold the treeview.
            folder (None): Placeholder for the folder widget.
            central (object): An instance of the MainMultipleDocumentInterface class from the wezel.widgets module.
        """

        super().__init__()
        self.wezel = wzl
        #self.setStyleSheet(SMALLSTYLESHEET)
        title = "  Wezel"
        if project is not None:
            title += ' -- project ' + project
        self.setWindowTitle(title)
        
        # self.offset = None
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        # self.setMouseTracking(True)

        self.dialog = wezel.widgets.Dialog(self)
        self.status = wezel.widgets.StatusBar()
        self.setStatusBar(self.status)

        self.toolBar = {}
        self.toolBarDockWidget = QDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.toolBarDockWidget)
        self.toolBarDockWidget.hide()

        self.treeView = None
        self.treeViewDockWidget = QDockWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.treeViewDockWidget)
        self.treeViewDockWidget.hide()

        self.central = wezel.widgets.MainMultipleDocumentInterface()
        self.central.subWindowActivated.connect(lambda subWindow: self.activateSubWindow(subWindow))
        self.setCentralWidget(self.central)


    # def mousePressEvent(self, event):
    #     self.offset = event.pos()

    # def mouseMoveEvent(self, event):
    #     if self.offset is not None:
    #         x=event.globalX()
    #         y=event.globalY()
    #         x_w = self.offset.x()
    #         y_w = self.offset.y()
    #         self.move(x-x_w, y-y_w)

    # def mouseReleaseEvent(self, event):
    #     self.offset is None
        
    # def resizeEvent(self, event):
    #     # add 8px padding on each side
    #     self.setContentsMargins(8, 8, 8, 8)
    #     super().resizeEvent(event)

    def closeEvent(self, event): #main
        accept = self.close()
        if accept:
            event.accept()
        else:
            event.ignore()

    def open(self, path):
        folder = db.database(path=path, 
            status = self.status, 
            dialog = self.dialog)
        self.display(folder)
        self.status.hide()


    def close(self):
        """Closes the application."""
        if self.database() is None:
            return True
        accept = self.database().close()
        if accept:
            self.toolBarDockWidget.hide()
            self.treeViewDockWidget.hide()
            for subWindow in self.central.subWindowList():
                self.central.removeSubWindow(subWindow)
            self.menuBar().enable()
        return accept

    def refresh(self):
        """
        Refreshes the Wezel display.
        """
        self.status.message('Refreshing display..')
        if self.treeView is not None:
            self.treeView.setDatabase()
        self.menuBar().enable()
        self.status.hide()
        
    def display(self, object):
        if isinstance(object, list):
            for o in object:
                self.display(o)
            return
        if object is None:
            self.dialog.information('There are no data to show here')
            return
        if object.type() == 'Database':
            self.treeView = wezel.widgets.DICOMFolderTree(object)
            self.treeView.itemSelectionChanged.connect(self.menuBar().enable)
            self.treeViewDockWidget.setWidget(self.treeView)
            self.treeViewDockWidget.show()
            self.menuBar().enable()
        elif object.type() == 'Patient': # No Patient Viewer yet
            pass
        elif object.type() == 'Study': # No Study Viewer yet
            pass
        elif object.type() == 'Series':
            viewer = wezel.displays.SeriesDisplay(object)
            self.addWidget(viewer, title=object.label())
        elif object.type() == 'Instance':
            pass

    # THIS WILL BE DEPRECATED!! 
    # Included for backwards compatibility only.
    @property
    def folder(self):
        return self.database()

    # THIS WILL BE DEPRECATED!!
    # Use selected()
    def get_selected(self, generation):  
        if self.treeView is None: 
            return []
        return self.treeView.get_selected(generation)

    # Retrieve the selected database
    def database(self):
        databases = self.selected('Databases')
        if databases == []:
            return 
        else:
            return databases[0]   

    def top_level_selected(self):
        patients = self.selected('Patients')
        studies = self.selected('Studies')
        series = self.selected('Series')
        sel = patients + studies + series
        if sel == []:     
            return
        tl_patients = []
        tl_studies = []
        tl_series = []
        for patient in self.database().patients():
            if patient in patients:
                tl_patients.append(patient)
            else:
                for study in patient.studies():
                    if study in studies:
                        tl_studies.append(study)
                    else:
                        for sery in study.series():
                            if sery in series:
                                tl_series.append(sery)
        return tl_patients, tl_studies, tl_series
             

    def selected(self, generation='Series'):
        """Returns a list of selected objects of the requested generation"""

        # Check if any databases are open
        if self.treeView is None: 
            return []

        # If an object is selected in the treeView, use that.
        if generation == 'Databases':
            return [self.treeView.database()]
        sel = self.treeView.selected(generation)
        if sel != []:
            return sel

        # If none are selected in the database, check the display.
        activeWindow = self.central.activeWindow
        if activeWindow is None:
            return []
        widget = activeWindow.widget()
        if generation=='Instances':
            if hasattr(widget, 'instance'):
                return [widget.instance()]
        elif generation=='Series':
            if hasattr(widget, 'series'):
                return [widget.series()] 
        elif generation=='Studies':
            if hasattr(widget, 'study'):
                return [widget.study()]
        elif generation=='Patients':
            if hasattr(widget, 'patient'):
                return [widget.patient()]
        elif generation=='Databases':
            if hasattr(widget, 'database'):
                return [widget.database()]
        return []
        
 
    def nr_selected(self, generation):
        if self.treeView is None: 
            return 0
        nr = self.treeView.nr_selected(generation)
        if nr != 0:
            return nr
        activeWindow = self.central.activeWindow
        if activeWindow is None:
            return 0
        widget = activeWindow.widget()
        if generation=='Instances':
            if hasattr(widget, 'instance'):
                return 1
        elif generation=='Series':
            if hasattr(widget, 'series'):
                return 1
        elif generation=='Studies':
            if hasattr(widget, 'study'):
                return 1
        elif generation=='Patients':
            if hasattr(widget, 'patient'):
                return 1
        elif generation=='Databases':
            if hasattr(widget, 'database'):
                return 1
        return 0
        

    def closeSubWindow(self, subWindow):
        self.central.removeSubWindow(subWindow)
        self.central.tileSubWindows()
        # The widget continues to exist - memory issues?
        # Delete widget when subwindow closes
        widget = subWindow.widget().__class__.__name__
        # Hack
        # The widget is sometimes destroyed by removeSubWindow but not always - not sure why
        if widget == 'QWidget':
            return
        if 0 == self.central.countSubWindow(widget):
            toolBar = subWindow.widget().toolBar
            if toolBar is not None:
                toolBar.setEnabled(False)
            #self.toolBarDockWidget.hide()
        #self.refresh()


    def activateSubWindow(self, subWindow):
        if self.central.activeWindow == subWindow:
            return
        activeWindow = self.central.activeWindow
        if activeWindow is not None:
            activeWindow.widget().setActive(False)
        self.central.activeWindow = subWindow
        if subWindow is not None:
            subWindow.widget().setActive(True)
            # If the main widget has a toolbar, set its state
            # add it as a dockwidget.
            toolBar = subWindow.widget().toolBar
            if toolBar is not None:
                subWindow.widget().setToolBarState()
                self.toolBarDockWidget.setWidget(toolBar)


    def addWidget(self, widget, title):
        # rename to addSubWindow()
        # widget needs to be subclassed from MainWidget
        if widget.error:
            return
        subWindow = self.central.addWidget(widget, title)
        subWindow.closed.connect(lambda: self.closeSubWindow(subWindow))
        self.central.tileSubWindows()
        widget.databaseUpdated.connect(self.refresh)
        # If the right kind of toolbar does not exist yet, create it and show it
        # If it does exist juts set it as current.
        if widget.toolBarClass is not None:
            toolBarName =  widget.toolBarClass.__name__
            if toolBarName in self.toolBar:
                toolBar = self.toolBar[toolBarName]
                self.toolBarDockWidget.setWidget(toolBar)
                widget.setToolBar(toolBar)
            else:
                toolBar =  widget.toolBarClass()
                self.toolBar[toolBarName] = toolBar
                self.toolBarDockWidget.setWidget(toolBar)
                widget.setToolBar(toolBar)
                self.toolBarDockWidget.show()
        self.menuBar().enable() # added


class MainWidget(QWidget):
    """Base class for widgets that are set as subWindow widgets"""

    databaseUpdated = Signal() 

    def __init__(self):
        super().__init__()
        self.toolBarClass = None
        self.toolBar = None
        self.error = False

    def setError(self, message='Error displaying data!!'):
        self.error = True
        QMessageBox.information(self, 'Information', message)

    def setToolBar(self, toolBar):
        self.toolBar = toolBar
        self.setToolBarState()

    def setToolBarState(self):
        self.toolBar.setWidget(self)
        self.toolBar.setEnabled(True)
        
    def setActive(self, active):
        pass
        # If the window is activated, set its toolbar
        # to the toolbar dockwidget
        # if active:
        #     if self.toolBar is not None:
        #         self.setToolBarState()
        #         subWindow = self.parentWidget()
        #         mdiArea = subWindow.mdiArea()
        #         mainWindow = mdiArea.parentWidget()
        #         mainWindow.toolBarDockWidget.setWidget(self.toolBar)
                
    def closeEvent(self, event):
        pass



class MenuBar(QMenuBar):
    def __init__(self, *args):
        self._menus = list(args)

    def menus(self):
        return self._menus

    def add(self, menu, position=None):
        if position is None:
            position = len(self._menus)
        self._menus.insert(position, menu)

    def add_menu(self, title='Menu'):
        menu = Menu(title)
        self.add(menu)
        return menu

    def setupUI(self, app):
        try:
            super().__init__()
        except:
            return
        for menu in self._menus:
            menu.setupUI(app)
            self.addMenu(menu)
        self.enable()
        
        # On Mac - use toolbar on window to resolve installer issues
        if sys.platform == 'darwin':
            self.setNativeMenuBar(False)
            self.show()

    def enable(self):
        for menu in self._menus:
            menu.enable()



class Menu(QMenu):

    def __init__(self, title='Menu'):
        self.app = None
        self._title = title
        self._items = []

    def title(self):
        return self._title
    
    def set_title(self, title):
        self._title = title

    def setupUI(self, app):
        try:
            super().__init__()
        except:
            # Do nothing if the object is already set up
            return
        self.setTitle(self._title)
        for item in self._items:
            if isinstance(item, Action):
                item.setupUI(app)
                self.addAction(item)
            elif isinstance(item, Menu):
                item.setupUI(app)
                self.addMenu(item)
            elif isinstance(item, Separator):
                self.addSeparator()

    def add(self, item, position=None, text=None):
        if text is not None:
            if isinstance(item, Action):
                item.set_text(text)
            elif isinstance(item, Menu):
                item.set_title(text)  
            elif isinstance(item, Separator):
                pass
        if position is None:
            position = len(self._items)
        self._items.insert(position, item)

    def add_action(self, *args, **kwargs):
        action = Action(*args, **kwargs)
        self.add(action)

    def add_menu(self, *args, **kwargs):
        menu = Menu(*args, **kwargs)
        self.add(menu)
        return menu

    def add_separator(self, **kwargs):
        sep = Separator()
        self.add(sep, **kwargs)

    def enable(self):
        for item in self._items:
            if isinstance(item, Action):
                enable = item.enable()
                item.setEnabled(enable)
            elif isinstance(item, Menu):
                item.enable()


class Action(QAction):
    def __init__(self, 
            text = 'Action',
            shortcut = None,
            tooltip = None, 
            icon = None, 
            on_clicked = None,
            is_clickable = None):

        self._app = None
        self._text = text
        self._shortcut = shortcut
        self._tooltip = tooltip
        self._icon = icon
        self._on_clicked = on_clicked
        self._is_clickable = is_clickable

    def set_text(self, text):
        self._text = text
        
    def setupUI(self, app):
        try:
            super().__init__()
        except:
            return
        self._app = app
        self.triggered.connect(self._run)
        self.setText(self._text)
        if self._icon is not None: 
            self.setIcon(QIcon(self._icon))
        if self._shortcut is not None: 
            self.setShortcut(self._shortcut)
        if self._tooltip is not None: 
            self.setToolTip(self._tooltip)
        
    def _run(self):
        if self._on_clicked is not None:
            try:
                self._on_clicked(self._app)
            # except ValueError as e:
            #     # If the user has selected a wrong value, inform them
            #     self._app.dialog.information(str(e))
            except:
                # Any other error - report as bug
                self._app.dialog.error()
                self._app.refresh()
        self._app.status.hide()
        self._app.status.message('Ready for your next move.. Give it to me!')

    def enable(self):
        if self._is_clickable is not None:
            return self._is_clickable(self._app)
        else:
            return True
        

class Separator:
    pass
