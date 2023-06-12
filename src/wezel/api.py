import sys
import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

import wezel

# Define font size
font_size = 8

# Create application-wide style sheet
STYLESHEET = """
    /* Set font size for all widgets */
    QWidget {{
        font-size: {}pt;
    }}

    /* Set font size for QComboBox drop-down list */
    QComboBox QAbstractItemView {{
        font-size: {}pt;
    }}

    /* Set font size for QLabel text */
    QLabel {{
        font-size: {}pt;
    }}

    /* Set font size for QLineEdit text */
    QLineEdit {{
        font-size: {}pt;
    }}

    /* Set font size for QPushButton text */
    QPushButton {{
        font-size: {}pt;
    }}

    /* Set font size for QTextEdit text */
    QTextEdit {{
        font-size: {}pt;
    }}
""".format(font_size, font_size, font_size, font_size, font_size, font_size)



QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)



class Wezel:

    def __init__(self, project=None):
        self.log = logger()
        self.QApp = QApplication(sys.argv)
        #self.QApp.setWindowIcon(QIcon(wezel.icons.animal_dog))
        self.QApp.setWindowIcon(QIcon(wezel.icons.wezel_icon_transparent))
        self.QApp.setStyleSheet(STYLESHEET)
        self.menubar = wezel.gui.MenuBar(
            wezel.menubar.folder.menu,
            wezel.menubar.edit.menu,
            wezel.menubar.view.menu,
        )
        self._project = project

    def show(self):    
        self.log.info('Launching Wezel!')
        self.main = wezel.gui.Main(self, project=self._project)
        self.menubar.setupUI(self.main)
        self.main.setMenuBar(self.menubar)
        self.main.show()
        self.QApp.exec_()

    def open(self, path):
        self.main.open(path)

    def add_menu(self, menu, position=None):
        self.menubar.add(menu, position=position)

    def add_action(self, action, menu='File', position=None):
        for mbar_menu in self.menubar.menus():
            if mbar_menu.title() == menu:
                mbar_menu.add(action, position=position)
                return

    def add_separator(self, menu='File', position=None):
        for mbar_menu in self.menubar.menus():
            if mbar_menu.title() == menu:
                mbar_menu.add_separator(position=position)
                return



def app(**kwargs):

    # Otional
    # This closes the splash screen
    # pyi_splash is part of pyinstaller
    try:
        import pyi_splash

        ## Attempt at showing progress bar - does not work
        # count = 0
        # direction = 'right'
        # while pyi_splash.is_alive():
        #     move = '\u0020' * count
        #     pyi_splash.update_text(f'{move}\u2591\u2591')
        #     if direction == 'right':
        #         if len(move) < 97:
        #             count += 1
        #         else:
        #             direction = 'left'
        #     else:
        #         if len(move) > 0:
        #             count -= 1
        #         else:
        #             direction = 'right'
        #     time.sleep(0.05)

        pyi_splash.close()
    except:
        pass

    return Wezel(**kwargs)


def logger():
    
    LOG_FILE_NAME = "wezel_log.log"
    # creates some sort of conflict with mdreg - commenting out for now
#    if os.path.exists(LOG_FILE_NAME):
#        os.remove(LOG_FILE_NAME)
    LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
    logging.basicConfig(
        filename = LOG_FILE_NAME, 
        level = logging.INFO, 
        format = LOG_FORMAT)
    return logging.getLogger(__name__)


