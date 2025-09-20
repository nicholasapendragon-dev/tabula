# popups_qt/comment_popup_qt.py
from PyQt6.QtWidgets import QLabel, QTextEdit, QPushButton, QHBoxLayout, QFrame
from .base_popup_qt import BasePopup

class CommentPopup(BasePopup):
    def __init__(self, footnote_number, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        self.footnote_number = footnote_number
        
        self.setWindowTitle(f"Comment for [^{footnote_number}]")
        self.setMinimumSize(500, 300)

        label = QLabel(f"Enter your comment for footnote <b>[^{footnote_number}]</b>:")
        self.main_layout.addWidget(label)
        
        self.text_edit = QTextEdit()
        self.main_layout.addWidget(self.text_edit)
        
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.save_button = QPushButton("Save Comment")
        self.save_button.setObjectName("GreenButton")
        self.save_button.clicked.connect(self.save_and_close)
        self.save_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        self.main_layout.addWidget(button_container)
        
        self.text_edit.setFocus()

    def save_and_close(self):
        comment_text = self.text_edit.toPlainText()
        if comment_text:
            self.parent()._save_comment_from_popup(self.footnote_number, comment_text)
        self.accept()
