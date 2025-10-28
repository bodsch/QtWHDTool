from pathlib import Path
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QListView, QGroupBox, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QToolBar, QStatusBar, QFileDialog,
    QCheckBox
)
from models import FileListModel

DUMMY = [f"{i:04d}Game_v1.0.lha" for i in range(1, 120)]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WHDLoad Download Tool v1.6 (Qt6)")
        self._build_actions()
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()
        self._wire()
        self._load_dummy()

    # Actions
    def _build_actions(self):
        self.act_open_dat = QAction("Load Data", self); self.act_open_dat.setShortcut(QKeySequence.Open)
        self.act_download = QAction("Download", self)
        self.act_quit = QAction("Quit", self); self.act_quit.setShortcut(QKeySequence.Quit)
        self.menuBar().addMenu("&File").addActions([self.act_open_dat, self.act_quit])

    def _build_toolbar(self):
        tb = QToolBar("Main", self); tb.setMovable(False)
        tb.addAction(self.act_open_dat); tb.addAction(self.act_download)
        self.addToolBar(Qt.TopToolBarArea, tb)

    # Central UI
    def _build_central(self):
        splitter = QSplitter(self); splitter.setOrientation(Qt.Horizontal)
        # Left: list
        self.list_view = QListView()
        self.list_model = FileListModel([])
        self.list_view.setModel(self.list_model)
        self.list_view.setSelectionMode(QListView.ExtendedSelection)
        splitter.addWidget(self.list_view)
        splitter.setStretchFactor(0, 3)

        # Right: controls column
        right = QWidget(); rv = QVBoxLayout(right); rv.setSpacing(8)

        # Server Settings
        gb_server = QGroupBox("Server Settings")
        g = QGridLayout(gb_server); r=0
        g.addWidget(QLabel("User Name"), r,0); self.ed_user = QLineEdit("ftp"); g.addWidget(self.ed_user, r,1)
        r+=1; g.addWidget(QLabel("Password"), r,0); self.ed_pwd = QLineEdit("amiga"); self.ed_pwd.setEchoMode(QLineEdit.Password); g.addWidget(self.ed_pwd, r,1)
        r+=1; g.addWidget(QLabel("Server"), r,0)
        hs = QHBoxLayout(); self.ed_server = QLineEdit("ftp2.grandis.nu"); hs.addWidget(self.ed_server)
        hs.addWidget(QLabel("Port")); self.sp_port = QSpinBox(); self.sp_port.setRange(1,65535); self.sp_port.setValue(21); hs.addWidget(self.sp_port)
        g.addLayout(hs, r,1)
        r+=1; g.addWidget(QLabel("FTP Folder"), r,0); self.ed_folder = QLineEdit("Retroplay WHDLoad Packs"); g.addWidget(self.ed_folder, r,1)
        r+=1; g.addWidget(QLabel("HTTP Path"), r,0); self.ed_http = QLineEdit("https://ftp2.grandis.nu/turran/FTP/Retroplay%20WHDLoad%20Packs/Commodore%20Amiga%20-%20HD%20Loaders%20-%20Games%20(2025-09-21).zip"); g.addWidget(self.ed_http, r,1)
        rv.addWidget(gb_server)

        # Folder Settings
        gb_folder = QGroupBox("Folder Settings"); g = QGridLayout(gb_folder); r=0
        g.addWidget(QLabel("Parent"), r,0)
        hp = QHBoxLayout(); self.ed_parent = QLineEdit(r"E:\AGS_Database\WHD\\"); hp.addWidget(self.ed_parent)
        self.btn_open_parent = QPushButton("Open"); self.btn_set_parent = QPushButton("Set")
        hp.addWidget(self.btn_open_parent); hp.addWidget(self.btn_set_parent)
        g.addLayout(hp, r,1); r+=1
        # Subfolders
        for label in ("Games","Demos","Gameβ","Gameδ"):
            g.addWidget(QLabel(label), r,0)
            hl = QHBoxLayout(); ed = QLineEdit(label if label!="Games" else "Game"); hl.addWidget(ed)
            btn = QPushButton("Open"); hl.addWidget(btn)
            g.addLayout(hl, r,1); r+=1
        rv.addWidget(gb_folder)

        # Sorting
        gb_sort = QGroupBox("Sorting"); hl = QHBoxLayout(gb_sort)
        self.cb_sort = QComboBox(); self.cb_sort.addItems(["Alphabetical","Size","Language","Type"])
        self.cb_lang_ignore = QComboBox(); self.cb_lang_ignore.addItems(["Ignore Languages","Only English","Only DE/EN"])
        hl.addWidget(QLabel("Sorting:")); hl.addWidget(self.cb_sort,1); hl.addWidget(self.cb_lang_ignore,1)
        rv.addWidget(gb_sort)

        # Filter
        gb_filter = QGroupBox("Filter"); g = QGridLayout(gb_filter)
        # System
        sys_box = QGroupBox("System"); sys_v = QVBoxLayout(sys_box)
        for t in ("Amiga","CD32","CDTV","CDROM","Arcadia"):
            setattr(self, f"chk_sys_{t.lower()}", QCheckBox(t)); sys_v.addWidget(getattr(self, f"chk_sys_{t.lower()}"))
        # Chipset
        chip_box = QGroupBox("Chipset"); chip_v = QVBoxLayout(chip_box)
        for t in ("AGA","NTSC","ECS/OCS","PAL"):
            key=t.replace("/","").replace(" ","").lower()
            setattr(self, f"chk_chip_{key}", QCheckBox(t)); chip_v.addWidget(getattr(self, f"chk_chip_{key}"))
        # Sound
        snd_box = QGroupBox("Sound"); snd_v = QVBoxLayout(snd_box)
        for t in ("MT32","NoMusic","GM","FM","Munt"):
            setattr(self, f"chk_sound_{t.lower()}", QCheckBox(t)); snd_v.addWidget(getattr(self, f"chk_sound_{t.lower()}"))
        # Language grid
        lang_box = QGroupBox("Language"); lang_g = QGridLayout(lang_box)
        langs = ["Croat.","Greek","Italian","Multi","Polish","Spanish","Swedish",
                 "Czech","Danish","Dutch","English","Finnish","French","German"]
        self.lang_checks=[]
        for i, name in enumerate(langs):
            cb = QCheckBox(name); cb.setChecked(True); self.lang_checks.append(cb)
            lang_g.addWidget(cb, i//4, i%4)

        g.addWidget(sys_box, 0,0)
        g.addWidget(chip_box, 0,1)
        g.addWidget(snd_box, 1,0)
        g.addWidget(lang_box, 1,1)
        # Lang/Clear/Reset row
        lang_btns = QHBoxLayout()
        self.btn_lang = QPushButton("Lang."); self.btn_clear = QPushButton("Clear"); self.btn_reset = QPushButton("Reset")
        lang_btns.addStretch(1); lang_btns.addWidget(self.btn_lang); lang_btns.addWidget(self.btn_clear); lang_btns.addWidget(self.btn_reset)
        g.addLayout(lang_btns, 2,0,1,2)
        rv.addWidget(gb_filter)

        # Right side button stacks
        right_buttons = QHBoxLayout()
        col1 = self._panel_with_buttons("FTP Actions", ["Load Data","Download","HTTP ▼"])
        col2 = self._panel_with_buttons("Lists", ["Edit List","Load List","Save List","Append List","Clear Edits"])
        col3 = self._panel_with_buttons("Data", ["Clean Files","Clear Data","Make Folder"])
        col4 = self._panel_with_buttons("Misc", ["Save Prefs","Load Prefs","Help","About","Donate!"])
        right_buttons.addLayout(col1); right_buttons.addLayout(col2); right_buttons.addLayout(col3); right_buttons.addLayout(col4)
        rv.addLayout(right_buttons)

        rv.addStretch(1)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 4)

        c = QWidget(); layout = QVBoxLayout(c); layout.addWidget(splitter)
        self.setCentralWidget(c)

    def _panel_with_buttons(self, title:str, labels:list[str]) -> QVBoxLayout:
        gb = QGroupBox(title); v = QVBoxLayout(gb)
        for lab in labels:
            btn = QPushButton(lab); v.addWidget(btn)
        v.addStretch(1)
        outer = QVBoxLayout(); outer.addWidget(gb)
        return outer

    def _build_statusbar(self):
        sb = QStatusBar(self); self.setStatusBar(sb)
        self.lb_sys = QLabel("System: Amiga"); self.lb_chip = QLabel("Chipset: ECS/OCS")
        self.lb_tv = QLabel("TV System: PAL"); self.lb_lang = QLabel("Language: English")
        self.lb_type = QLabel("Type: Game"); self.lb_status = QLabel("Status: Available")
        self.lb_size = QLabel("Size: 202 KB")
        for w in (self.lb_sys, self.lb_chip, self.lb_tv, self.lb_lang, self.lb_type, self.lb_status, self.lb_size):
            sb.addPermanentWidget(w)

    def _wire(self):
        self.act_open_dat.triggered.connect(self._open_dat)
        self.act_quit.triggered.connect(self.close)
        self.act_download.triggered.connect(self._download)
        self.btn_clear.clicked.connect(self._clear_filters)
        self.btn_reset.clicked.connect(self._reset_filters)

    def _load_dummy(self):
        self.list_model.setItems(DUMMY)

    # Slots / stubs
    @Slot()
    def _open_dat(self):
        p, _ = QFileDialog.getOpenFileName(self, "Load DAT", "", "DAT files (*.dat);;All files (*.*)")
        if not p: return
        self.statusBar().showMessage(f"Loaded: {Path(p).name}", 3000)

    @Slot()
    def _download(self):
        sel = self.list_view.selectionModel().selectedIndexes()
        count = len(sel)
        self.statusBar().showMessage(f"Queued {count} items", 3000)

    @Slot()
    def _clear_filters(self):
        for cb in self.lang_checks: cb.setChecked(False)

    @Slot()
    def _reset_filters(self):
        for cb in self.lang_checks: cb.setChecked(True)
