"""
Main widget for displaying tabular data
"""

import pandas as pd

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QFileDialog, QLineEdit, QApplication,                           
        QVBoxLayout, QHBoxLayout, QTableWidgetItem, QLabel, QToolBar, QAction,
        QWidget, QHeaderView,  QTableWidget,  QAbstractItemView)
from PySide2.QtGui import QIcon

import wezel
import wezel.icons as icons


class TableDisplay(wezel.gui.MainWidget):
    """Display dataframe as table."""

    rowHeight = 4

    def __init__(self, df):  
        super().__init__()
        
        if isinstance(df, list):
            df = pd.concat(df, ignore_index=True)
        elif isinstance(df, dict):
            df = pd.DataFrame(df)
        if df.empty:
            self.setError('Empty dataset. \n\n Nothing to show here..')
            return 
        self._df = df

        # Search Bar
        searchFieldLabel = QLabel(self)
        searchFieldLabel.setText("Search for: ")
        searchFieldLabel.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        self.searchField = QLineEdit()
        self.searchField.textEdited.connect(self.searchTable)
        
        # Export buttons
        self.action_export_csv = QAction()
        self.action_export_csv.setIcon(QIcon(icons.document_excel_csv))
        self.action_export_csv.setToolTip('Save as CSV file')
        self.action_export_csv.triggered.connect(self.exportToCSV) 
        self.action_export_xls = QAction()
        self.action_export_xls.setIcon(QIcon(icons.document_excel))
        self.action_export_xls.setToolTip('Save as Excel file')
        self.action_export_xls.triggered.connect(self.exportToExcel) 
        self.action_export_clp = QAction()
        self.action_export_clp.setIcon(QIcon(icons.clipboard__plus))
        self.action_export_clp.setToolTip('Copy to clipboard')
        self.action_export_clp.triggered.connect(self.exportToClipboard) 

        # Toolbar
        tableTools = QToolBar()
        tableTools.addAction(self.action_export_csv)
        tableTools.addAction(self.action_export_xls)
        tableTools.addAction(self.action_export_clp)

        # Top row with controls
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(searchFieldLabel)
        layout.addWidget(self.searchField)
        layout.addWidget(tableTools)
        horizontalBox = QWidget()
        horizontalBox.setStyleSheet("background-color: white")
        horizontalBox.setLayout(layout)

        # Add table
        self.tableWidget = QTableWidget()
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tableWidget.horizontalScrollBar().setEnabled(True)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.verticalHeader().setVisible(False)
        self.populateTable()

        # Global layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(horizontalBox)
        layout.addWidget(self.tableWidget) 
        self.setLayout(layout)
        self.setAttribute(Qt.WA_DeleteOnClose)
        


    def populateTable(self):   
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Create header row
        for c, col in enumerate(self._df):
            headerItem = QTableWidgetItem(QTableWidgetItem(col+"\n"))
            headerItem.setTextAlignment(Qt.AlignLeft)
            self.tableWidget.setHorizontalHeaderItem(c, headerItem)

        # Create all other rows
        for _, row in self._df.iterrows():
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setRowHeight(rowPosition, self.rowHeight)
            for c, col in enumerate(self._df):
                self.tableWidget.setItem(rowPosition, c, QTableWidgetItem(str(row[col])))

        # Resize columns to contents
        ncol = self._df.shape[1]
        header = self.tableWidget.horizontalHeader()
        for col in range(ncol-1):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(ncol-1, QHeaderView.ResizeMode(QHeaderView.AdjustToContentsOnFirstShow))

        QApplication.restoreOverrideCursor()



    def exportToCSV(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save as ...', 'table.csv', "CSV files (*.csv)") 
        if filename != '':
            self._df.to_csv(filename, index=False)


    def exportToExcel(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save as ...', 'table.xlsx', "Excel files (*.xlsx)") 
        if filename != '':
            self._df.to_excel(filename, index=False)


    def exportToClipboard(self):
        self._df.to_clipboard(excel=True, sep='\t', index=False, header=None)


    def searchTable(self):
        expression = self.searchField.text()
        self.tableWidget.clearSelection()
        if expression:
            items = self.tableWidget.findItems(expression, Qt.MatchContains)
            if items:  # we have found something
                for item in items:
                    item.setSelected(True)
                    #self.tableWidget.item(item).setSelected(True)
                self.tableWidget.scrollToItem(items[0])
                #item = items[0]  # take the first
                #table.table.setCurrentItem(item)





