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


class Option(QtWidgets.QDialog):

    options = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Option, self).__init__()
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setFixedSize(300, 340)
        self.initUI()
        self._lock = threading.Lock()

    def initUI(self):
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
        self.label4.setText("Run Checker on completion?")

        self.interface_box = QLineEdit(self)
        self.interface_box.setGeometry(20, 55, 80, 20)

        self.package_box = QLineEdit(self)
        self.package_box.setGeometry(20, 115, 80, 20)
        self.onlyInt = QIntValidator()
        self.package_box.setValidator(self.onlyInt)

        self.filename_box = QLineEdit(self)
        self.filename_box.setGeometry(20, 175, 80, 20)

        self.option_box = QCheckBox(self)
        self.option_box.setGeometry(90, 235, 80, 20)

        self.button_close = QPushButton(self)
        self.button_close.setGeometry(80, 280, 100, 50)
        self.button_close.setText("Accept")
        self.button_close.clicked.connect(partial(self.__clicked_btn))

    def __clicked_btn(self):
        result = dict()
        result['interface'] = self.interface_box.text()
        result['packages'] = str(self.package_box.text())
        result['filename'] = self.filename_box.text()
        result['option'] = str(self.option_box.isChecked())

        self.options.emit(json.dumps(result))
        self.close()

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 260)
        self.initUI()
        self.messages = []
        self.file = 'cs448b_ipasn.csv'
        self._lock = threading.Lock()
        self.options = None
        self.listener = None

    def initUI(self):
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
        self.button_listen.setText("Listen network")
        self.button_listen.clicked.connect(partial(self.__clicked_btn, 3))

        self.button_reset = QPushButton(self)
        self.button_reset.setGeometry(90, 200, 100, 50)
        self.button_reset.setText("Restore default")
        self.button_reset.clicked.connect(partial(self.__clicked_btn, 4))

        self.text_box = QTextEdit(self)
        self.text_box.setGeometry(20, 100, 460, 90)
        self.text_box.setReadOnly(True)

        self.show()

    def __clicked_btn(self, value):
        if value == 1:
            self.__load_file()
        if value == 2:
            self.__check(self.file)
        if value == 3:
            self.__listen()
        if value == 4:
            self.__reset_file()

    def __load_file(self):
        home = str(Path.home())
        dlg = QFileDialog(self, 'Network data', home)
        dlg.setModal(True)
        source_path = dlg.getOpenFileName()[0]
        url = QUrl.fromLocalFile(source_path)
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

    def __check(self, filename):
        checker = CheckerThread(filename, self)
        checker.message.connect(self.__display_text)
        checker.start()

    def __listen(self):
        if self.listener:
            self.__disable_listener()
            return
        with self._lock:
            self.text_box.append("listening")
            self.text_box.repaint()
        option_window = Option()
        option_window.setWindowModality(Qt.ApplicationModal)
        option_window.options.connect(self.__listen_thread)
        option_window.show()

    def __listen_thread(self, options):
        options = json.loads(options)
        print(options)
        check_option = False
        if options['option'] == 'True':
            check_option = True
        self.listener = ListenerThread(options['interface'], int(options['packages']), options['filename'], self,
                                  check_option)
        self.listener.message.connect(self.__display_text)
        self.listener.checker_activation.connect(self.__run_checker_from_listener)
        self.button_listen.setText('Stop listening')

        self.listener.start()

    def __disable_listener(self):
        self.listener.stop()
        self.listener = None
        self.button_listen.setText('Listen network')

    def __reset_file(self):
        self.check_filename = 'cs448b_ipasn.csv'
        self.text_box.append("Restored default file")

    def __display_text(self, text):
        with self._lock:
            self.text_box.append(text)
            self.text_box.repaint()
            self.text_box.update()

    def __run_checker_from_listener(self, filename):
        self.__check(filename)


class ListenerThread(QThread):

    message = pyqtSignal(str)
    checker_activation = pyqtSignal(str)

    def __init__(self, interface, number, filename, parent, auto_check=False):
        QObject.__init__(self, parent)
        self.interface = interface
        self.number = number
        self.filename = filename
        self.auto_check = auto_check
        self.files_amount = 0

    def __run_listener(self, interface, number, output_name):
        return run_from_gui(interface, 'archive/' + output_name, number)

    def run(self):
        while True:
            self.files_amount += 1
            iteration_number = self.files_amount

            output_name = self.filename + str(iteration_number) + '.csv'
            result = self.__run_listener(self.interface, self.number, output_name)
            self.message.emit('listening finished, output saved to file ' + output_name)
            if result and self.auto_check:
                self.checker_activation.emit(output_name)

    def stop(self):
        self.terminate()


class CheckerThread(QThread):

    message = pyqtSignal(str)

    def __init__(self, filename, parent):
        QObject.__init__(self, parent)
        self.filename = filename

    def run(self):
        self.message.emit('running checker on file: ' + self.filename)
        checker = Checker()
        entropy = checker.check_file('archive/' + self.filename)
        if type(entropy) is dict:
            for key in entropy.keys():
                value = entropy[key]
                message = 'is not suspicious'
                if value > 0.1:
                    message = 'is suspicious'
                self.message.emit('Station with address ' + str(key) + ' ' + message + f', entropy value: {value:.3f}')
        else:
            self.message.emit(entropy)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

