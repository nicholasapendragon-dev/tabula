# popups_qt/input_popup_qt.py
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from .base_popup_qt import BasePopup
from PyQt6.QtCore import Qt

class InputPopup(BasePopup):
    def __init__(self, title, label_text, default_text="", parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        
        self.setWindowTitle(title)
        self.user_input = ""

        label = QLabel(label_text)
        self.main_layout.addWidget(label)
        
        self.line_edit = QLineEdit()
        if default_text:
            self.line_edit.setText(default_text)
        self.line_edit.selectAll()
        self.main_layout.addWidget(self.line_edit)
        
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok)
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        self.main_layout.addWidget(button_container)
        
        self.line_edit.setFocus()
        self.line_edit.returnPressed.connect(self.on_ok)

    def on_ok(self):
        self.user_input = self.line_edit.text()
        self.accept()

    def get_text(self):
        return self.user_input
