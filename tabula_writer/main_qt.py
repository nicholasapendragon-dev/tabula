import sys
import os
import re
import datetime
import tempfile
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout,
                             QMessageBox, QDialog, QStatusBar, QLabel, QFileDialog, QSplashScreen)
from PyQt6.QtGui import QShortcut, QKeySequence, QAction, QPixmap
from PyQt6.QtCore import Qt, QTimer, QThreadPool, QMetaObject, Q_ARG, QEvent, QObject, pyqtProperty, QPropertyAnimation, QEasingCurve, QCoreApplication

from .utils.project_loader import load_project
from .utils.email_sender import send_email
from .utils.config_manager import load_config, save_config
from .utils.exporter import export_to_docx, export_to_pdf
from .utils.worker_qt import Worker
from .utils.search_indexer import SearchIndexer
from .utils.pomodoro_timer_qt import PomodoroTimer
from .panels_qt.chapter_panel_qt import ChapterPanel
from .panels_qt.editor_panel_qt import EditorPanel
from .panels_qt.notes_panel_qt import NotesPanel
from .popups_qt.save_popup_qt import SavePopup
from .popups_qt.search_popup_qt import SearchPopup
from .popups_qt.tag_popup_qt import TagPopup
from .popups_qt.wikilink_popup_qt import WikiLinkPopup
from .popups_qt.export_popup_qt import ExportPopup
from .popups_qt.comment_popup_qt import CommentPopup
from .popups_qt.full_comment_viewer_popup_qt import FullCommentViewerPopup
from .popups_qt.email_popup_qt import EmailPopup
from .popups_qt.pomodoro_popup_qt import PomodoroPopup
from .popups_qt.wifi_popup_qt import WifiPopup
from .popups_qt.bluetooth_popup_qt import BluetoothPopup
from .popups_qt.file_dialog_popup_qt import FileDialogPopup

class FocusTracker(QObject):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.last_focused_panel = ""

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.FocusIn:
            current_panel = self.main_window.get_focused_panel_name()
            if current_panel != self.last_focused_panel:
                if current_panel == "document":
                    self.main_window.animate_document_panel(expand=True)
                else:
                    self.main_window.animate_document_panel(expand=False)
                self.last_focused_panel = current_panel
        return super().eventFilter(watched, event)


class WriterDeckApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.drag_pos = None

        # --- FONT SIZE ADJUSTMENT ---
        self.base_font_size = 36 # Increased by 4 points
        
        self.theme = {
            'bg': '#fbfaf5',
            'panel_bg': '#f2ede4',
            'widget_bg': '#fdfdf6',
            'text_fg': '#4d4d4d',
            'select_bg': '#a0522d',
            'accent_main': '#a0522d',
            'accent_positive': '#556b2f',
            'accent_negative': '#bc4749',
            'accent_red': '#bc4749',
            'accent_gray': '#C3B091',
            'link_beige': '#C3B091',
            'text_fg_light': '#fbfaf5',
        }

        self.config = load_config()
        self.project_path = self.config.get("project_path")

        if not self.project_path or not os.path.exists(self.project_path):
            self.project_path = self.prompt_for_project_directory()
            if not self.project_path:
                sys.exit()
            self.config["project_path"] = self.project_path
            save_config(self.config)

        self.directories, self.documents, self.notes_path = load_project(self.project_path)
        self.documents_path = os.path.join(self.project_path, "documents")

        self.threadpool = QThreadPool()
        self.search_indexer = SearchIndexer()
        self.current_search_worker = None
        self.pomodoro_timer = PomodoroTimer()
        
        self.is_searching = False
        
        self.panel_widths = {
            "document_expanded": 280,
            "document_minimized": 0,
        }
        self.animation = None
        self.font_animation = None

        self.init_ui()
        self.apply_stylesheet()
        self.create_actions()

        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(10000)

        QTimer.singleShot(50, self.run_startup_checks)

        self.focus_tracker = FocusTracker(self)
        QApplication.instance().installEventFilter(self.focus_tracker)

    def mousePressEvent(self, event):
        if self.status_bar.geometry().contains(event.pos()):
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

    @pyqtProperty(int)
    def documentPanelWidth(self):
        sizes = self.splitter.sizes()
        return sizes[0] if sizes else 0

    @documentPanelWidth.setter
    def documentPanelWidth(self, width):
        sizes = self.splitter.sizes()
        if not sizes or len(sizes) < 2: return
        
        delta = width - sizes[0]
        sizes[0] = width
        sizes[1] -= delta
        self.splitter.setSizes(sizes)

    def animate_document_panel(self, expand=True):
        if self.animation and self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        target_width = self.panel_widths["document_expanded"] if expand else self.panel_widths["document_minimized"]
        
        self.animation = QPropertyAnimation(self, b"documentPanelWidth")
        self.animation.setEndValue(target_width)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

    def prompt_for_project_directory(self):
        QMessageBox.information(self, "Welcome to Tabula", "Please select a folder to store your project files.")
        
        dialog = FileDialogPopup(self, start_path=os.path.expanduser("~"), title="Select Location for Project Folder", is_directory_mode=True)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            parent_dir = dialog.selected_path
            if parent_dir:
                try:
                    project_folder_name = "TabulaProject" 
                    new_path = os.path.join(parent_dir, project_folder_name)
                    os.makedirs(new_path, exist_ok=True)
                    return new_path
                except Exception as e:
                    QMessageBox.critical(self, "Creation Error", f"Could not create project directory.\n\nError: {e}")
                    return None

        QMessageBox.critical(self, "No Directory Selected", "Tabula cannot start without a project directory.")
        return None

    def run_startup_checks(self):
        self.run_rescan()

    def init_ui(self):
        self.setWindowTitle("Tabula")
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.create_status_bar()
        self.setStatusBar(self.status_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter, 1)

        self.document_panel = ChapterPanel(self)
        self.editor_panel = EditorPanel(self)
        self.notes_panel = NotesPanel(self)
        
        self.splitter.addWidget(self.document_panel)
        self.splitter.addWidget(self.editor_panel)
        self.splitter.addWidget(self.notes_panel)

        self.splitter.setSizes([220, 554, 250])
        self.splitter.setStretchFactor(1, 1)

        self.document_panel.document_selected.connect(self.load_document)
        
        for panel in [self.editor_panel, self.notes_panel.general_notes_view]:
            panel.word_count_changed.connect(self.update_word_count)
            panel.save_status_changed.connect(self.update_save_status)
            panel.wikilink_clicked.connect(self.on_wikilink_click)
            panel.footnote_clicked.connect(self.on_footnote_click)
            panel.tag_clicked.connect(self.on_tag_click)
        
        self.editor_panel.file_saved.connect(self.update_search_index)
        self.editor_panel.file_saved.connect(self.run_rescan)
        self.editor_panel.headers_updated.connect(self.document_panel.update_headers_for_current_doc)
        
        self.notes_panel.file_saved.connect(self.update_search_index)
        self.pomodoro_timer.time_updated.connect(self.update_pomodoro_display)
        self.pomodoro_timer.emit_update()

    def run_rescan(self):
        self.status_bar.showMessage("Refreshing document list...")
        worker = Worker(self.document_panel.scan_filesystem)
        worker.signals.result.connect(self.on_rescan_finished)
        worker.signals.error.connect(lambda err: QMessageBox.critical(self, "Error Scanning Files", str(err[1])))
        self.threadpool.start(worker)

    def on_rescan_finished(self, result):
        self.directories, self.documents = result
        self.document_panel.populate_tree(self.directories, self.documents)
        
        if self.editor_panel.current_path and self.editor_panel.current_path not in self.documents:
            self.editor_panel.load_file(None)

        self.status_bar.showMessage("Rebuilding search index...", 3000)
        index_worker = Worker(self.search_indexer.build_index, self._get_all_project_files())
        index_worker.signals.finished.connect(lambda: self.status_bar.showMessage("Ready", 2000))
        self.threadpool.start(index_worker)

        if not self.editor_panel.current_path:
            if self.documents:
                self.load_document(self.documents[0])

    def update_search_index(self, path, content):
        self.threadpool.start(Worker(self.search_indexer.update_file, path, content))

    def apply_stylesheet(self):
        self.editor_panel.text_edit.set_font_size(self.base_font_size)
        self.editor_panel.highlighter.rehighlight()

        qss = f"""
            QMainWindow, QWidget {{
                background-color: {self.theme['bg']};
                font-family: Georgia;
                color: {self.theme['text_fg']};
            }}
            QSplitter::handle {{
                background-color: {self.theme['bg']};
                width: 2px;
            }}
            QFrame {{
                border-radius: 15px;
                border: 1px solid #e3d9c9;
            }}
            QFrame#EditorPanel {{ background-color: {self.theme['panel_bg']}; }}
            QFrame#ChapterPanel {{ background-color: #B2A68D; }}
            QFrame#NotesPanel {{ background-color: #9DBA94; }}
            #PanelHeader {{
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 15px 5px 15px;
                background-color: transparent;
                border-bottom: 1px solid #e3d9c9;
            }}
            #EditorPanel #PanelHeader {{
                background-color: #7297A0;
                color: {self.theme['text_fg_light']};
                border-bottom: 1px solid #7297A0;
            }}
            QTextEdit, QLineEdit {{
                background-color: {self.theme['widget_bg']};
                border-radius: 10px;
                border: 1px solid #e3d9c9;
                padding: 15px;
                font-size: {self.base_font_size}pt; /* Use base_font_size here for consistency */
            }}
            QStatusBar {{
                background-color: {self.theme['bg']};
                border-top: 1px solid #e3d9c9;
            }}
            QStatusBar QLabel {{
                color: {self.theme['text_fg']};
                font-size: 12pt;
                border: none;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {self.theme['accent_gray']};
                color: {self.theme['text_fg']};
                border: none;
                padding: 8px 20px;
                font-size: 14pt;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #A99A7F; }}
            QPushButton:focus {{
                background-color: {self.theme['select_bg']};
                color: {self.theme['text_fg_light']};
                outline: none;
            }}
        """
        self.setStyleSheet(qss)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.pomodoro_label = QLabel("🍅 25:00"); self.save_status_label = QLabel("✓")
        self.words_label = QLabel("0 words"); self.file_label = QLabel("No Document")
        self.status_bar.addWidget(self.pomodoro_label)
        self.status_bar.addPermanentWidget(self.save_status_label)
        self.status_bar.addPermanentWidget(self.words_label)
        self.status_bar.addPermanentWidget(self.file_label)

    def update_pomodoro_display(self, time_str, is_work, is_running):
        self.pomodoro_label.setText(f"{'🍅' if is_work else '☕'} {time_str}")
        color = self.theme['accent_positive'] if is_work else self.theme['accent_main']
        if not is_running: color = self.theme['text_fg']
        self.pomodoro_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_word_count(self):
        active_panel_name = self.get_focused_panel_name()
        content, current_file = "", "No File"
        if active_panel_name == "editor":
            content = self.editor_panel.get_content()
            if self.editor_panel.current_path: current_file = os.path.basename(self.editor_panel.current_path)
        elif active_panel_name == "notes":
            content = self.notes_panel.get_content()
            current_file = "_GeneralNotes.md"
        word_count = len(content.split())
        self.words_label.setText(f"{word_count:,} words")
        self.file_label.setText(current_file)

    def update_save_status(self):
        is_modified = self.editor_panel.text_modified or self.notes_panel.general_notes_view.text_modified
        self.save_status_label.setText("●" if is_modified else "✓")
        self.save_status_label.setStyleSheet(f"color: {self.theme['accent_positive'] if not is_modified else '#e6d9b1'};")

    def create_actions(self):
        action_definitions = {
            "Quit": ("Ctrl+Q", self.close),
            "New Document": ("Ctrl+N", self.document_panel.create_new_document),
            "New Folder": ("Ctrl+Alt+F", self.document_panel.create_new_folder),
            "Save": ("Ctrl+S", self.show_save_popup),
            "Search": ("Ctrl+F", self.show_search_popup),
            "Export": ("Ctrl+Shift+X", self.show_export_popup),
            "Email": ("Ctrl+Shift+E", self.show_email_popup),
            "Action Key": ("Ctrl+O", self.on_action_key),
            "Pomodoro": ("Ctrl+P", self.show_pomodoro_popup),
            "Wifi": ("Ctrl+W", self.show_wifi_popup),
            "Bluetooth": ("Ctrl+Shift+B", self.show_bluetooth_popup),
            "Bold": ("Ctrl+B", lambda: self.editor_panel.toggle_text_format('bold')),
            "Italic": ("Ctrl+I", lambda: self.editor_panel.toggle_text_format('italic')),
            "Insert Footnote": ("Ctrl+M", self.editor_panel.insert_footnote),
            "Focus Mode": ("Ctrl+T", self.editor_panel.toggle_focus_mode),
            "Delete Item": ("Ctrl+Shift+D", self.document_panel.delete_selected_item),
            "Rename Item": ("Ctrl+R", self.document_panel.rename_selected_item),
            "Toggle Fullscreen": ("F11", self.toggle_fullscreen),
            "Increase Font Size": ("Ctrl+Shift++", self.increase_font_size),
            "Decrease Font Size": ("Ctrl+Shift+-", self.decrease_font_size),
            "Update Program": ("Ctrl+Shift+U", self.run_updater),
            # --- NEW PANEL NAVIGATION SHORTCUTS ---
            "Navigate Panel Left": ("Ctrl+Alt+Left", self.navigate_panels_left),
            "Navigate Panel Right": ("Ctrl+Alt+Right", self.navigate_panels_right),
        }
        
        actions = []
        for name, (shortcut, slot) in action_definitions.items():
            action = QAction(name, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(slot)
            actions.append(action)
            
        self.addActions(actions)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def navigate_panels_left(self):
        focused_panel = self.get_focused_panel_name()
        if focused_panel == "editor":
            self.focus_panel("document")
        elif focused_panel == "notes":
            self.focus_panel("editor")
        elif focused_panel == "document":
            self.focus_panel("notes") # Wrap around

    def navigate_panels_right(self):
        focused_panel = self.get_focused_panel_name()
        if focused_panel == "document":
            self.focus_panel("editor")
        elif focused_panel == "editor":
            self.focus_panel("notes")
        elif focused_panel == "notes":
            self.focus_panel("document") # Wrap around

    def _animate_font_size(self, new_size):
        if self.font_animation and self.font_animation.state() == QPropertyAnimation.State.Running:
            return

        current_size = self.editor_panel.text_edit.get_font_size()
        
        self.font_animation = QPropertyAnimation(self.editor_panel.text_edit, b"dynamicFontSize")
        self.font_animation.setDuration(150)
        self.font_animation.setStartValue(current_size)
        self.font_animation.setEndValue(new_size)
        self.font_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.font_animation.start()
        
        self.base_font_size = new_size # Update base_font_size to reflect current animated size

    def increase_font_size(self):
        new_size = self.base_font_size + 2
        self._animate_font_size(new_size)

    def decrease_font_size(self):
        new_size = max(8, self.base_font_size - 2)
        self._animate_font_size(new_size)
        
    def run_updater(self):
        reply = QMessageBox.question(self, "Update Application",
                                     "This will pull the latest version from GitHub and restart the application.\n\nProceed with update?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        self.status_bar.showMessage("Updating from GitHub...")
        QApplication.processEvents()

        pip_executable = os.path.join(os.path.dirname(sys.executable), 'pip')

        try:
            git_process = subprocess.run(['git', 'pull'], cwd=self.project_path, check=True, capture_output=True, text=True)
            pip_process = subprocess.run([pip_executable, 'install', '--force-reinstall', '.'], cwd=self.project_path, check=True, capture_output=True, text=True)

            QMessageBox.information(self, "Update Complete", "Application updated successfully. It will now restart.")
            QCoreApplication.quit()

        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred during the update process.\n\n"
            error_message += f"Command: {' '.join(e.cmd)}\n"
            error_message += f"Return Code: {e.returncode}\n\n"
            error_message += f"Output:\n{e.stdout}\n{e.stderr}"
            QMessageBox.critical(self, "Update Failed", error_message)
            self.status_bar.showMessage("Update failed.", 3000)

    def on_action_key(self):
        panel = getattr(self, f"{self.get_focused_panel_name()}_panel", self.editor_panel)
        if hasattr(panel, 'on_action_key'):
            panel.on_action_key()

    def load_document(self, path):
        if self.editor_panel.current_path and path and os.path.exists(path) and os.path.samefile(self.editor_panel.current_path, path):
            self.editor_panel.focus_text()
            return

        if path and os.path.exists(path):
            headers = self.editor_panel.load_file(path)
            self.document_panel.update_headers_for_current_doc(headers)
            self.notes_panel.load_comments_for_document(path)
            self.document_panel.select_document_by_path(path)
            self.update_word_count()
        else:
            QMessageBox.warning(self, "File Not Found", f"The document at the path could not be found:\n{path}")
            self.document_panel.update_headers_for_current_doc([])
            self.run_rescan()

    def auto_save(self):
        self.editor_panel.save_file()
        self.notes_panel.save_notes()

    def _save_comment_from_popup(self, footnote_number, comment_text):
        if not self.editor_panel.current_path: return
        doc_base = os.path.splitext(os.path.basename(self.editor_panel.current_path))[0]
        sanitized_doc = re.sub(r'[^\w\-_\.]', '_', doc_base)
        comments_dir = os.path.join(self.notes_path, 'comments', sanitized_doc)
        os.makedirs(comments_dir, exist_ok=True)
        comment_path = os.path.join(comments_dir, f"{sanitized_doc}_comment_{footnote_number}.md")
        content = f"# Comment for [^{footnote_number}]\nReferencing: '{os.path.basename(self.editor_panel.current_path)}'\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{comment_text.strip()}\n"
        with open(comment_path, "w", encoding="utf-8") as f: f.write(content)
        self.notes_panel.load_comments_for_document(self.editor_panel.current_path)

    def delete_comments_for_footnotes(self, footnote_numbers, doc_path):
        if not doc_path: return
        doc_base = os.path.splitext(os.path.basename(doc_path))[0]
        sanitized_doc = re.sub(r'[^\w\-_\.]', '_', doc_base)
        comments_dir = os.path.join(self.notes_path, 'comments', sanitized_doc)
        for num in footnote_numbers:
            path = os.path.join(comments_dir, f"{sanitized_doc}_comment_{num}.md")
            if os.path.exists(path): os.remove(path)
        self.notes_panel.load_comments_for_document(doc_path)

    def get_focused_panel_name(self):
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            if self.document_panel.isAncestorOf(focused_widget): return "document"
            if self.notes_panel.isAncestorOf(focused_widget): return "notes"
        return "editor"
    
    def focus_panel(self, panel_name):
        panel = getattr(self, f"{panel_name}_panel", self.editor_panel)
        if hasattr(panel, 'focus_text'):
            panel.focus_text()
        elif hasattr(panel, 'focus_list'):
            panel.focus_list()

    def _get_all_project_files(self):
        files_info = [{'path': p, 'type': 'document', 'name': os.path.splitext(os.path.basename(p))[0]} for p in self.documents]
        notes_main = os.path.join(self.notes_path, "_GeneralNotes.md")
        if os.path.exists(notes_main):
            files_info.append({'path': notes_main, 'type': 'note', 'name': '_GeneralNotes'})
        return files_info

    def on_wikilink_click(self, link):
        paths = self.search_indexer.get_occurrences_for_wikilink(link)
        if not paths:
            QMessageBox.information(self, "Not Found", f"No occurrences of '[[{link}]]' were found in the project.")
            return
        matches = [f for f in self._get_all_project_files() if f['path'] in paths] # FIXED: Removed extra 'f'
        if not matches:
            QMessageBox.information(self, "Not Found", f"No occurrences of '[[{link}]]' were found in the project.")
            return
        dialog = WikiLinkPopup(link, matches, self.load_document, self)
        dialog.show_animated()

    def on_footnote_click(self, num):
        if not self.editor_panel.current_path: return
        data = self.notes_panel.get_comment_data_by_number(num)
        if data: FullCommentViewerPopup(data, self).show_animated()
        else: QMessageBox.information(self, "Not Found", f"Comment for [^{num}] not found.")

    def on_tag_click(self, tag):
        paths = self.search_indexer.get_files_for_tag(tag)
        matches = [f for f in self._get_all_project_files() if f['path'] in paths] # FIXED: Removed extra 'f'
        if matches: TagPopup(tag[1:], matches, self.load_document, self).show_animated()

    def _get_footnotes_for_export(self):
        footnotes = {}
        if not self.editor_panel.current_path: return footnotes
        for comment in self.notes_panel.loaded_comments:
            footnotes[comment['footnote_number']] = comment['body_text']
        return footnotes

    def show_export_popup(self):
        if not self.editor_panel.current_path:
            QMessageBox.warning(self, "Export Error", "Please save the document before exporting.")
            return
        name = os.path.splitext(os.path.basename(self.editor_panel.current_path))[0]
        dialog = ExportPopup(name, self)
        dialog.finished.connect(lambda res: res == QDialog.DialogCode.Accepted and self.run_export(dialog.get_selected_format(), name, dialog))
        dialog.show_animated()

    def run_export(self, fmt, name, dialog):
        start_dir = os.path.dirname(self.editor_panel.current_path) if self.editor_panel.current_path else self.documents_path
        path, _ = QFileDialog.getSaveFileName(self, f"Export as {fmt.upper()}", os.path.join(start_dir, f"{name}.{fmt}"), f"{fmt.upper()} Files (*.{fmt})")
        if path:
            try:
                content = self.editor_panel.get_content()
                footnotes = self._get_footnotes_for_export()
                if fmt == "docx":
                    export_to_docx(content, path, footnotes=footnotes)
                elif fmt == "pdf":
                    export_to_pdf(content, path, footnotes=footnotes) # Assuming export_to_pdf also handles footnotes
                QMessageBox.information(self, "Export Successful", f"Document exported to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export document:\n{e}")

    def show_save_popup(self):
        dialog = SavePopup(self)
        dialog.exec()

    def show_search_popup(self):
        if self.is_searching: return
        self.is_searching = True
        dialog = SearchPopup(self.search_indexer, self._get_all_project_files(), self.load_document, self)
        dialog.finished.connect(lambda: self.on_search_popup_closed())
        dialog.show_animated()

    def on_search_popup_closed(self):
        self.is_searching = False

    def show_pomodoro_popup(self):
        dialog = PomodoroPopup(self.pomodoro_timer, self)
        dialog.show_animated()
    
    def show_email_popup(self):
        dialog = EmailPopup(self)
        dialog.show_animated()

    def show_wifi_popup(self):
        dialog = WifiPopup(self)
        dialog.show_animated()
    
    def show_bluetooth_popup(self):
        dialog = BluetoothPopup(self)
        dialog.show_animated()

    def show_tag_popup(self):
        pass # Placeholder for future direct tag popup access

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    # Splash screen
    splash_pix = QPixmap(os.path.join(os.path.dirname(__file__), 'assets', 'splash.png'))
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    QApplication.processEvents()

    main_win = WriterDeckApp()
    main_win.show()
    main_win.showFullScreen() # ADDED THIS LINE
    splash.finish(main_win)
    sys.exit(app.exec())
