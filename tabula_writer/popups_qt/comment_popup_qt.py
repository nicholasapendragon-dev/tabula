# tabula_writer/popups_qt/comment_popup_qt.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from .base_popup_qt import BasePopup

class CommentPopup(BasePopup):
    # Add the missing signal definition
    comment_saved = pyqtSignal(int, str)

    def __init__(self, footnote_number, app_instance):
        super().__init__(app_instance.theme, parent=app_instance)
        self.footnote_number = footnote_number
        self.app = app_instance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Comment for Footnote [^{self.footnote_number}]")

        self.main_layout.addWidget(QLabel(f"Enter your comment for [^{self.footnote_number}]:"))

        self.comment_edit = QTextEdit()
        self.comment_edit.setMinimumHeight(150)
        self.main_layout.addWidget(self.comment_edit)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Comment")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        self.main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)

        self.comment_edit.setFocus()

    def on_save(self):
        comment_text = self.comment_edit.toPlainText().strip()
        if comment_text:
            # Emit the signal with the footnote number and the text
            self.comment_saved.emit(self.footnote_number, comment_text)
            self.accept()
