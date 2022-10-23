import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("resources/icon.ico"))
