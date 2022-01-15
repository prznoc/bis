import shutil
import sys
import threading
import json
from shutil import copyfile
from functools import partial
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from Checker import Checker
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QTextEdit, QLabel, QMainWindow, QLineEdit, \
    QCheckBox
from NetLog import run_from_gui


# Listener options Window
class Option(QtWidgets.QDialog):

    options = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Option, self).__init__()
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setFixedSize(300, 340)
        self.initUI()
        self._lock = threading.Lock()

    def initUI(self):
        # Elements of GUI
        self.label1 = QLabel(self)
        self.label1.setGeometry(110, 40, 180, 50)
        self.label1.setText("Select interface")

        self.label2 = QLabel(self)
        self.label2.setGeometry(110, 100, 180, 50)
        self.label2.setText("Number of packages")

        self.label3 = QLabel(self)
        self.label3.setGeometry(110, 160, 180, 50)
        self.label3.setText("Output filename")

        self.label4 = QLabel(self)
        self.label4.setGeometry(110, 220, 180, 50)
        self.label4.setText("Run Checker on completion")

        self.interface_box = QLineEdit(self)
        self.interface_box.setGeometry(20, 55, 80, 20)

        self.package_box = QLineEdit(self)
        self.package_box.setGeometry(20, 115, 80, 20)
        self.onlyInt = QIntValidator()  # Validator is set to let pass only int data
        self.package_box.setValidator(self.onlyInt)

        self.filename_box = QLineEdit(self)
        self.filename_box.setGeometry(20, 175, 80, 20)

        self.option_box = QCheckBox(self)
        self.option_box.setGeometry(90, 235, 80, 20)

        # button to send data
        self.button_close = QPushButton(self)
        self.button_close.setGeometry(100, 280, 100, 50)
        self.button_close.setText("Accept")
        self.button_close.clicked.connect(partial(self.__clicked_btn))

    def __clicked_btn(self):
        result = dict()
        result['interface'] = self.interface_box.text()
        result['packages'] = str(self.package_box.text())
        result['filename'] = self.filename_box.text()
        result['option'] = str(self.option_box.isChecked())

        self.options.emit(json.dumps(result))  # send data to main window
        self.close()

# Main GUI Window
class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 260)
        self.initUI()
        self.messages = []
        self.file = 'cs448b_ipasn.csv'  # default dataset
        self._lock = threading.Lock()
        self.options = None  # options sent from Option Window, neccesary for data exchange
        self.listener = None

    def initUI(self):
        # Interface elements
        self.button_open = QPushButton(self)
        self.button_open.setGeometry(90, 40, 100, 50)
        self.button_open.setText("Set file")
        self.button_open.clicked.connect(partial(self.__clicked_btn, 1))

        self.button_check = QPushButton(self)
        self.button_check.setGeometry(200, 40, 100, 50)
        self.button_check.setText("Run checker")
        self.button_check.clicked.connect(partial(self.__clicked_btn, 2))

        self.button_listen = QPushButton(self)
        self.button_listen.setGeometry(310, 40, 100, 50)
        self.button_listen.setText("Run NetLog")
        self.button_listen.clicked.connect(partial(self.__clicked_btn, 3))

        self.button_reset = QPushButton(self)
        self.button_reset.setGeometry(90, 200, 100, 50)
        self.button_reset.setText("Restore default")
        self.button_reset.clicked.connect(partial(self.__clicked_btn, 4))

        self.text_box = QTextEdit(self)
        self.text_box.setGeometry(20, 100, 460, 90)
        self.text_box.setReadOnly(True)

        self.show()

    # Determines result of button click (shared by all buttons, 'value' passed to distinguish them)
    def __clicked_btn(self, value):
        if value == 1:
            self.__load_file()
        if value == 2:
            self.__check(self.file)
        if value == 3:
            self.__listen()
        if value == 4:
            self.__reset_file()

    # Set File
    def __load_file(self):
        home = str(Path.home())
        # Open dialog to select source file
        dlg = QFileDialog(self, 'Network data', home)
        dlg.setModal(True)
        source_path = dlg.getOpenFileName()[0]
        url = QUrl.fromLocalFile(source_path)
        # copy chosen file to /archive dir
        try:
            copyfile(source_path, 'archive/' + url.fileName())
            self.file = url.fileName()
            self.text_box.append("Loaded file: " + url.fileName())
        except FileNotFoundError as fnt:
            pass
        except shutil.SameFileError:
            self.file = url.fileName()
            self.text_box.append("Loaded file: " + url.fileName())
            pass

    # Run checker
    def __check(self, filename):
        checker = CheckerThread(filename, self)  # start another thread
        # 'connect' connects pyqtSignal object in checker with __display(text) method in self
        checker.message.connect(self.__display_text)
        checker.start()

    # Run NetLog/Stop Listening
    def __listen(self):
        if self.listener:  # If listener is active, deactivate
            self.__disable_listener()
            return
        option_window = Option()  # process option selection window
        option_window.setWindowModality(Qt.ApplicationModal)  # set to disable main window while choosing options
        option_window.options.connect(self.__listen_thread)  # connection for data exchange
        option_window.show()

    def __listen_thread(self, options):
        options = json.loads(options)  # load options from Option window
        check_option = False
        # Validate values from option
        if options['option'] == 'True':
            check_option = True
        with self._lock:
            self.text_box.append("listening")
            self.text_box.repaint()
        package = 1000
        try:
            package = int(options['packages'])
        except Exception:
            pass
        # Run listener in separate thread
        self.listener = ListenerThread(options['interface'], package, options['filename'], self,
                                  check_option)
        self.listener.message.connect(self.__display_text)
        self.listener.checker_activation.connect(self.__run_checker_from_listener)
        # Change text on listener button
        self.button_listen.setText('Stop listening')

        self.listener.start()

    def __disable_listener(self):
        self.listener.stop()
        self.listener = None
        self.button_listen.setText('Listen network')

    def __reset_file(self):
        self.check_filename = 'cs448b_ipasn.csv'
        self.text_box.append("Restored default file")

    # neccesary to display text from another thread
    def __display_text(self, text):
        with self._lock:
            self.text_box.append(text)
            self.text_box.repaint()
            self.text_box.update()

    def __run_checker_from_listener(self, filename):
        self.__check(filename)


# Listener thread class
class ListenerThread(QThread):

    message = pyqtSignal(str)  # necessary for data exchange
    checker_activation = pyqtSignal(str)  # necessary for data exchange

    def __init__(self, interface, number, filename, parent, auto_check=False):
        QObject.__init__(self, parent)
        self.interface = interface
        self.number = number
        self.filename = filename
        self.auto_check = auto_check
        self.files_amount = 0

    def __run_listener(self, interface, number, output_name):
        return run_from_gui(interface, 'archive/' + output_name, number)  # Run NetLog module

    def run(self):
        # writes to separate files, limited by package option, until deactivated
        while True:
            self.files_amount += 1  # no of processed file
            iteration_number = self.files_amount

            output_name = self.filename + str(iteration_number) + '.csv'
            result = self.__run_listener(self.interface, self.number, output_name)
            if not result:
                self.checker_activation.emit('Something went wrong, check console for details')
                break
            self.message.emit('listening finished, output saved to file ' + output_name)
            # if relevant, check created file
            if result and self.auto_check:
                self.checker_activation.emit(output_name)

    def stop(self):
        self.terminate()


# Separate checker thread
class CheckerThread(QThread):

    message = pyqtSignal(str)  # necessary for data exchange

    def __init__(self, filename, parent):
        QObject.__init__(self, parent)
        self.filename = filename

    def run(self):
        self.message.emit('running checker on file: ' + self.filename)
        checker = Checker()
        entropy = checker.check_file('archive/' + self.filename)
        if type(entropy) is dict:
            # display results
            for key in entropy.keys():
                value = entropy[key]
                message = 'is not suspicious'
                # threshold based on example dataset
                if value > 0.1:
                    message = 'is suspicious'
                self.message.emit('Station with address ' + str(key) + ' ' + message + f', entropy value: {value:.3f}')
        else:
            self.message.emit(entropy)


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    

