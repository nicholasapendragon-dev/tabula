# tabula_writer/panels_qt/base_panel_qt.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor, QTextBlock
from PyQt6.QtCore import QRegularExpression, pyqtSignal, Qt, QTimer, QPoint, QObject
import re
from spellchecker import SpellChecker
from ..utils.nav_qt import handle_panel_navigation

LINK_TYPE_PROPERTY_ID = Qt.ItemDataRole.UserRole + 1

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document, panel_instance, theme):
        super().__init__(document)
        self.panel = panel_instance
        self.theme = theme
        
        self.header_format = self._create_format(30, bold=True)
        self.bold_format = self._create_format(bold=True)
        self.italic_format = self._create_format(italic=True)
        
        self.wikilink_format = self._create_format(underline=True, color=self.theme['accent_main'], bold=True)
        self.wikilink_format.setProperty(LINK_TYPE_PROPERTY_ID, "wikilink")

        self.footnote_format = self._create_format(underline=True, color=self.theme['accent_negative'])
        self.footnote_format.setProperty(LINK_TYPE_PROPERTY_ID, "footnote")

        self.tag_format = self._create_format(color=self.theme['accent_main'], bold=True)
        self.tag_format.setProperty(LINK_TYPE_PROPERTY_ID, "tag")
        
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor("red"))
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        self.hide_format = QTextCharFormat()
        self.hide_format.setForeground(QColor("transparent"))
        self.hide_format.setFontPointSize(1)
        
        self.unfocused_format = QTextCharFormat()
        unfocused_color = QColor(self.theme['text_fg'])
        unfocused_color.setAlphaF(0.4)
        self.unfocused_format.setForeground(unfocused_color)

        self.rules = [
            (QRegularExpression(r"(#\s)(.*)"), self.header_format, [1]),
            (QRegularExpression(r"(\*\*)(.*?)(\*\*)"), self.bold_format, [1, 3]),
            (QRegularExpression(r"(\*)(.*?)(\*)"), self.italic_format, [1, 3]),
            (QRegularExpression(r"(\[\[)(.*?)(\]\])"), self.wikilink_format, [1, 3]),
            (QRegularExpression(r"(\[\^)(\d+)(\])"), self.footnote_format, [1, 3]),
            (QRegularExpression(r"(@\w+)"), self.tag_format, []) 
        ]
        self.spell_checker = SpellChecker()

    def _create_format(self, point_size=16, bold=False, italic=False, underline=False, color="#3d3d3d"):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(point_size)
        fmt.setFontWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        fmt.setFontItalic(italic)
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline if underline else QTextCharFormat.UnderlineStyle.NoUnderline)
        fmt.setForeground(QColor(color))
        return fmt

    def highlightBlock(self, text):
        if hasattr(self.panel, 'is_focus_mode') and self.panel.is_focus_mode:
            current_block_number = self.currentBlock().blockNumber()
            focused_block_number = self.panel.focused_block_number
            context_lines = self.panel.focus_context_lines
            
            if abs(current_block_number - focused_block_number) > context_lines:
                self.setFormat(0, len(text), self.unfocused_format)
                return

        for pattern, base_format, marker_groups in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                content_group_index = 2 if len(marker_groups) > 0 and match.lastCapturedIndex() >= 2 else 0
                self.setFormat(match.capturedStart(content_group_index), match.capturedLength(content_group_index), base_format)
                for group_index in marker_groups:
                    self.setFormat(match.capturedStart(group_index), match.capturedLength(group_index), self.hide_format)
        
        words = re.findall(r"\b[a-zA-Z']+\b", text)
        if not words: return
        
        misspelled = self.spell_checker.unknown(words)
        for word in misspelled:
            pattern = QRegularExpression(fr"\b{word}\b")
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                is_link = False
                for i in range(match.capturedStart(), match.capturedEnd()):
                    if self.format(i).property(LINK_TYPE_PROPERTY_ID):
                        is_link = True
                        break
                if not is_link:
                    self.setFormat(match.capturedStart(), match.capturedLength(), self.misspelled_format)


class InteractiveTextEdit(QTextEdit):
    wikilink_clicked = pyqtSignal(str)
    footnote_clicked = pyqtSignal(str)
    tag_clicked = pyqtSignal(str)

    def __init__(self, parent_panel):
        super().__init__()
        self.parent_panel = parent_panel
        self.setMouseTracking(True)
        
    def get_link_at_position(self, position):
        if isinstance(position, QPoint):
            cursor = self.cursorForPosition(position)
        else:
            cursor = QTextCursor(self.document())
            cursor.setPosition(position)
        
        block = cursor.block()
        block_text = block.text()
        pos_in_block = cursor.position() - block.position()
        
        highlighter = self.parent_panel.highlighter

        for pattern, fmt, _ in highlighter.rules:
            link_type = fmt.property(LINK_TYPE_PROPERTY_ID)
            if not link_type:
                continue

            it = pattern.globalMatch(block_text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart(0)
                end = match.capturedEnd(0)

                if start <= pos_in_block < end:
                    if link_type == "tag":
                        link_text = match.captured(0)
                    else:
                        link_text = match.captured(2)
                    
                    return link_type, link_text

        return None, None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            link_type, link_text = self.get_link_at_position(event.pos())
            
            if link_type and link_text:
                if link_type == "wikilink": self.wikilink_clicked.emit(link_text)
                elif link_type == "footnote": self.footnote_clicked.emit(link_text)
                elif link_type == "tag": self.tag_clicked.emit(link_text)
                return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if handle_panel_navigation(self.parent_panel, event):
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        link_type, _ = self.get_link_at_position(event.pos())
        self.viewport().setCursor(Qt.CursorShape.PointingHandCursor if link_type else Qt.CursorShape.IBeamCursor)
        super().mouseMoveEvent(event)


class BasePanel(QFrame):
    word_count_changed = pyqtSignal()
    save_status_changed = pyqtSignal()
    wikilink_clicked = pyqtSignal(str)
    footnote_clicked = pyqtSignal(str)
    tag_clicked = pyqtSignal(str)

    def __init__(self, app_instance, framed=True, header_text=None):
        super().__init__()
        self.app = app_instance
        self.text_modified = False
        
        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        if header_text:
            header_label = QLabel(header_text)
            header_label.setObjectName("PanelHeader")
            content_layout.addWidget(header_label)

        self.text_edit = InteractiveTextEdit(self)
        if header_text:
            self.text_edit.setStyleSheet("border-top: none; border-top-left-radius: 0; border-top-right-radius: 0;")
        
        content_layout.addWidget(self.text_edit)
        
        self.highlighter = MarkdownHighlighter(self.text_edit.document(), self, self.app.theme)
        
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.wikilink_clicked.connect(self.wikilink_clicked.emit)
        self.text_edit.footnote_clicked.connect(self.footnote_clicked.emit)
        self.text_edit.tag_clicked.connect(self.tag_clicked.emit)
        
    def on_text_changed(self):
        self.text_modified = True
        self.save_status_changed.emit()
        self.word_count_changed.emit()

    def focus_text(self):
        QTimer.singleShot(0, self.text_edit.setFocus)

    def get_content(self):
        return self.text_edit.toPlainText()

    def on_action_key(self):
        cursor = self.text_edit.textCursor()
        link_type, link_text = self.text_edit.get_link_at_position(cursor.position())
        if link_type and link_text:
            if link_type == "wikilink": self.wikilink_clicked.emit(link_text)
            elif link_type == "footnote": self.footnote_clicked.emit(link_text)
            elif link_type == "tag": self.tag_clicked.emit(link_text)
