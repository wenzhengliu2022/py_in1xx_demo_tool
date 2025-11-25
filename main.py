import sys

from PySide6.QtWidgets import QApplication
import gui.images_rc
from gui.app_gui import MainWindow

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
