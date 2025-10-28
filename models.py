from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

class FileListModel(QAbstractListModel):
    def __init__(self, items:list[str]|None=None, parent=None):
        super().__init__(parent)
        self.items = items or []

    def rowCount(self, parent=QModelIndex()): return len(self.items)

    def data(self, idx, role=Qt.DisplayRole):
        if not idx.isValid(): return None
        if role == Qt.DisplayRole: return self.items[idx.row()]
        return None

    def setItems(self, items:list[str]):
        self.beginResetModel(); self.items = items; self.endResetModel()
