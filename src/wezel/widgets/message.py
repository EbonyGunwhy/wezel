import traceback

from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor, QPixmap
from PySide2.QtWidgets import (    
    QApplication,                          
    QStatusBar, 
    QProgressBar, 
    QFileDialog, 
    QMessageBox, 
    QMessageBox, 
)

from wezel import icons, widgets


class Dialog():

    def __init__(self, parent=None):

        self.parent = parent

    def information(self, message="Message in the box", title="Information"):
        """
        Information message. Press 'OK' to continue.
        """
        QMessageBox.information(self.parent, title, message)

    def warning(self, message="Message in the box", title="Warning"):
        """
        Warning message. Press 'OK' to continue.
        """
        QMessageBox.warning(self.parent, title, message)

    def error(self, title=None, message=None, detail=None):
        """
        Error message. Press 'OK' to continue.
        """
        if title is None:
            title = "  Oops..."
        if message is None:
            message = 'Congratulations!!! You found a bug!\n'
        if detail is None:
            detail = 'Please email the detail below to a wezel developer \n'
            detail += 'and briefly explain what you did just before this happened.\n'
            detail += 'They will let you know when the bug has been squashed. \n'
        msg = QMessageBox()
        msg.setIconPixmap(QPixmap(icons.bug))
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setInformativeText(detail)
        msg.setDetailedText(traceback.format_exc())
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_() # value of pressed message box button

    def directory(self, message='Please select a folder', datafolder=None):
        """
        Select a directory.
        """
        return QFileDialog.getExistingDirectory(
            parent = self.parent, 
            caption = message, 
            directory = datafolder, 
            options = QFileDialog.ShowDirsOnly)

    def files(self, 
        title = 'Select files..', 
        initial_folder = None, 
        extension = "All files (*.*)"):
        """
        Select a file to read.
        """
        # dialog = QFileDialog()
        # dialog.setFileMode(QFileDialog.ExistingFiles)
        # #dialog.setNameFilter("Images (*.png *.xpm *.jpg)")
        # dialog.exec_()
        # return dialog.selectedFiles()
        # This selects files only - ideally want to select files and directories
        # This may be a solution 
        # https://stackoverflow.com/questions/6484793/multiple-files-and-folder-selection-in-a-qfiledialog
        names, _ = QFileDialog.getOpenFileNames(None, title, initial_folder, extension)
        return names

    def question(self, message="Do you wish to proceed?", title="Question for the user", cancel=False):
        """
        Displays a question window in the User Interface.
        
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        Returns False if reply is "Cancel" and True if reply is "OK".
        """
        if cancel:
            reply = QMessageBox.question(
                self.parent, title, message,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, 
                QMessageBox.No)
        else:
            reply = QMessageBox.question(
                self.parent, title, message,
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)
        if reply == QMessageBox.Yes: return "Yes"
        elif reply == QMessageBox.No: return "No"
        elif reply == QMessageBox.Cancel: return "Cancel"

    def file_to_open(self, 
        title = 'Open file..', 
        initial_folder = None, 
        extension = "All files (*.*)", 
        datafolder = None):
        """
        Select a file to read.
        """
        if initial_folder is None:
            initial_folder = datafolder
        filename, _ = QFileDialog.getOpenFileName(title, initial_folder, extension)
        if filename == '': 
            return None
        return filename

    def file_to_save(self, title='Save as ...', directory=None, filter="All files (*.*)", datafolder=None):
        """
        Select a filename to save.
        """
        if directory is None:
            directory = datafolder
        filename, _ = QFileDialog.getSaveFileName(caption=title, directory=directory, filter=filter)
        if filename == '': return None
        return filename

    def input(self, *fields, title="User input window", helpText=""):
        """
        Collect user input of various types.
        """
        input = widgets.UserInput(*fields, title=title, helpText=helpText)
        return input.cancel, input.values
        #return dialog.button=='Cancel', dialog.returnListParameterValues()


class StatusBar(QStatusBar):

    def __init__(self):
        super().__init__()

        self.progressBar = QProgressBar()
        self.progressBar.setFixedHeight(10)
        self.addPermanentWidget(self.progressBar)
        self.hide()

    def hide(self):

        self.message('')
        self.progressBar.hide()
        QApplication.processEvents() # allow gui to update

    def message(self, message=None):

        if message == None: 
            message = ''
        self.showMessage(message)
        QApplication.processEvents() # allow gui to update

    def progress(self, value, total, message=None):

        if message is not None: 
            self.message(message)
        if total > 1:
            self.progressBar.show()
            self.progressBar.setRange(0, total)
            self.progressBar.setValue(value)
        else:
            self.progressBar.hide()
        QApplication.processEvents() # allow gui to update - prevent freezing

    def cursorToHourglass(self):
        """
        Turns the arrow shape for the cursor into an hourglass. 
        """   
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    def cursorToNormal(self):
        """
        Restores the cursor into an arrow after it was set to hourglass 
        """   
        QApplication.restoreOverrideCursor() 

    def pixelValue(self, x, y, array):
        text = ""
        if array is not None:
            if 0 <= x < array.shape[0]:
                if 0 <= y < array.shape[1]:
                    pixelValue = array[x,y]
                    text = "Signal ({}, {}) = {}".format(x, y, pixelValue)
        self.message(text)



