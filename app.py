import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from controller import MainController

def main():
    app = QApplication(sys.argv)
    ui_path = str(Path(__file__).parent / "ui" / "mainwindow.ui")
    ctl = MainController(ui_path)
    ctl.ui.resize(1280, 800)
    ctl.ui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
