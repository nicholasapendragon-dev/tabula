# popups_qt/wikilink_popup_qt.py
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from .base_popup_qt import BasePopup
import os

class WikiLinkPopup(BasePopup):
    def __init__(self, link, matches, open_file_callback, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        
        self.setWindowTitle(f"Links for: {link}")
        self.setMinimumSize(500, 300)
        self.open_file_callback = open_file_callback

        label = QLabel(f"Documents referencing <b>[[{link}]]</b>:")
        self.main_layout.addWidget(label)

        self.list_widget = QListWidget()
        for match in matches:
            item = QListWidgetItem(os.path.basename(match['path']))
            item.setData(Qt.ItemDataRole.UserRole, match['path'])
            self.list_widget.addItem(item)
        self.list_widget.itemDoubleClicked.connect(self.on_item_selected)
        
        self.main_layout.addWidget(self.list_widget)

    def on_item_selected(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.open_file_callback(path)
        self.accept()
