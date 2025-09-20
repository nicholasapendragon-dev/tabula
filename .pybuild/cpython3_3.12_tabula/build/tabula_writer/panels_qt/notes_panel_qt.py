# tabula_writer/panels_qt/notes_panel_qt.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget, QScrollArea,
                             QLabel, QMessageBox, QFrame)
from .base_panel_qt import BasePanel
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
import os
import re
from ..popups_qt.full_comment_viewer_popup_qt import FullCommentViewerPopup
from ..utils.nav_qt import handle_panel_navigation

class CommentPreviewWidget(QWidget):
    def __init__(self, comment_data, parent_panel):
        super().__init__(parent_panel)
        self.notes_panel = parent_panel
        self.comment_data = comment_data
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAutoFillBackground(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        text = f"<b>[^{comment_data['footnote_number']}]</b> - {comment_data['body_text'][:50]}..."
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = self.notes_panel.app.theme
        
        if self.hasFocus():
            bg_color = QColor(theme['select_bg'])
            border_color = QColor(theme['select_bg'])
        else:
            bg_color = QColor(theme['widget_bg'])
            border_color = QColor(theme['panel_bg'])

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)
        
        super().paintEvent(event)

    def focusInEvent(self, event):
        self.label.setStyleSheet("background: transparent; border: none; color: {};".format(self.notes_panel.app.theme['text_fg_light']))
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.label.setStyleSheet("background: transparent; border: none; color: {};".format(self.notes_panel.app.theme['text_fg']))
        self.update()
        super().focusOutEvent(event)

    def open_full_view(self):
        dialog = FullCommentViewerPopup(self.comment_data, self.notes_panel.app)
        dialog.show_animated()

    def mouseDoubleClickEvent(self, event):
        self.open_full_view()
        
    def keyPressEvent(self, event):
        if handle_panel_navigation(self.notes_panel, event):
            event.accept()
            return
            
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.open_full_view()
        elif event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.notes_panel.navigate_comment_list(self, event.key())
        else:
            super().keyPressEvent(event)

class NotesPanel(QFrame):
    word_count_changed = pyqtSignal()
    save_status_changed = pyqtSignal()
    file_saved = pyqtSignal(str, str)
    
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.setObjectName("NotesPanel")
        
        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.text_modified = False
        self.loaded_comments = []
        self.current_note = None
        
        self.main_note_path = os.path.join(self.app.notes_path, "_GeneralNotes.md")
        
        header_label = QLabel("Notes")
        header_label.setObjectName("PanelHeader")
        content_layout.addWidget(header_label)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        self.general_notes_view = BasePanel(self.app, framed=False, header_text=None)
        self.stacked_widget.addWidget(self.general_notes_view)
        
        self.comments_view_scroll = QScrollArea()
        self.comments_view_scroll.setWidgetResizable(True)

        comments_container = QWidget()
        comments_container.setStyleSheet("background: transparent;")
        
        self.comments_layout = QVBoxLayout(comments_container)
        self.comments_layout.setContentsMargins(15, 15, 15, 15)
        self.comments_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.comments_view_scroll.setWidget(comments_container)
        self.stacked_widget.addWidget(self.comments_view_scroll)

        self.stacked_widget.setStyleSheet("background-color: transparent;")
        self.general_notes_view.setStyleSheet("background-color: transparent;")
        self.comments_view_scroll.setStyleSheet("background-color: transparent; border: none;")

        self.load_main_note()

    def load_main_note(self):
        try:
            if os.path.exists(self.main_note_path):
                with open(self.main_note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.general_notes_view.text_edit.setPlainText(content)
            else:
                placeholder_text = "# General Notes\n\n- This is the main notes file for your project."
                with open(self.main_note_path, 'w', encoding='utf-8') as f:
                    f.write(placeholder_text)
                self.general_notes_view.text_edit.setPlainText(placeholder_text)
        except Exception as e:
            QMessageBox.critical(self.app, "Notes Error", f"Could not load or create the main notes file.\n\nError: {e}")
            self.general_notes_view.text_edit.setPlainText("")
        
        self.general_notes_view.text_modified = False

    def load_comments_for_document(self, document_path):
        self.loaded_comments.clear()
        while self.comments_layout.count():
            child = self.comments_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            
        doc_base_name = os.path.splitext(os.path.basename(document_path))[0]
        sanitized_doc_name = re.sub(r'[^\w\-_\.]', '_', doc_base_name)
        comments_dir = os.path.join(self.app.notes_path, 'comments', sanitized_doc_name)

        no_comments_label = QLabel("No comments for this document.")
        no_comments_label.setStyleSheet("background-color: transparent; border: none;")
        
        if not os.path.exists(comments_dir) or not os.listdir(comments_dir):
            self.comments_layout.addWidget(no_comments_label)
        else:
            comment_files = sorted(os.listdir(comments_dir))
            for filename in comment_files:
                if filename.endswith(".md"):
                    path = os.path.join(comments_dir, filename)
                    with open(path, 'r', encoding='utf-8') as f: full_text = f.read()
                    fn_match = re.search(r'\[\^(\d+)\]', full_text)
                    if fn_match:
                        body = "\n".join([line for line in full_text.split('\n') if not (line.startswith('#') or line.startswith('Referencing:') or line.startswith('Date:'))])
                        comment_data = {
                            'footnote_number': fn_match.group(1), 
                            'body_text': body.strip(),
                            'full_text': full_text,
                            'path': path
                        }
                        self.loaded_comments.append(comment_data)
                        preview = CommentPreviewWidget(comment_data, self)
                        self.comments_layout.addWidget(preview)
        
        self.stacked_widget.setCurrentWidget(self.comments_view_scroll)

    def get_comment_data_by_number(self, number):
        for data in self.loaded_comments:
            if data['footnote_number'] == number:
                return data
        return None

    def save_notes(self):
        if self.general_notes_view.text_modified:
            try:
                content = self.general_notes_view.get_content()
                with open(self.main_note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.general_notes_view.text_modified = False
                self.save_status_changed.emit()
                self.file_saved.emit(self.main_note_path, content)
                return True
            except Exception as e:
                QMessageBox.critical(self.app, "Auto-Save Error", f"Failed to save the main notes file:\n{self.main_note_path}\n\nError: {e}")
        return False
        
    def on_action_key(self):
        if self.stacked_widget.currentWidget() == self.general_notes_view:
            self.general_notes_view.on_action_key()

    def focus_text(self):
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'focus_text'):
            current_view.focus_text()
        elif current_view == self.comments_view_scroll:
            if self.comments_layout.count() > 0:
                first_comment = self.comments_layout.itemAt(0).widget()
                if isinstance(first_comment, CommentPreviewWidget):
                    QTimer.singleShot(0, first_comment.setFocus)
    
    def navigate_comment_list(self, current_widget, key):
        current_index = -1
        for i in range(self.comments_layout.count()):
            if self.comments_layout.itemAt(i).widget() == current_widget:
                current_index = i
                break
        if current_index == -1: return

        if key == Qt.Key.Key_Up:
            next_index = max(0, current_index - 1)
        elif key == Qt.Key.Key_Down:
            next_index = min(self.comments_layout.count() - 1, current_index + 1)
        else: return
            
        next_widget = self.comments_layout.itemAt(next_index).widget()
        if next_widget:
            next_widget.setFocus()

    def get_content(self):
        if self.stacked_widget.currentWidget() == self.general_notes_view:
            return self.general_notes_view.get_content()
        return ""
