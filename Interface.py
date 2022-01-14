import sys
from shutil import copyfile
from functools import partial

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit
from PyQt5.uic.properties import QtCore


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 260)
        self.initUI()
        self.messages = []
        self.check_filename = 'cs448b_ipasn.csv'

    def initUI(self):
        self.button_open = QPushButton(self)
        self.button_open.setGeometry(40, 40, 100, 50)
        self.button_open.setText("Set file")
        self.button_open.clicked.connect(partial(self.__clicked_btn, 1))

        self.button_check = QPushButton(self)
        self.button_check.setGeometry(150, 40, 100, 50)
        self.button_check.setText("Run checker")
        self.button_check.clicked.connect(partial(self.__clicked_btn, 2))

        self.button_listen = QPushButton(self)
        self.button_listen.setGeometry(260, 40, 100, 50)
        self.button_listen.setText("Listen network")
        self.button_listen.clicked.connect(partial(self.__clicked_btn, 3))

        self.button_reset = QPushButton(self)
        self.button_reset.setGeometry(40, 200, 100, 50)
        self.button_reset.setText("Restore default")
        self.button_reset.clicked.connect(partial(self.__clicked_btn, 4))

        self.text_box = QTextEdit(self)
        self.text_box.setGeometry(20, 100, 360, 90)
        self.text_box.setReadOnly(True)

        self.show()

    def __clicked_btn(self, value):
        if value == 1:
            self.__load_file()
        if value == 2:
            self.__check()
        if value == 3:
            self.__listen()
        if value == 4:
            self.__reset_file()

    def __load_file(self):
        dlg = QFileDialog()
        dlg.setModal(True)
        source_path = dlg.getOpenFileName()[0]
        url = QUrl.fromLocalFile(source_path)
        try:
            copyfile(source_path, 'archive/' + url.fileName())
            self.file = url.fileName()
            self.text_box.append("Loaded file: " + url.fileName())
        except FileNotFoundError as fnt:
            pass

    def __check(self):
        print('checking')
        self.text_box.append("checking")

    def __listen(self):
        print('listening')
        self.text_box.append("listening")

    def __reset_file(self):
        self.check_filename = 'cs448b_ipasn.csv'
        self.text_box.append("Restored default file")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

'''
        app = QApplication([])
        window = QWidget()
        layout = QVBoxLayout()
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        self.open_button = QPushButton('Select file')
        layout.addWidget(open_button)
        check_button = QPushButton('Check')
        layout.addWidget(check_button)
        window.setLayout(layout)
        window.show()
        app.exec()
        '''
