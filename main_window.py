from pathlib import Path
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFileDialog, QDockWidget, QTableView, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QSpinBox, QProgressBar,
    QToolBar, QStatusBar, QMessageBox
)
from models import EntryTableModel, Entry

DUMMY = [
    Entry("Another World", "1.2", "EN", 1024),
    Entry("Katakis", "1.0", "DE", 2048),
    Entry("Turrican", "2.1", "EN", 1536),
    Entry("Lotus 2", "1.1", "FR", 1024),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WHDLoad Download Tool")
        self._build_actions()
        self._build_toolbar()
        self._build_central()
        self._build_filter_dock()
        self._build_statusbar()
        self._wire()
        self._load_dummy()

    # Actions
    def _build_actions(self):
        self.act_open_dat = QAction("DAT laden...", self)
        self.act_open_dat.setShortcut(QKeySequence.Open)
        self.act_quit = QAction("Beenden", self)
        self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_select_all = QAction("Alle auswählen", self)
        self.act_select_none = QAction("Auswahl löschen", self)
        self.act_download = QAction("Auswahl laden", self)
        self.act_stop = QAction("Abbrechen", self)
        self.act_prefs = QAction("Einstellungen...", self)
        self.act_about = QAction("Über", self)

        # Menü
        m_file = self.menuBar().addMenu("&Datei")
        m_file.addAction(self.act_open_dat)
        m_file.addSeparator()
        m_file.addAction(self.act_quit)

        m_actions = self.menuBar().addMenu("&Aktion")
        m_actions.addAction(self.act_select_all)
        m_actions.addAction(self.act_select_none)
        m_actions.addSeparator()
        m_actions.addAction(self.act_download)
        m_actions.addAction(self.act_stop)

        m_help = self.menuBar().addMenu("&Hilfe")
        m_help.addAction(self.act_prefs)
        m_help.addSeparator()
        m_help.addAction(self.act_about)

    # Toolbar
    def _build_toolbar(self):
        tb = QToolBar("Hauptleiste", self)
        tb.setMovable(False)
        tb.addAction(self.act_open_dat)
        tb.addSeparator()
        tb.addAction(self.act_download)
        tb.addAction(self.act_stop)
        tb.addSeparator()
        tb.addAction(self.act_select_all)
        tb.addAction(self.act_select_none)
        self.addToolBar(Qt.TopToolBarArea, tb)

    # Central widget (table + quick filter)
    def _build_central(self):
        c = QWidget(self); self.setCentralWidget(c)
        v = QVBoxLayout(c)
        # Quick filter row
        h = QHBoxLayout()
        h.addWidget(QLabel("Suche:"))
        self.ed_search = QLineEdit(placeholderText="Name/Sprache")
        self.btn_clear = QPushButton("Zurücksetzen")
        h.addWidget(self.ed_search, 1)
        h.addWidget(self.btn_clear)
        v.addLayout(h)

        # Table
        self.table = QTableView(self)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setSortingEnabled(True)
        self.model = EntryTableModel([])
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        v.addWidget(self.table, 1)

        # Bottom buttons
        bh = QHBoxLayout()
        self.btn_download = QPushButton("Auswahl laden")
        self.btn_stop = QPushButton("Abbrechen")
        bh.addStretch(1)
        bh.addWidget(self.btn_download)
        bh.addWidget(self.btn_stop)
        v.addLayout(bh)

    # Filter dock (extended)
    def _build_filter_dock(self):
        dock = QDockWidget("Filter", self)
        dock.setObjectName("FilterDock")
        w = QWidget(); v = QVBoxLayout(w)

        # Language filter
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Sprache:"))
        self.cb_lang = QComboBox(); self.cb_lang.addItems(["Alle","EN","DE","FR","IT","ES"])
        lang_row.addWidget(self.cb_lang, 1)
        v.addLayout(lang_row)

        # Size range
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Größe ≤ (KB):"))
        self.sp_max_size = QSpinBox(); self.sp_max_size.setRange(0, 10_000); self.sp_max_size.setValue(0)
        size_row.addWidget(self.sp_max_size, 1)
        v.addLayout(size_row)

        # Flags typical for WHDLoad sets
        self.chk_installed = QCheckBox("Nur installierbare")
        self.chk_updates = QCheckBox("Nur Updates")
        self.chk_missing = QCheckBox("Nur fehlende")
        v.addWidget(self.chk_installed)
        v.addWidget(self.chk_updates)
        v.addWidget(self.chk_missing)

        v.addStretch(1)

        dock.setWidget(w)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    # Status bar
    def _build_statusbar(self):
        sb = QStatusBar(self)
        self.setStatusBar(sb)
        self.lbl_status = QLabel("Bereit")
        self.pb_total = QProgressBar()
        self.pb_total.setRange(0, 1)
        self.pb_total.setValue(0)
        self.pb_total.setFixedWidth(250)
        sb.addPermanentWidget(self.lbl_status)
        sb.addPermanentWidget(self.pb_total)

    # Wiring
    def _wire(self):
        self.act_open_dat.triggered.connect(self._open_dat)
        self.act_quit.triggered.connect(self.close)
        self.act_select_all.triggered.connect(self._select_all)
        self.act_select_none.triggered.connect(self._select_none)
        self.act_download.triggered.connect(self._download_selected)
        self.act_stop.triggered.connect(self._stop_downloads)
        self.act_about.triggered.connect(self._about)
        self.btn_download.clicked.connect(self._download_selected)
        self.btn_stop.clicked.connect(self._stop_downloads)
        self.btn_clear.clicked.connect(self._clear_filters)
        self.ed_search.textChanged.connect(self._apply_filters)
        self.cb_lang.currentIndexChanged.connect(self._apply_filters)
        self.sp_max_size.valueChanged.connect(self._apply_filters)
        self.chk_installed.toggled.connect(self._apply_filters)
        self.chk_updates.toggled.connect(self._apply_filters)
        self.chk_missing.toggled.connect(self._apply_filters)

    # Data
    def _load_dummy(self):
        self._all = DUMMY
        self.model.setItems(self._all)

    # Slots
    @Slot()
    def _open_dat(self):
        p, _ = QFileDialog.getOpenFileName(self, "DAT wählen", "", "DAT-Dateien (*.dat);;Alle Dateien (*.*)")
        if not p: return
        # Nur UI: Parser wird später integriert
        self.statusBar().showMessage(f"Geladen: {Path(p).name}", 3000)

    @Slot()
    def _select_all(self):
        self.table.selectAll()

    @Slot()
    def _select_none(self):
        self.table.clearSelection()

    @Slot()
    def _download_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        if not rows:
            QMessageBox.information(self, "Hinweis", "Keine Auswahl.")
            return
        self.lbl_status.setText(f"{len(rows)} Elemente in Warteschlange")
        # Nur UI: Fortschritt simulieren
        self.pb_total.setRange(0, len(rows))
        self.pb_total.setValue(0)

    @Slot()
    def _stop_downloads(self):
        # Nur UI
        self.pb_total.setRange(0,1); self.pb_total.setValue(0)
        self.lbl_status.setText("Abgebrochen")

    @Slot()
    def _clear_filters(self):
        self.ed_search.clear()
        self.cb_lang.setCurrentIndex(0)
        self.sp_max_size.setValue(0)
        self.chk_installed.setChecked(False)
        self.chk_updates.setChecked(False)
        self.chk_missing.setChecked(False)

    @Slot()
    def _apply_filters(self):
        txt = self.ed_search.text().lower()
        lang = self.cb_lang.currentText()
        max_kb = self.sp_max_size.value()
        def keep(e:Entry)->bool:
            if txt and txt not in e.name.lower() and txt not in e.lang.lower():
                return False
            if lang != "Alle" and e.lang != lang:
                return False
            if max_kb and e.size > max_kb:
                return False
            # Flags sind Platzhalter. Später echte Felder mappen.
            return True
        self.model.setItems([e for e in self._all if keep(e)])

    @Slot()
    def _about(self):
        QMessageBox.information(self, "Über", "WHDLoad Download Tool\nUI-Prototyp in PySide6")
