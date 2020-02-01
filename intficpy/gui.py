import sys, os, re, time
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QPushButton,
    QAction,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QAbstractSlider,
    QSizePolicy,
    QFileDialog,
)
from PyQt5.QtGui import QIcon, QFont, QIcon
from .things import reflexive

##############################################################
# GUI.PY - the GUI for IntFicPy
# Defines the default GUI application for .
##############################################################
# TODO: modify App.__init__ to allow for insertion of a custom stylesheet directly from the main game file when the GUI is created
# TODO: display game title in the window title
# TODO: disallow ".sav" as a complete filename for saving

# defines the bold font for game output text
tBold = QFont()
tBold.setBold(True)

main_file = ""

scroll_style = """
        /* VERTICAL */
        QWidget {
        	background: #efefef; 
        }
        QScrollBar:vertical {
            border: none;
            background: #a3a3a3;
            border-radius: 6px;
            width: 30px;
            margin: 10px 8px 10px 8px;
        }

        QScrollBar::handle:vertical {
            background: #d0d0d0;
            border-radius: 6px;
            min-height: 15px;
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 10px;
            subcontrol-position: top left;
            subcontrol-origin: margin;
            position: absolute;
        }

        QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """


class Prelim:
    def __init__(self, main_name):
        global main_file
        main_file = main_name


class App(QMainWindow):
    """The App class, of which the GUI app will be an instance, creates the GUI's widgets and defines its methods """

    def __init__(
        self,
        me,
        style1="color: black; background-color: #d3e56b; border: none; border-radius:20px; margin-bottom: 15px",
        style2="color: black; background-color: #6be5cb; border: none; border-radius:20px; margin-bottom: 15px",
        scroll_style=scroll_style,
        app_style="QFrame { border:none;}",
        icon=None,
    ):
        """Initialize the GUI
		Takes argument me, pointing to the Player """
        import __main__

        super().__init__()
        if icon:
            self.setWindowIcon(QIcon(icon))
        reflexive.makeKnown(me)
        self.setObjectName("MainWindow")
        self.title = "IntFicPy"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.box_style1 = style1
        self.box_style2 = style2
        self.scroll_style = scroll_style
        self.initUI()
        self.showMaximized()
        self.me = me
        self.newBox(self.box_style1)
        #initGame(me, self, main_file)
        self.setStyleSheet(app_style)
        self.new_obox = False
        # used for game-interrupting cutscenes
        # populated by enterForMore()
        self.game = None

    def closeEvent(self, event):
        """Trigger program close. Close the recording file first, if open. """
        if self.game.lastTurn.recfile:
            self.game.lastTurn.recfile.close()
        event.accept()

    def initUI(self):
        """Build the basic user interface
		called by __init__ """
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.widget.resize(self.width, self.height)
        # self.widget.setLayout(self.main_layout)

        #   Container Widget
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.main_layout = QVBoxLayout()
        self.widget.setLayout(self.main_layout)

        # TextBox
        self.textbox = QLineEdit()
        self.textbox.resize(280, 30)

        #   Scroll Area Properties
        self.scroll_container = QWidget()
        self.scroll_container_layout = QVBoxLayout(self.scroll_container)

        self.scroll_widget = QWidget()
        self.scroll_widget_layout = QVBoxLayout()
        self.scroll_widget_layout.setContentsMargins(15, 15, 15, 30)
        self.scroll_widget.setLayout(self.scroll_widget_layout)

        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.Box)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_container_layout.addWidget(self.scroll)

        self.scroll_widget_layout.setAlignment(QtCore.Qt.AlignTop)

        self.main_layout.addWidget(self.scroll_container)
        self.main_layout.addWidget(self.textbox)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll_container.setStyleSheet(self.scroll_style)

        self.cutscene = []
        self.anykeyformore = False

        self.new_obox = True
        self.obox = QFrame()
        self.obox.setFrameStyle(QFrame.StyledPanel)
        self.obox.setStyleSheet(self.box_style1)
        self.olayout = QVBoxLayout()
        self.obox.setLayout(self.olayout)
        self.scroll_widget_layout.addWidget(self.obox)

    def turnMain(self, input_string):
        """Sends user input to the parser each turn
		Takes argument input_string, the cleaned user input string """
        quit = False
        if len(input_string) == 0:
            return 0
        else:
            # parse string
            self.game.parser.parseInput(input_string)
            self.game.daemons.runAll(self.game)

    def newBox(self, box_style):
        """Creates a new QFrame to wrap text in the game output area
		Takes argument box_style, an integer specifying textbox colour and style """
        self.new_obox = True
        self.obox = QFrame()
        self.obox.setFrameStyle(QFrame.StyledPanel)
        self.obox.setStyleSheet(box_style)

    def on_click(self):
        """Echos input, cleans input, and sends input to turnMain
		Called when the user presses return """
        textboxValue = self.textbox.text()
        self.textbox.setText("")
        self.newBox(self.box_style2)
        t_echo = "> " + textboxValue
        self.printToGUI(t_echo)
        input_string = textboxValue.lower()
        input_string = re.sub(r"[^\w\s]", "", input_string)
        self.newBox(self.box_style1)
        self.turnMain(textboxValue)

    def keyPressEvent(self, event):
        """Maps on_click to the enter key """
        if self.anykeyformore and self.cutscene != []:
            self.cutsceneNext()
        elif event.key() == QtCore.Qt.Key_Up and len(self.game.lastTurn.turn_list) > 0:
            self.game.lastTurn.back = self.game.lastTurn.back - 1
            if -self.game.lastTurn.back >= len(self.game.lastTurn.turn_list):
                self.game.lastTurn.back = 0
            self.textbox.setText(self.game.lastTurn.turn_list[self.game.lastTurn.back])
        elif (
            event.key() == QtCore.Qt.Key_Down
            and len(self.game.lastTurn.turn_list) > 0
            and self.game.lastTurn.back < 0
        ):
            self.game.lastTurn.back = self.game.lastTurn.back + 1
            self.textbox.setText(self.game.lastTurn.turn_list[self.game.lastTurn.back])
        elif event.key() == QtCore.Qt.Key_Return and len(self.textbox.text()) > 0:
            self.game.lastTurn.back = 0
            self.on_click()

    def printToGUI(self, out_string, bold=False):
        """Prints game output to the GUI, and scrolls down
		Takes arguments out_string, the string to print, and bold, a Boolean which defaults to False
		Returns True on success """
        try:
            self.new_obox
        except:
            self.new_obox = False
        if self.new_obox:
            self.scroll_widget_layout.addWidget(self.obox)
            self.olayout = QVBoxLayout()
            self.obox.setLayout(self.olayout)
            self.new_obox = False

        out = QLabel()
        out.setText(out_string)
        if bold:
            out.setFont(tBold)
        self.olayout.addWidget(out)
        out.setWordWrap(True)
        out.setStyleSheet("margin-bottom: 5px")
        out.setMaximumSize(out.sizeHint())
        out.setMinimumSize(out.sizeHint())
        self.obox.setMaximumSize(self.obox.sizeHint())
        self.obox.setMinimumSize(self.obox.sizeHint())
        vbar = self.scroll.verticalScrollBar()
        vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))
        return True

    def getSaveFileGUI(self):
        """Creates a QFileDialog when the user types save, and validates the selected file name
		Returns the file name or None"""
        cwd = os.getcwd()
        fname = QFileDialog.getSaveFileName(
            self, "New save file", cwd, "Save files (*.sav)"
        )
        fname = fname[0]
        if len(fname) == 0:
            return None
        # add .sav extension if necessary
        self.newBox(self.box_style1)
        if not "." in fname:
            fname = fname + ".sav"
        elif (fname.index(".") - len(fname)) != -4:
            ex_start = fname.index(".")
            fname = fname[0:ex_start]
            fname = fname + ".sav"
        elif fname[-4:] != ".sav":
            fname = fname[0:-4]
            fname = fname + ".sav"
        return fname

    def saveFilePrompt(self, extension, filetype_desc, msg):
        cwd = os.getcwd()
        fname = QFileDialog.getSaveFileName(
            self, msg, cwd, f"{filetype_desc} (*{extension})"
        )
        fname = fname[0]
        if len(fname) == 0:
            return None

        if fname.endswith(extension):
            return fname

        if "." in fname:
            fname = fname[:fname.index(".")]

        return fname + extension

    def openFilePrompt(self, extension, filetype_desc, msg):
        cwd = os.getcwd()
        fname = QFileDialog.getOpenFileName(
            self, msg, cwd, f"{filetype_desc} (*{extension})"
        )
        if not fname[0].endswith(extension):
            return None

        return fname[0]
