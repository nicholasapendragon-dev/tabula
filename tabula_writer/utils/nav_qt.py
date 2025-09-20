# tabula_writer/utils/nav_qt.py
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QTextCursor

def handle_editor_navigation(editor_widget, event):
    cursor = editor_widget.textCursor()
    is_at_start = cursor.position() == 0
    is_at_end = cursor.position() == len(editor_widget.toPlainText())

    if event.key() == Qt.Key.Key_Left and is_at_start:
        editor_widget.parent_panel.app.focus_panel("document")
        return True

    if event.key() == Qt.Key.Key_Right and is_at_end:
        editor_widget.parent_panel.app.focus_panel("notes")
        return True

    return False

def handle_panel_navigation(panel_widget, event):
    if event.key() == Qt.Key.Key_Right or event.key() == Qt.Key.Key_Left:
        panel_widget.app.focus_panel("editor")
        return True
    return False

class PopupNavFilter(QObject):
    def __init__(self, popup, parent=None):
        super().__init__(parent)
        self.popup = popup

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                self.popup.focusNextPrevChild(event.key() not in (Qt.Key.Key_Left, Qt.Key.Key_Up))
                return True
        return super().eventFilter(obj, event)

def install_popup_navigation_filter(popup):
    popup._nav_filter = PopupNavFilter(popup)
    popup.installEventFilter(popup._nav_filter)
