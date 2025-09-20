# popups_qt/file_dialog_popup_qt.py
from PyQt6.QtWidgets import (QApplication, QLabel, QPushButton, QLineEdit, QTreeWidget, 
                             QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QFrame,
                             QMessageBox, QTreeWidgetItemIterator, QDialog)
from PyQt6.QtCore import Qt
from .base_popup_qt import BasePopup
from .input_popup_qt import InputPopup # --- MODIFICATION: Import the new custom popup ---
import os
import time

class FileDialogTree(QTreeWidget):
    """A custom tree widget with enhanced keyboard navigation."""
    def __init__(self, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog
        self.last_enter_press_time = 0

    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            current_time = time.time()
            double_press_interval = QApplication.doubleClickInterval() / 1000.0

            if self.parent_dialog.is_directory_mode:
                self.parent_dialog.on_select_clicked()
            
            elif (current_time - self.last_enter_press_time) < double_press_interval:
                if not self.parent_dialog.is_directory_mode:
                    self.parent_dialog.filename_input.setFocus()
            
            else:
                self.parent_dialog.toggle_expand_current_item()
            
            self.last_enter_press_time = current_time
            event.accept()
            return
            
        if event.text().isalnum() and not self.parent_dialog.is_directory_mode:
            self.parent_dialog.filename_input.setFocus()
            self.parent_dialog.filename_input.setText(event.text())
            event.accept()
            return
            
        super().keyPressEvent(event)


class FileDialogLineEdit(QLineEdit):
    """A custom line edit with enhanced keyboard navigation."""
    def __init__(self, parent_dialog):
        super().__init__()
        self.parent_dialog = parent_dialog

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.parent_dialog.select_button.setFocus()
            event.accept()
            return
        
        if key == Qt.Key.Key_Up:
            self.parent_dialog.tree.setFocus()
            event.accept()
            return

        super().keyPressEvent(event)


class FileDialogPopup(BasePopup):
    def __init__(self, parent, start_path, title="Select File", is_directory_mode=False):
        super().__init__(theme=parent.theme, parent=parent)
        self.is_directory_mode = is_directory_mode
        self.setWindowTitle(title)
        self.setMinimumSize(600, 500)
        self.selected_path = None

        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        self.tree = FileDialogTree(self)
        self.tree.setHeaderHidden(True)
        self.tree.itemExpanded.connect(self.populate_children)
        self.tree.currentItemChanged.connect(self.on_item_selected)
        content_layout.addWidget(self.tree)
        
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        
        if not self.is_directory_mode:
            self.filename_input = FileDialogLineEdit(self)
            self.filename_input.setPlaceholderText("Double-Enter a folder, then type a filename...")
            bottom_layout.addWidget(self.filename_input)

        self.new_folder_button = QPushButton("New Folder (Ctrl+N)")
        self.new_folder_button.clicked.connect(self.create_new_folder)
        
        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.select_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        bottom_layout.addWidget(self.new_folder_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.cancel_button)
        bottom_layout.addWidget(self.select_button)
        
        content_layout.addWidget(bottom_frame)
        self.main_layout.addLayout(content_layout)

        self.populate_initial_tree(start_path)
        self.tree.setFocus()

    def keyPressEvent(self, event):
        """Handle global shortcuts for the popup."""
        if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.create_new_folder()
            event.accept()
            return
        super().keyPressEvent(event)

    def toggle_expand_current_item(self):
        """Expands or collapses the currently selected item in the tree."""
        current_item = self.tree.currentItem()
        if current_item:
            current_item.setExpanded(not current_item.isExpanded())

    def populate_initial_tree(self, start_path):
        self.tree.clear()
        path_parts = os.path.normpath(start_path).split(os.sep)
        
        current_path = ""
        parent_item = self.tree.invisibleRootItem()

        for part in path_parts:
            if not part and os.path.isabs(start_path):
                current_path = os.sep
                item = QTreeWidgetItem(parent_item, ["/"])
                item.setData(0, Qt.ItemDataRole.UserRole, "/")
                parent_item = item
                continue

            current_path = os.path.join(current_path, part)
            item = QTreeWidgetItem(parent_item, [part])
            item.setData(0, Qt.ItemDataRole.UserRole, current_path)
            parent_item = item
        
        self.populate_children(parent_item)
        self.tree.expandItem(parent_item)
        self.tree.setCurrentItem(parent_item)

    def populate_children(self, parent_item):
        if parent_item.childCount() > 0 and parent_item.child(0).text(0) != "Loading...":
            return

        parent_item.takeChildren()
        path = parent_item.data(0, Qt.ItemDataRole.UserRole)
        if not path or not os.path.isdir(path):
            return

        try:
            for name in sorted(os.listdir(path)):
                if name.startswith('.'): continue
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path):
                    child_item = QTreeWidgetItem(parent_item, [name])
                    child_item.setData(0, Qt.ItemDataRole.UserRole, full_path)
                    placeholder = QTreeWidgetItem(child_item, ["Loading..."])
        except PermissionError:
            parent_item.addChild(QTreeWidgetItem(["Permission Denied"]))

    def on_item_selected(self, current_item, previous_item):
        if not current_item: return
        path = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not self.is_directory_mode and os.path.isdir(path):
            self.filename_input.setText("")
        elif not self.is_directory_mode:
            self.filename_input.setText(os.path.basename(path))

    def create_new_folder(self):
        """Creates a new folder in the currently selected directory."""
        current_item = self.tree.currentItem()
        if not current_item: return

        parent_path = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not os.path.isdir(parent_path):
            parent_path = os.path.dirname(parent_path)

        # --- MODIFICATION: Use the custom InputPopup ---
        dialog = InputPopup("New Folder", "Enter folder name:", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_text()
            if name:
                try:
                    new_path = os.path.join(parent_path, name)
                    os.makedirs(new_path)
                    parent_item = self.find_item_by_path(parent_path)
                    if parent_item:
                        parent_item.takeChildren()
                        self.populate_children(parent_item)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not create folder:\n{e}")

    def find_item_by_path(self, path):
        it = QTreeWidgetItemIterator(self.tree)
        while it.value():
            item = it.value()
            if item.data(0, Qt.ItemDataRole.UserRole) == path:
                return item
            it += 1
        return None

    def on_select_clicked(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a directory or file.")
            return

        base_path = current_item.data(0, Qt.ItemDataRole.UserRole)

        if self.is_directory_mode:
            if os.path.isdir(base_path):
                self.selected_path = base_path
                self.accept()
            else:
                QMessageBox.warning(self, "Selection Error", "Please select a directory.")
            return

        filename = self.filename_input.text()
        if not filename:
            QMessageBox.warning(self, "No Filename", "Please enter a filename.")
            return
            
        if os.path.isdir(base_path):
            final_path = os.path.join(base_path, filename)
        else:
            final_path = os.path.join(os.path.dirname(base_path), filename)
        
        self.selected_path = final_path
        self.accept()
