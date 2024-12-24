import sys

from PyQt5.QtWidgets import QApplication

from gui import Pico8Player

app = QApplication(sys.argv)
player = Pico8Player()
player.show()
sys.exit(app.exec())