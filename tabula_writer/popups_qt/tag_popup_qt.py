from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from .animated_popup_qt import AnimatedPopup
from tabula_writer.ui.widgets_qt import RoundedFrame

class TagPopup(AnimatedPopup):
    def __init__(self, tag, files, open_callback, parent=None):
        super().__init__(parent)
        self.app = parent
        self.files = files
        self.open_callback = open_callback
        self.theme = self.app.theme

        self.setWindowTitle(f"Files with @{tag}")
        self.setModal(True)
        self.setGeometry(0, 0, 500, 250)
        self.setStyleSheet(f"QDialog {{ background-color: {self.theme['bg']}; }}")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Files tagged with @{tag}"))
        header_layout.addStretch()
        header_layout.addWidget(QLabel(f"({len(files)} files)"))
        main_layout.addLayout(header_layout)

        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        if not files:
            self.list_widget.addItem("No files found with this tag.")
        else:
            for file_info in files:
                item = QListWidgetItem(f" [{file_info['type'].upper()}] {file_info['name']}")
                item.setData(Qt.ItemDataRole.UserRole, file_info)
                self.list_widget.addItem(item)
        
        self.list_widget.itemDoubleClicked.connect(self.on_select)

    def on_select(self, item):
        file_info = item.data(Qt.ItemDataRole.UserRole)
        if file_info and self.open_callback:
            self.open_callback(file_info['path'])
        self.accept()
