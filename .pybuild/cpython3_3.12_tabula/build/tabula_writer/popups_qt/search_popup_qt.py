# popups_qt/search_popup_qt.py
from PyQt6.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from .base_popup_qt import BasePopup
import os

class SearchPopup(BasePopup):
    search_requested = pyqtSignal(str)
    open_file_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(theme=parent.theme, parent=parent)

        self.setWindowTitle("Search Files")
        self.setMinimumSize(600, 400)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search all files...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_activated)
        
        self.status_label = QLabel("Ready to search.")
        self.status_label.setStyleSheet(f"color: {self.theme['accent_gray']};")

        self.main_layout.addWidget(self.search_input)
        self.main_layout.addWidget(self.results_list, 1) # Give list stretch factor
        self.main_layout.addWidget(self.status_label)
        
        self.search_input.setFocus()
        
        self.result_found = self.results_list.addItem
        
    def on_search_changed(self, query):
        if len(query) > 2:
            self.results_list.clear()
            self.status_label.setText("Searching...")
            self.search_requested.emit(query)
        else:
            self.results_list.clear()
            self.status_label.setText("Type at least 3 characters to search.")
            
    def search_finished(self):
        self.status_label.setText(f"Found {self.results_list.count()} results.")

    def result_found(self, result):
        display_text = f"{result['name']} (line {result['line_num']}): {result['preview']}"
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, result['path'])
        self.results_list.addItem(item)
        
    def on_item_activated(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.open_file_requested.emit(file_path)
        self.accept()
