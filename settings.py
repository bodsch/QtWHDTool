# settings.py
from PySide6.QtCore import QSettings

ORG = "WHDLoad"
APP = "WHDLoadDownloadTool"

def settings() -> QSettings:
    s = QSettings(ORG, APP)
    return s
