from PySide2.QtCore import Qt
from PySide2.QtWidgets import (    
    QDialog, 
    QFormLayout, 
    QDialogButtonBox, 
    QComboBox,
    QLabel, 
    QSpinBox,  
    QScrollBar,
    QDoubleSpinBox, 
    QLineEdit, 
    QListWidget, 
    QAbstractItemView 
)


class UserInput(QDialog):
    """
    Pop-up window for user input
    
    Input Parameters
    *****************
    fields: 
                a list of dictionaries of one of the following types:
                {"type":"float", "label":"Name of the field", "value":1.0, "minimum": 0.0, "maximum": 1.0}
                {"type":"integer", "label":"Name of the field", "value":1, "minimum": 0, "maximum": 100}
                {"type":"string", "label":"Name of the field", "value":"My string"}
                {"type":"dropdownlist", "label":"Name of the field", "list":["item 1",...,"item n" ], "value":2}
                {"type":"listview", "label":"Name of the field", "list":["item 1",...,"item n"], "value": [0,3]}
                {"type":"select record", "label":"Name of the field", "options":["item 1",...,"item n" ], default":item 1} # Note: default can be a list
                {"type":"select records", "label":"Name of the field", "options":["item 1",...,"item n"], "default": [item 1, item 3]}
            
            Widgets are created in the same order on the dialog they occupy in the dictionary; ie., 
            the first dictionary item is uppermost input widget on the dialog 
            and the last dictionary item is the last input widget on the dialog.

    Raises:
        ValueError if default values for listr items are provided that are not in the list of options
    
    title - optional string containing the input dialog title. 
            Has a default string "Input Parameters"
    helpText - optional help text to be displayed above the input widgets.
    """
    def __init__(self, *fields, title="Input Parameters", helpText=None):
        super().__init__()

        self.button = 'Cancel'
        self.fields = fields
        
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.CustomizeWindowHint, True)
        self.setSizeGripEnabled(True)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel   # OK and Cancel button
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.clickedOK)   # OK button
        self.buttonBox.rejected.connect(self.clickedCancel)  # Cancel button
        self.layout = QFormLayout()
        if helpText:
            self.helpTextLbl = QLabel("<H4>" + helpText  +"</H4>")
            self.helpTextLbl.setWordWrap(True)
            self.layout.addRow(self.helpTextLbl)

        self.listWidget = []
        for field in self._processInput(*fields):

            if field['type'] == "integer":
                widget = QSpinBox()
                widget.setMinimum(int(field['minimum']))
                widget.setMaximum(int(field['maximum']))
                widget.setValue(int(field['value']))

            elif field['type'] == "float":
                widget = QDoubleSpinBox()
                widget.setDecimals(6)
                widget.setMinimum(float(field['minimum']))
                widget.setMaximum(float(field['maximum']))
                widget.setValue(float(field['value']))
                

            elif field['type'] == "string":
                widget = QLineEdit()
                widget.setText(str(field['value']))
                
            elif field['type'] == "dropdownlist":
                widget = QComboBox()
                widget.addItems([str(v) for v in field["list"]])
                try:
                    widget.setCurrentIndex(int(field['value'])) 
                except:
                    msg = 'Default list index is out of range'
                    raise ValueError(msg)

            elif field['type'] == "select record":
                widget = QComboBox()
                widget.addItems([v.label() for v in field["options"]])
                if isinstance(field['default'], list):
                    field['default'] = None if field['default']==[] else field['default'][0]
                    #field['default'] = field["options"][0] if field['default']==[] else field['default'][0]
                if field['default'] is None:
                    idx = 0
                else:
                    try:
                        idx = field["options"].index(field['default'])
                    except:
                        msg = 'Default value is not in the list of options provided'
                        raise ValueError(msg)
                widget.setCurrentIndex(idx)
                    

            elif field['type'] == "listview":
                widget = QListWidget()
                widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
                widget.addItems([str(v) for v in field["list"]])
                scrollBar = QScrollBar(self) 
                widget.setVerticalScrollBar(scrollBar)
                #widget.setMinimumHeight(widget.sizeHintForColumn(0))
                #widget.setMaximumHeight(300)
                widget.setMinimumWidth(widget.sizeHintForColumn(0))
                widget.resize(widget.sizeHintForColumn(0),300)
                for i in field['value']:
                    item = widget.item(i)
                    item.setSelected(True)

            elif field['type'] == "select records":
                widget = QListWidget()
                widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
                widget.addItems([v.label() for v in field["options"]])
                scrollBar = QScrollBar(self) 
                widget.setVerticalScrollBar(scrollBar)
                #widget.setMinimumHeight(widget.sizeHintForColumn(0))
                #widget.setMaximumHeight(300)
                widget.setMinimumWidth(widget.sizeHintForColumn(0))
                widget.resize(widget.sizeHintForColumn(0),300)
                for record in field['default']:
                    try:
                        idx = field["options"].index(record)
                    except:
                        msg = 'Default value is not in the list of options provided'
                        raise ValueError(msg)
                    widget.item(idx).setSelected(True)

            self.layout.addRow(field['label'], widget)
            self.listWidget.append(widget)

        self.layout.addRow("", self.buttonBox)
        self.setLayout(self.layout)
        self.exec_()  
        self.cancel = self.button=='Cancel'
        self.values = self._processOutput()


    def _processInput(self, *fields):
        """Processes the dictionary objects in *fields into a format that 
        can be used to create the widgets on the input dialog window.
        """

        types = (
            "integer", 
            "float", 
            "string", 
            "dropdownlist", 
            "listview", 
            "select record", 
            "select records",
        )
    
        # set default values for items that are not provided by the user
        for field in fields:

            if field['type'] not in types:
                msg = field['label'] + ' is not a valid type \n'
                msg += 'Must be either integer, float, string, dropdownlist or listview'
                raise TypeError(msg)

            if field['type'] == "listview":
                if "value" not in field: 
                    field['value'] = []

            elif field['type'] == "select records":
                if "default" not in field: 
                    field['default'] = []

            elif field["type"] == "dropdownlist":
                if "value" not in field: 
                    field["value"] = 0

            elif field["type"] == "select record":
                if "default" not in field: 
                    field["default"] = field['options'][0]

            elif field["type"] == "string":
                if "value" not in field: 
                    field["value"] = "Hello"

            elif field["type"] == "integer":
                if "value" not in field: 
                    field["value"] = 0 
                if "minimum" not in field: 
                    field["minimum"] = -2147483648
                if "maximum" not in field: 
                    field["maximum"] = +2147483647
                if field["value"] < field["minimum"]: 
                    field["value"] = field["minimum"]
                if field["value"] > field["maximum"]: 
                    field["value"] = field["maximum"]

            elif field["type"] == "float":
                if "value" not in field: 
                    field["value"] = 0.0  
                if "minimum" not in field: 
                    field["minimum"] = -1.0e+18
                if "maximum" not in field: 
                    field["maximum"] = +1.0e+18          
                if field["value"] < field["minimum"]: 
                    field["value"] = field["minimum"]
                if field["value"] > field["maximum"]: 
                    field["value"] = field["maximum"]

        return fields


    def _processOutput(self):
        """Returns a list of parameter values as input by the user, 
        in the same as order as the widgets
        on the input dialog from top most (first item in the list) 
        to the bottom most (last item in the list)."""
  
        # Overwrite the value key with the returned parameter
        output = []
        for f, field in enumerate(self.fields):
            widget = self.listWidget[f]

            if field["type"] == "listview":
                n, sel = widget.count(), widget.selectedItems()
                field["value"] = [i for i in range(n) if widget.item(i) in sel]
                output.append(field)

            elif field["type"] == "select records":
                n, sel = widget.count(), widget.selectedItems()
                records = [field["options"][i] for i in range(n) if widget.item(i) in sel]
                output.append(records)

            elif field["type"] == "dropdownlist":
                field["value"] = widget.currentIndex()
                output.append(field)

            elif field["type"] == "select record":
                record = field["options"][widget.currentIndex()]
                output.append(record)

            elif field["type"] == "string":
                field["value"] = widget.text()
                output.append(field)

            elif field["type"] == "integer":
                field["value"] = widget.value()
                output.append(field)

            elif field["type"] == "float":
                field["value"] = widget.value()
                output.append(field)

        return output
        #return self.fields


    def clickedOK(self): # OK button clicked
        self.button = 'OK'
        self.accept()
    
    def clickedCancel(self): # Cancel button clicked
        self.button = 'Cancel'
        self.accept()


