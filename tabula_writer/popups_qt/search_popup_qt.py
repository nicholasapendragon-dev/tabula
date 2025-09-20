# tabula_writer/popups_qt/search_popup_qt.py
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from .base_popup_qt import BasePopup

class SearchPopup(BasePopup):
    search_requested = pyqtSignal(str)
    open_file_requested = pyqtSignal(str)

    def __init__(self, app_instance):
        super().__init__(app_instance.theme, parent=app_instance)
        self.app = app_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Search Project")
        
        self.main_layout.addWidget(QLabel("Enter search query:"))
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        self.main_layout.addLayout(search_layout)
        
        self.results_list = QListWidget()
        self.main_layout.addWidget(self.results_list)

        self.status_label = QLabel("Ready to search.")
        self.main_layout.addWidget(self.status_label)
        
        self.search_input.returnPressed.connect(self.on_search)
        self.search_button.clicked.connect(self.on_search)
        self.results_list.itemDoubleClicked.connect(self.on_item_activated)

    def on_search(self):
        query = self.search_input.text().strip()
        if query:
            self.results_list.clear()
            self.status_label.setText("Searching...")
            self.search_requested.emit(query)

    def display_search_results(self, results):
        """Clears the list and displays all results returned from a search."""
        self.results_list.clear()
        if not results:
            self.status_label.setText("No results found.")
            return

        for result_data in results:
            item_text = f"{result_data['name']} (Line {result_data['line_num']})\n  {result_data['preview']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, result_data['path'])
            self.results_list.addItem(item)
        
        self.status_label.setText(f"Found {len(results)} match(es).")

    def search_finished(self):
        """Called when the search worker is done."""
        if self.results_list.count() == 0:
            self.status_label.setText("No results found.")

    def on_item_activated(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.open_file_requested.emit(file_path)
            self.accept()
