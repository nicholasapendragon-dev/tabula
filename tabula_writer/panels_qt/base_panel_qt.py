# tabula_writer/panels_qt/base_panel_qt.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import pyqtSignal
from .panel_components import InteractiveTextEdit, MarkdownHighlighter

class BasePanel(QWidget):
    word_count_changed = pyqtSignal()
    save_status_changed = pyqtSignal()
    wikilink_clicked = pyqtSignal(str)
    footnote_clicked = pyqtSignal(str)
    tag_clicked = pyqtSignal(str)

    def __init__(self, app_instance, framed=False, header_text=None, parent=None):
        super().__init__(parent)
        self.app = app_instance
        self.text_modified = False

        # --- Corrected Layout Logic ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QFrame() if framed else QWidget()
        main_layout.addWidget(container)
        
        content_layout = QVBoxLayout(container)
        if framed:
            content_layout.setContentsMargins(15, 15, 15, 15)
        else:
            content_layout.setContentsMargins(0, 15, 0, 15)
        content_layout.setSpacing(10)
        # --- End of Corrected Logic ---

        if header_text:
            self.header_label = QLabel(header_text)
            self.header_label.setObjectName("PanelHeader")
            content_layout.addWidget(self.header_label)

        self.text_edit = InteractiveTextEdit(self)
        self.highlighter = MarkdownHighlighter(self.text_edit.document(), self.app.theme, self.app)
        content_layout.addWidget(self.text_edit)

        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.wikilink_clicked.connect(self.wikilink_clicked)
        self.text_edit.footnote_clicked.connect(self.footnote_clicked)
        self.text_edit.tag_clicked.connect(self.tag_clicked)

    def on_text_changed(self):
        self.text_modified = True
        self.word_count_changed.emit()
        self.save_status_changed.emit()

    def get_content(self):
        return self.text_edit.toPlainText()

    def focus_text(self):
        self.text_edit.setFocus()
    
    def on_action_key(self):
        cursor = self.text_edit.textCursor()
        link_type, link_text = self.text_edit.get_link_at_position(cursor.position())
        
        if link_type == "wikilink":
            self.wikilink_clicked.emit(link_text)
        elif link_type == "footnote":
            self.footnote_clicked.emit(link_text)
        elif link_type == "tag":
            self.tag_clicked.emit(link_text)
