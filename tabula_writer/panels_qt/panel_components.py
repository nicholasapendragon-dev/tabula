from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QRegularExpression, pyqtProperty
import re
from spellchecker import SpellChecker
from tabula_writer.utils.nav_qt import handle_editor_navigation

class MarkdownHighlighter(QSyntaxHighlighter):
    # The __init__ method is now corrected to accept the app_instance
    def __init__(self, document, theme, app_instance):
        super().__init__(document)
        self.theme = theme
        self.app = app_instance # Store a reference to the main app

        self.bold_format = self._create_format(bold=True)
        self.italic_format = self._create_format(italic=True)
        self.wikilink_format = self._create_format(underline=True, color=self.theme['link_beige'], bold=True)
        self.footnote_format = self._create_format(underline=True, color=self.theme['accent_red'])
        self.tag_format = self._create_format(color=self.theme['link_beige'], bold=True)
        
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor("red"))
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        self.hide_format = QTextCharFormat()
        self.hide_format.setForeground(QColor("transparent"))
        self.hide_format.setFontPointSize(1)

        self.rules = [
            (QRegularExpression(r"(\*\*)(.*?)(\*\*)"), self.bold_format, [1, 3]),
            (QRegularExpression(r"(\*)(.*?)(\*)"), self.italic_format, [1, 3]),
            (QRegularExpression(r"(\[\[)(.*?)(\]\])"), self.wikilink_format, [1, 3]),
            (QRegularExpression(r"(\[\^)(\d+)(\])"), self.footnote_format, [1, 3]),
            (QRegularExpression(r"(@\w+)"), self.tag_format, []) 
        ]
        self.spell_checker = SpellChecker()

    def _create_format(self, point_size=None, bold=False, italic=False, underline=False, color="#3d3d3d"):
        fmt = QTextCharFormat()
        if point_size:
            fmt.setFontPointSize(point_size)
        fmt.setFontWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        fmt.setFontItalic(italic)
        fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline if underline else QTextCharFormat.UnderlineStyle.NoUnderline)
        fmt.setForeground(QColor(color))
        return fmt

    def highlightBlock(self, text):
        header_match = re.match(r'^(#+)\s(.*)', text)
        if header_match:
            hash_count = len(header_match.group(1))
            header_size = max(12, self.app.base_font_size + (18 - (hash_count * 4)))
            header_format = self._create_format(point_size=header_size, bold=True)
            self.setFormat(0, len(text), header_format)

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
                    if self.format(i) in (self.wikilink_format, self.footnote_format, self.tag_format):
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
        
        self.blur_enabled = False
        self.verticalScrollBar().valueChanged.connect(self.ensure_centered)
        self._font_size = 18

    def get_font_size(self):
        return self._font_size

    def set_font_size(self, size):
        self._font_size = size
        self.setStyleSheet(f"font-size: {size}pt;")
        if hasattr(self.parent_panel, 'highlighter'):
            self.parent_panel.highlighter.rehighlight()

    dynamicFontSize = pyqtProperty(int, get_font_size, set_font_size)

    def toggle_typewriter_blur(self, enabled: bool):
        self.blur_enabled = enabled
        if enabled:
            self.ensure_centered()
        self.viewport().update()

    def ensure_centered(self):
        if not self.blur_enabled:
            return
        cursor_rect = self.cursorRect()
        center_pos = (self.viewport().height() // 2) - (cursor_rect.height() // 2)
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.value() + cursor_rect.top() - center_pos)

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.blur_enabled:
            return

        painter = QPainter(self.viewport())
        cursor_y = self.cursorRect().center().y()
        bg_color = self.parent_panel.app.theme['widget_bg']
        base_qcolor = QColor(bg_color)
        r, g, b = base_qcolor.red(), base_qcolor.green(), base_qcolor.blue()

        fade_gradient = QLinearGradient(0, 0, 0, cursor_y)
        fade_gradient.setColorAt(0.0, QColor(r, g, b, 220))
        fade_gradient.setColorAt(0.5, QColor(r, g, b, 100))
        fade_gradient.setColorAt(1.0, QColor(r, g, b, 0))

        painter.fillRect(QRect(0, 0, self.viewport().width(), cursor_y), fade_gradient)
        painter.end()

    def keyPressEvent(self, event):
        if handle_editor_navigation(self, event):
            return
        super().keyPressEvent(event)
        if self.blur_enabled:
            self.ensure_centered()

    def get_link_at_position(self, position):
        cursor = self.document().findBlock(position)
        block_text = cursor.text()
        block_start_pos = cursor.position()
        pos_in_block = position - block_start_pos

        highlighter = self.parent_panel.highlighter
        if not highlighter:
            return None, None

        for pattern, _, _ in highlighter.rules:
            link_type = None
            if pattern.pattern() == r"(\[\[)(.*?)(\]\])":
                link_type = "wikilink"
            elif pattern.pattern() == r"(\[\^)(\d+)(\])":
                link_type = "footnote"
            elif pattern.pattern() == r"(@\w+)":
                link_type = "tag"
            
            if not link_type:
                continue

            it = pattern.globalMatch(block_text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart(0)
                end = match.capturedEnd(0)

                if start <= pos_in_block < end:
                    link_text = match.captured(0) if link_type == 'tag' else match.captured(2)
                    return link_type, link_text

        return None, None

    def mousePressEvent(self, event):
        if event and event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            link_type, link_text = self.get_link_at_position(cursor.position())
            
            if link_type and link_text:
                if link_type == "wikilink":
                    self.wikilink_clicked.emit(link_text)
                elif link_type == "footnote":
                    self.footnote_clicked.emit(link_text)
                elif link_type == "tag":
                    self.tag_clicked.emit(link_text)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        link_type, _ = self.get_link_at_position(cursor.position())
        if link_type:
            self.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        super().mouseMoveEvent(event)
