# popups_qt/full_comment_viewer_popup_qt.py
from PyQt6.QtWidgets import QLabel, QTextBrowser, QPushButton
from .base_popup_qt import BasePopup
import re
# --- MODIFICATION: Added the missing import for Qt ---
from PyQt6.QtCore import Qt

class FullCommentViewerPopup(BasePopup):
    def __init__(self, comment_data, parent=None):
        super().__init__(theme=parent.theme, parent=parent)
        
        self.setWindowTitle(f"Viewing Comment [^{comment_data['footnote_number']}]")
        self.setMinimumSize(600, 400)
        
        title = f"Comment for <b>[^{comment_data['footnote_number']}]</b>"
        ref_match = re.search(r"Referencing: '(.*)'", comment_data['full_text'])
        if ref_match:
            title += f" in <i>{ref_match.group(1)}</i>"
        
        self.main_layout.addWidget(QLabel(title))

        self.text_browser = QTextBrowser()
        self.text_browser.setPlainText(comment_data['body_text'])
        self.main_layout.addWidget(self.text_browser)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignRight)
        
        self.close_button.setFocus()
