# tabula_writer/panels_qt/editor_panel_qt.py
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import pyqtSignal, QTimer
from .base_panel_qt import BasePanel
from ..popups_qt.comment_popup_qt import CommentPopup
import os
import re

class EditorPanel(BasePanel):
    headers_updated = pyqtSignal(list)
    file_saved = pyqtSignal(str, str)

    def __init__(self, app_instance):
        super().__init__(app_instance, framed=True, header_text="Editor")
        
        self.setObjectName("EditorPanel")
        self.current_path = None
        self.current_footnotes = set()
        
        self.is_focus_mode = False

        self.header_update_timer = QTimer(self)
        self.header_update_timer.setSingleShot(True)
        self.header_update_timer.setInterval(500)
        self.header_update_timer.timeout.connect(self._scan_and_update_headers)

        self.rehighlight_timer = QTimer(self)
        self.rehighlight_timer.setSingleShot(True)
        self.rehighlight_timer.setInterval(300)
        self.rehighlight_timer.timeout.connect(self.highlighter.rehighlight)

    def toggle_text_format(self, format_type):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        text = cursor.selectedText()
        marker = ""
        if format_type == 'bold':
            marker = "**"
        elif format_type == 'italic':
            marker = "*"
        
        if text.startswith(marker) and text.endswith(marker):
            cursor.insertText(text[len(marker):-len(marker)])
        else:
            cursor.insertText(f"{marker}{text}{marker}")
        
        self.text_edit.setTextCursor(cursor)

    def toggle_focus_mode(self):
        self.is_focus_mode = not self.is_focus_mode
        self.text_edit.toggle_typewriter_blur(self.is_focus_mode)
        self.app.status_bar.showMessage(f"Focus Mode {'On' if self.is_focus_mode else 'Off'}", 2000)

    def load_file(self, path):
        if self.is_focus_mode:
            self.toggle_focus_mode()
        
        self.current_path = path
        if not path:
             self.text_edit.clear()
             self.text_modified = False
             return []

        try:
            with open(path, "r", encoding="utf-8") as f: content = f.read()
            
            self.text_edit.textChanged.disconnect()
            self.text_edit.setPlainText(content)
            self.text_edit.textChanged.connect(self.on_text_changed)
            
            self.current_footnotes = set(re.findall(r'\[\^(\d+)\]', content))
            headers = re.findall(r'^(#+\s*)(.*)', content, re.MULTILINE)

            self.text_modified = False
            self.save_status_changed.emit()
            self.word_count_changed.emit()
            
            return headers
        except Exception as e:
            self.text_edit.setPlainText(f"Error loading file: {e}")
            self.current_path = None
            self.current_footnotes = set()
            return [] 

    def on_text_changed(self):
        super().on_text_changed()

        self.header_update_timer.start()
        self.rehighlight_timer.start()

        if not self.current_path:
            return

        new_content = self.get_content()
        new_footnotes = set(re.findall(r'\[\^(\d+)\]', new_content))
        deleted_footnotes = self.current_footnotes - new_footnotes
        if deleted_footnotes:
            self.app.delete_comments_for_footnotes(list(deleted_footnotes), self.current_path)
        self.current_footnotes = new_footnotes
    
    def _scan_and_update_headers(self):
        content = self.get_content()
        headers = re.findall(r'^(#+\s*)(.*)', content, re.MULTILINE)
        self.headers_updated.emit(headers)

    def save_file(self):
        if self.current_path and self.text_modified:
            try:
                content_to_save = self.get_content()
                with open(self.current_path, "w", encoding="utf-8") as f:
                    f.write(content_to_save)
                self.text_modified = False
                self.save_status_changed.emit()
                self.file_saved.emit(self.current_path, content_to_save)
                return True
            except Exception as e:
                QMessageBox.critical(self.app, "Auto-Save Error", f"Failed to save document:\n{self.current_path}\n\nError: {e}")
        return False
        
    def insert_footnote(self):
        if not self.current_path:
            QMessageBox.warning(self, "Footnote Error", "Please save the document before adding a footnote.")
            return

        content = self.get_content()
        existing_numbers = [int(n) for n in re.findall(r'\[\^(\d+)\]', content)]
        next_num = max(existing_numbers) + 1 if existing_numbers else 1

        self.text_edit.textCursor().insertText(f"[^{next_num}]")
        
        dialog = CommentPopup(next_num, self.app)
        dialog.comment_saved.connect(self.app._save_comment_from_popup)
        dialog.show_animated()
