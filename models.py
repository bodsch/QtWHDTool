from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

class Entry:
    __slots__ = ("name","version","lang","size","status")
    def __init__(self, name, version, lang, size, status=""):
        self.name=name; self.version=version; self.lang=lang; self.size=size; self.status=status

class EntryTableModel(QAbstractTableModel):
    HEAD = ["Name","Version","Sprache","Größe","Status"]
    def __init__(self, items:list[Entry]|None=None, parent=None):
        super().__init__(parent)
        self.items = items or []

    def rowCount(self, parent=QModelIndex()): return len(self.items)
    def columnCount(self, parent=QModelIndex()): return len(self.HEAD)

    def data(self, idx, role=Qt.DisplayRole):
        if not idx.isValid(): return None
        e = self.items[idx.row()]
        if role == Qt.DisplayRole:
            return [e.name, e.version, e.lang, f"{e.size}", e.status][idx.column()]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft if idx.column() in (0,4) else Qt.AlignCenter
        return None

    def headerData(self, s, o, role=Qt.DisplayRole):
        if role==Qt.DisplayRole and o==Qt.Horizontal: return self.HEAD[s]
        return None

    def setItems(self, items:list[Entry]):
        self.beginResetModel(); self.items = items; self.endResetModel()

    def entry(self, row:int)->Entry:
        return self.items[row]
