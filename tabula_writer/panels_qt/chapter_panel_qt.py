# tabula_writer/panels_qt/chapter_panel_qt.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QTreeWidgetItemIterator, QMessageBox, QInputDialog,
                             QLabel, QMenu, QDialog, QFrame, QStyledItemDelegate, QStyle)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QAction, QIcon, QPainter, QColor, QBrush, QPen
import os
import re
import shutil
from tabula_writer.utils.nav_qt import handle_panel_navigation
from tabula_writer.popups_qt.input_popup_qt import InputPopup

class CustomItemDelegate(QStyledItemDelegate):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(32)
        return size

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        
        depth = 0
        parent = index.parent()
        while parent.isValid():
            depth += 1
            parent = parent.parent()
        
        indentation = depth * 20

        painter.fillRect(rect, QColor("#B2A68D"))

        if option.state & QStyle.StateFlag.State_Selected or option.state & QStyle.StateFlag.State_HasFocus:
            bubble_color = QColor(self.theme['select_bg'])
            text_color = QColor(self.theme['text_fg_light'])
        else:
            bubble_color = QColor(self.theme['widget_bg'])
            text_color = QColor(self.theme['text_fg'])
        
        bubble_height = 26
        bubble_top = rect.top() + (rect.height() - bubble_height) // 2
        bubble_rect = rect.adjusted(indentation + 5, 0, -5, 0)
        bubble_rect.setTop(bubble_top)
        bubble_rect.setHeight(bubble_height)

        painter.setBrush(bubble_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bubble_rect, 8, 8)

        icon = index.data(Qt.ItemDataRole.DecorationRole)
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        icon_rect = bubble_rect.adjusted(8, 0, 0, 0)
        text_rect = bubble_rect.adjusted(30, 0, 0, 0)

        if icon:
            icon_size = 16
            icon_y = bubble_rect.top() + (bubble_rect.height() - icon_size) // 2
            
            paint_rect = icon_rect.adjusted(0, 0, 0, 0)
            paint_rect.setTop(icon_y)
            paint_rect.setHeight(icon_size)
            paint_rect.setWidth(icon_size)
            icon.paint(painter, paint_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        painter.setPen(text_color)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)

        painter.restore()

class DocumentTreeWidget(QTreeWidget):
    def __init__(self, parent_panel):
        super().__init__()
        self.parent_panel = parent_panel
        self.setObjectName("DocumentTreeWidget")

    def keyPressEvent(self, event):
        if handle_panel_navigation(self.parent_panel, event):
            event.accept()
            return

        key = event.key()
        modifiers = event.modifiers()
        
        current_item = self.currentItem()
        if not current_item and key not in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            if modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and key == Qt.Key.Key_N:
                self.parent_panel.create_new_folder()
                event.accept()
                return
        
        if not current_item:
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_R:
            if current_item.childCount() > 0:
                current_item.setExpanded(not current_item.isExpanded())
            event.accept()
            return
        
        if modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and key == Qt.Key.Key_N:
            self.parent_panel.create_new_folder()
            event.accept()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if current_item.data(0, Qt.ItemDataRole.UserRole) == "file":
                self.parent_panel.on_item_selected(current_item)
            elif current_item.data(0, Qt.ItemDataRole.UserRole) == "header":
                self.parent_panel.on_header_selected(current_item)
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        
        menu = QMenu(self)
        
        if item: 
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(self.parent_panel.rename_selected_item)
            menu.addAction(rename_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.parent_panel.delete_selected_item)
            menu.addAction(delete_action)
            menu.addSeparator()

        new_doc_action = QAction("New Document", self)
        new_doc_action.triggered.connect(self.parent_panel.create_new_document)
        menu.addAction(new_doc_action)

        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(self.parent_panel.create_new_folder)
        menu.addAction(new_folder_action)
        
        menu.addSeparator()
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.parent_panel.app.run_rescan)
        menu.addAction(refresh_action)

        menu.exec(event.globalPos())


class ChapterPanel(QWidget):
    document_selected = pyqtSignal(str)

    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.folder_icon = QIcon("assets/folder.svg")
        self.note_icon = QIcon("assets/note.svg")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container_frame = QFrame()
        container_frame.setObjectName("ChapterPanel")
        main_layout.addWidget(container_frame)

        content_layout = QVBoxLayout(container_frame)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        header_label = QLabel("Documents")
        header_label.setObjectName("PanelHeader")
        content_layout.addWidget(header_label)

        self.tree_widget = DocumentTreeWidget(self)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(0)
        self.tree_widget.setRootIsDecorated(False)
        
        self.tree_widget.setItemDelegate(CustomItemDelegate(self.tree_widget, self.app.theme))
        self.tree_widget.setStyleSheet("background-color: transparent; border: none;")

        self.tree_widget.itemDoubleClicked.connect(self.handle_item_double_click)
        content_layout.addWidget(self.tree_widget)

        self.tree_widget.addTopLevelItem(QTreeWidgetItem(["Loading..."]))

    def populate_tree(self, directories, files):
        self.tree_widget.clear()
        docs_path = self.app.documents_path
        
        path_map = {docs_path: self.tree_widget.invisibleRootItem()}

        for dir_path in sorted(directories):
            if dir_path == docs_path: continue
            parent_path, dir_name = os.path.split(dir_path)
            parent_item = path_map.get(parent_path)
            if parent_item:
                dir_item = QTreeWidgetItem(parent_item, [dir_name])
                dir_item.setIcon(0, self.folder_icon)
                dir_item.setData(0, Qt.ItemDataRole.UserRole, "folder")
                dir_item.setData(1, Qt.ItemDataRole.UserRole, dir_path)
                path_map[dir_path] = dir_item
        
        for file_path in files:
            parent_path, file_name = os.path.split(file_path)
            parent_item = path_map.get(parent_path)
            if parent_item:
                file_item = QTreeWidgetItem(parent_item, [os.path.splitext(file_name)[0]])
                file_item.setIcon(0, self.note_icon)
                file_item.setData(0, Qt.ItemDataRole.UserRole, "file")
                file_item.setData(1, Qt.ItemDataRole.UserRole, file_path)

        self.tree_widget.expandAll()
    
    def scan_filesystem(self):
        docs_path = self.app.documents_path
        directories = [docs_path]
        documents = []
        for root, dirs, files in os.walk(docs_path):
            for name in dirs:
                directories.append(os.path.join(root, name))
            for file in files:
                if file.endswith(".md"):
                    documents.append(os.path.join(root, file))
        documents.sort()
        return directories, documents

    def handle_item_double_click(self, item, column):
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        if item_type == "file":
            self.on_item_selected(item)
        elif item_type == "header":
            self.on_header_selected(item)
        elif item_type == "folder":
            item.setExpanded(not item.isExpanded())

    def on_item_selected(self, item):
        file_path = item.data(1, Qt.ItemDataRole.UserRole)
        self.document_selected.emit(file_path)
        
    def on_header_selected(self, item):
        header_text = item.data(0, Qt.ItemDataRole.WhatsThisRole)
        self.app.editor_panel.text_edit.find(header_text)
        self.app.editor_panel.text_edit.setFocus()

    def find_item_by_path(self, path):
        iterator = QTreeWidgetItemIterator(self.tree_widget)
        while iterator.value():
            item = iterator.value()
            if item.data(1, Qt.ItemDataRole.UserRole) == path:
                return item
            iterator += 1
        return None

    def select_document_by_path(self, path):
        item = self.find_item_by_path(path)
        if item:
            self.tree_widget.setCurrentItem(item)
            self.tree_widget.scrollToItem(item, QTreeWidget.ScrollHint.PositionAtTop)

    def update_headers_for_current_doc(self, headers):
        iterator = QTreeWidgetItemIterator(self.tree_widget, QTreeWidgetItemIterator.IteratorFlag.All)
        items_to_remove = []
        while iterator.value():
            item = iterator.value()
            parent = item.parent()
            if parent and item.data(0, Qt.ItemDataRole.UserRole) == "header":
                items_to_remove.append((parent, parent.indexOfChild(item)))
            iterator += 1
        
        for parent, index in reversed(items_to_remove):
            parent.takeChild(index)

        current_doc_path = self.app.editor_panel.current_path
        if not current_doc_path: return
        
        target_item = self.find_item_by_path(current_doc_path)
        if not target_item: return

        header_font = QFont("Georgia", 12)
        header_font.setItalic(True)
        for level, title in headers:
            item_text = "› " + title.strip()
            
            header_item = QTreeWidgetItem(target_item, [item_text])
            header_item.setFont(0, header_font)
            header_item.setData(0, Qt.ItemDataRole.UserRole, "header")
            header_item.setData(0, Qt.ItemDataRole.WhatsThisRole, title.strip())

        target_item.setExpanded(True)

    def focus_list(self):
        QTimer.singleShot(0, self.tree_widget.setFocus)

    def get_current_directory(self):
        current_item = self.tree_widget.currentItem()
        parent_path = self.app.documents_path
        
        if current_item:
            item_type = current_item.data(0, Qt.ItemDataRole.UserRole)
            item_path = current_item.data(1, Qt.ItemDataRole.UserRole)
            if item_type == "folder":
                parent_path = item_path
            elif item_type == "file":
                parent_path = os.path.dirname(item_path)
        
        return parent_path

    def create_new_folder(self):
        parent_path = self.get_current_directory()
        
        dialog = InputPopup("New Folder", "Enter folder name:", parent=self.app)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_text()
            if name:
                sanitized_name = re.sub(r'[^\w\s\-_\.]', '_', name).strip()
                if not sanitized_name:
                    QMessageBox.warning(self, "Invalid Name", "The folder name is invalid.")
                    return
                
                new_folder_path = os.path.join(parent_path, sanitized_name)
                if os.path.exists(new_folder_path):
                    QMessageBox.critical(self, "Error", f"A folder named '{sanitized_name}' already exists.")
                    return
                try:
                    os.makedirs(new_folder_path)
                    self.app.run_rescan()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create folder:\n{new_folder_path}\n\nError: {e}")
    
    def create_new_document(self):
        parent_path = self.get_current_directory()

        dialog = InputPopup("New Document", "Enter document name:", parent=self.app)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_text()
            if name:
                sanitized_name = re.sub(r'[^\w\s\-_\.]', '_', name).strip()
                if not sanitized_name:
                    QMessageBox.warning(self, "Invalid Name", "The document name is invalid.")
                    return

                filename = os.path.join(parent_path, f"{sanitized_name}.md")
                
                if os.path.exists(filename):
                    QMessageBox.critical(self, "Error", f"A document named '{sanitized_name}.md' already exists.")
                    return
                try:
                    content = f"# {sanitized_name}\n"
                    with open(filename, "w", encoding="utf-8") as f: 
                        f.write(content)
                    
                    self.app.run_rescan()
                    QTimer.singleShot(250, lambda: self.app.load_document(filename))

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create document:\n{filename}\n\nError: {e}")

    def delete_selected_item(self):
        item = self.tree_widget.currentItem()
        if not item: return

        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        item_path = item.data(1, Qt.ItemDataRole.UserRole)
        item_name = item.text(0)

        reply = QMessageBox.question(self, "Confirm Delete", 
            f"Are you sure you want to permanently delete '{item_name}'?\n\nThis action cannot be undone.")
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if item_type == "file":
                    os.remove(item_path)
                elif item_type == "folder":
                    shutil.rmtree(item_path)
                
                self.app.run_rescan()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete {item_type}: {e}")

    def rename_selected_item(self):
        item = self.tree_widget.currentItem()
        if not item: return

        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        old_path = item.data(1, Qt.ItemDataRole.UserRole)
        old_name_no_ext = os.path.splitext(item.text(0))[0]

        dialog = InputPopup(f"Rename {item_type.capitalize()}", "Enter new name:", old_name_no_ext, parent=self.app)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_text()
            if new_name and new_name != old_name_no_ext:
                sanitized_name = re.sub(r'[^\w\s\-_\.]', '_', new_name).strip()
                if not sanitized_name:
                    QMessageBox.warning(self, "Invalid Name", "The provided name is invalid.")
                    return
                
                parent_path = os.path.dirname(old_path)
                new_filename = sanitized_name
                if item_type == "file":
                    new_filename += ".md"
                new_path = os.path.join(parent_path, new_filename)

                if os.path.exists(new_path):
                    QMessageBox.critical(self, "Error", f"A {item_type} named '{new_filename}' already exists.")
                    return
                
                try:
                    is_renaming_current_file = (self.app.editor_panel.current_path == old_path)
                    
                    os.rename(old_path, new_path)
                    
                    self.app.run_rescan()

                    if is_renaming_current_file:
                        QTimer.singleShot(250, lambda: self.app.load_document(new_path))

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to rename {item_type}: {e}")
