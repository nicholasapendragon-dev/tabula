# popups_qt/save_popup_qt.py
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QLineEdit
from PyQt6.QtCore import pyqtSignal
from .base_popup_qt import BasePopup

class SavePopup(BasePopup):
    save_current_requested = pyqtSignal()
    save_as_new_requested = pyqtSignal(str) # Now carries the filename

    def __init__(self, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        
        self.setWindowTitle("Save Options")
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        self.save_button = QPushButton("Save Current Document")
        self.save_button.clicked.connect(self.on_save_current)
        self.save_button.setDefault(True)
        
        self.save_as_button = QPushButton("Save as New Document...")
        self.save_as_button.clicked.connect(self.show_save_as_input)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        # --- MODIFICATION: Add a hidden line edit for the new filename ---
        self.filename_input = QLineEdit(self)
        self.filename_input.setPlaceholderText("Enter new document name...")
        self.filename_input.setVisible(False)
        self.filename_input.returnPressed.connect(self.on_save_as)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.save_as_button)
        button_layout.addWidget(self.filename_input) # Add to layout
        button_layout.addSpacing(15)
        button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(button_layout)
        
        self.save_button.setFocus()

    def show_save_as_input(self):
        """Shows the filename input field and hides the other buttons."""
        self.filename_input.setVisible(True)
        self.filename_input.setFocus()
        self.save_button.setVisible(False)
        self.save_as_button.setVisible(False)
        self.setWindowTitle("Save As...")

    def on_save_as(self):
        """Emits the signal with the new filename and closes."""
        filename = self.filename_input.text()
        if filename:
            self.save_as_new_requested.emit(filename)
            self.accept()

    def on_save_current(self):
        """Emit the signal for a normal save and then close."""
        self.save_current_requested.emit()
        self.accept()
