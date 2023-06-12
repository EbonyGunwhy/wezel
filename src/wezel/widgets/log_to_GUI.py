"""
This module contains classes for the creation of a widget to display status updates
on the GUI from a calculation running in its own thread.
"""
import sys
import datetime
import traceback
from PySide2.QtCore import (QObject, QRunnable, QThreadPool, Signal, Slot)
from PySide2.QtWidgets import (QVBoxLayout, QWidget, QPlainTextEdit)

import wezel
import time
import numpy as np
import os


class WorkerSignals(QObject):
      """
      Defines the signals available from a running worker thread.
      Supported signals are:
          finished - No data
          error - tuple (exctype, value, traceback.format_exc() )
          result - object data returned from processing, anything
          progress - int indicating % progress
          log - string containing the status of the calculation

      An object instanciated from this class must be passed into the 
      callback function, so that it can communicate with the GUI.
      """
      finished = Signal()
      error = Signal(tuple)
      result = Signal(object)
      progress = Signal(int)
      log = Signal(str)


class Worker(QRunnable):
      """
      This class allows a long-running calculation to run in its own thread, 
      the Worker thread, separate from the thread that the GUI is run in.

      Threads run in the same memory space, Processes run in a separate memory space.
      
      The function containing the long-running calculation is passed as an object
      into this class's object constructor.

      Thus, during the calculation, status updates can be made to the GUI without
      causing it to freeze. 

      It inherits from QRunnable to handle worker thread setup, signals and
      wrap-up.
        
      Input arguments:
      ****************
      func: The callback function containing a long-running calculation as an object. 
      args: arguments to pass to the callback function
      kwargs: Keyword arguments to pass to the callback function
      """
      def __init__(self, func, *args, **kwargs):
          super().__init__()
          self._func = func
          self.args = args
          self.signals = WorkerSignals()
          # Add the signals object to the kwargs
          kwargs["signals"] = self.signals
          self.kwargs = kwargs
          

      @Slot()
      def run(self):
          """
          Executes the function passed into the Worker object 
          and communicates messages from within this function 
          to the GUI.
          """
          try:
            result = self._func(*self.args, **self.kwargs)
          except Exception:
              traceback.print_exc()
              exctype, value = sys.exc_info()[:2]
              self.signals.error.emit((exctype, value, traceback.format_exc()))
          else:
              self.signals.result.emit(result) # Return the result of the calculation
          finally:
              self.signals.finished.emit() # Finished


class LoggingWidget(QWidget):
    """
    This class creates a custom composite widget that displays status updates
    from the callback function in a plain text textbox.  

    Additionally, it creates a thread for the callback function to run in.

    Input arguments:
    ****************
      func: The callback function containing a long-running calculation as an object. 
      args: arguments to pass to the callback function
      kwargs: Keyword arguments to pass to the callback function
    """
    def __init__(self, func, *args, **kwargs):
          super().__init__()
          self._function = func
          self.args = args
          self.kwargs = kwargs
          layout = QVBoxLayout()
          self.displayLogs = QPlainTextEdit()
          self.displayLogs.setReadOnly(True)
          layout.addWidget(self.displayLogs)
          self.setLayout(layout)
          self.threadpool = QThreadPool()
          #Comment out the next line of code if you wish to trigger
          #execution of the callback function by a button press on the GUI
          self.executeFunction()  


    def executeFunction(self):
        """
        This function sets up a Worker object to run the callback function and
        starts it running in it's own thread. 

        Additionally, it sets up communication of status from the callback function
        to the plain text textbox in the GUI thread.

        Connect this function to the  clicked() signal of a QPushButton if you wish to
        start with calculation with the click of a  button on the GUI.
        """
        worker = Worker(self._function, *self.args, **self.kwargs)
        worker.signals.log.connect(self.logProgress)
        worker.signals.result.connect(self.logResult)
        worker.signals.finished.connect(self.logFinished)
        worker.signals.progress.connect(self.logProgress)
        # Start the calculation in its own thread
        self.threadpool.start(worker)
          

    def logProgress(self, text):
        self.displayLogs.appendPlainText(str(datetime.datetime.now())[:19] + ': ' + text)


    def logResult(self, text):
        self.displayLogs.appendPlainText(str(datetime.datetime.now())[:19] + ': ' + text)


    def logFinished(self):
        self.displayLogs.appendPlainText(str(datetime.datetime.now())[:19] + ': ' + "Finished")



def test_Function(start, end, signals):
  signals.log.emit("Calculation Started")
  for n in range(start, end):
    time.sleep(1)
    signals.log.emit("Message " + str(n))  
  return "Result of the calculation"


def test_Copy(series_list, signals):
    signals.log.emit("Copying {} series".format(len(series_list)))      
    for series in series_list:
        signals.log.emit('Copying {}'.format(series.label()))
        series.copy()  
    return "Copying complete"


def test_export(series, path,signals):
    signals.log.emit("Start exporting series")
    for s in series:
        signals.log.emit("Exporting {} series to {}".format(s.label(), path))
        s.export(path)
    return "Series export complete"   


def test_array_copy(start, end, signals):
    signals.log.emit("Copying arrays started")      
    for n in range(start, end):
        time.sleep(1)
        first_array=np.arange(n)
        second_array=np.copy(first_array)
        signals.log.emit("{} copied".format(first_array)) 
    return "Array copying complete"


def test_file_write(signals):
    try:
        if not os.path.exists("C:\\FileDemo\\"):
            os.makedirs("C:\\FileDemo\\")
            signals.log.emit("Directory created")
        with open('C:\\FileDemo\\myfile.txt', 'w+') as f:
            f.write('Create a new text file!')
        signals.log.emit("File created") 
        for n in range(10):
            time.sleep(1)
            with open("C:\\FileDemo\\myfile.txt", "a") as f:
                f.write("\n This text was added using Append.")
            signals.log.emit("Text appended to file")
        return "File operations finished"
    except FileNotFoundError:
        signals.log.emit("File myfile.txt does not exist")
        return "Terminated by error"

        
    
    

class Test_FileWrite(wezel.gui.Action):
    def run(self, app):
        window = wezel.widgets.LoggingWidget(test_file_write)
        app.addAsSubWindow(window, "Test File Write and Logging to GUI")


class Test_LoggingToGUI(wezel.gui.Action):
    def run(self, app):
        window = wezel.widgets.LoggingWidget(test_Function, start=1,end=10)
        app.addAsSubWindow(window, "Test Logging to GUI")


class Test_Copy(wezel.gui.Action):
    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        series_list = app.selected('Series')
        window = wezel.widgets.LoggingWidget(test_Copy, series_list=series_list)
        app.addAsSubWindow(window, "Test Logging to GUI while copying DICOM series")
       

class Test_ArrayCopy(wezel.gui.Action):  
    def run(self, app):
        window = wezel.widgets.LoggingWidget(test_array_copy, start=10,end=20)
        app.addAsSubWindow(window, "Test Logging to GUI while copying numpy arrays")


class Test_Export(wezel.gui.Action):
    """Export selected series"""

    def enable(self, app):
        return app.nr_selected('Series') != 0

    def run(self, app):
        series = app.selected('Series')
        path = app.dialog.directory("Where do you want to export the data?")
        window = wezel.widgets.LoggingWidget(test_export, series=series, path=path)
        app.addAsSubWindow(window, "Test Logging to GUI while copying numpy arrays")

