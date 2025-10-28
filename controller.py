from pathlib import Path
from typing import Optional
from PySide6.QtCore import QFile, QObject, Slot
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader

from models import FileListModel

class MainController(QObject):
    def __init__(self, ui_path: str):
        super().__init__()
        self.ui = self._load_ui(ui_path)  # QMainWindow
        self.ui.setWindowTitle("WHDLoad Download Tool v1.6 (Qt6)")

        # Models
        self.file_model = FileListModel([f"{i:04d}Game_v1.0.lha" for i in range(1, 120)])
        self.ui.listView.setModel(self.file_model)

        # Wire buttons
        self.ui.btnLoadData.clicked.connect(self.on_load_data)
        self.ui.btnDownload.clicked.connect(self.on_download)
        self.ui.btnHttp.clicked.connect(self.on_http)
        self.ui.btnClear.clicked.connect(self.on_clear_lang)
        self.ui.btnReset.clicked.connect(self.on_reset_lang)
        self.ui.btnOpenParent.clicked.connect(self.on_open_parent)
        self.ui.btnSetParent.clicked.connect(self.on_set_parent)
        self.ui.btnAbout.clicked.connect(self.on_about)

    def _load_ui(self, path: str):
        f = QFile(path)
        if not f.open(QFile.ReadOnly):
            raise RuntimeError(f"UI nicht gefunden: {path}")
        try:
            loader = QUiLoader()
            w = loader.load(f, None)
            if w is None:
                raise RuntimeError("QUiLoader konnte UI nicht laden.")
            return w
        finally:
            f.close()

    # Slots
    @Slot()
    def on_load_data(self):
        fname, _ = QFileDialog.getOpenFileName(self.ui, "Load DAT", "", "DAT files (*.dat);;All files (*.*)")
        if not fname: return
        self.ui.statusbar.showMessage(f"Loaded: {Path(fname).name}", 3000)

    @Slot()
    def on_download(self):
        sel = self.ui.listView.selectionModel().selectedIndexes()
        QMessageBox.information(self.ui, "Download", f"Queued {len(sel)} item(s).")

    @Slot()
    def on_http(self):
        QMessageBox.information(self.ui, "HTTP", "HTTP action stub.")

    @Slot()
    def on_clear_lang(self):
        for child in self.ui.boxLanguage.findChildren(type(self.ui.langEnglish)):
            if getattr(child, "isChecked", None):
                child.setChecked(False)

    @Slot()
    def on_reset_lang(self):
        for child in self.ui.boxLanguage.findChildren(type(self.ui.langEnglish)):
            if getattr(child, "isChecked", None):
                child.setChecked(True)

    @Slot()
    def on_open_parent(self):
        d = QFileDialog.getExistingDirectory(self.ui, "Select Parent Folder")
        if d:
            self.ui.edParent.setText(d)

    @Slot()
    def on_set_parent(self):
        QMessageBox.information(self.ui, "Folder", f"Parent set:\n{self.ui.edParent.text()}")

    @Slot()
    def on_about(self):
        QMessageBox.information(self.ui, "About", "WHDLoad Download Tool\nUI via Qt Designer + PySide6")
