# app.py
import sys, asyncio
from PySide6.QtWidgets import QApplication
# from qasync import QEventLoop
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WHDLoad Download Tool")
    app.setOrganizationName("WHDLoad")
    win = MainWindow()
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
