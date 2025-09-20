# tabula_writer/utils/nav_qt.py
from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtWidgets import QLineEdit, QPushButton, QCheckBox, QRadioButton, QTextEdit
from tabula_writer.ui.widgets_qt import NavigableRadioButton, NavigableListWidget

def _focus_panel(app, panel_name):
    """Sets focus on the specified panel."""
    panel = getattr(app, f"{panel_name}_panel", app.editor_panel)
    if hasattr(panel, 'focus_text'):
        panel.focus_text()
    elif hasattr(panel, 'focus_list'):
        panel.focus_list()

def _navigate_panels(app, direction):
    """Calculates the next panel and focuses it."""
    current = app.get_focused_panel_name()
    if direction == "left":
        panel_map = {"notes": "editor", "editor": "document", "document": "notes"}
        next_panel = panel_map.get(current, "document")
    else:  # right
        panel_map = {"document": "editor", "editor": "notes", "notes": "document"}
        next_panel = panel_map.get(current, "editor")
    _focus_panel(app, next_panel)

def handle_panel_navigation(widget_with_app_ref, event):
    """
    Checks for Ctrl+Arrow keys and triggers panel navigation.
    """
    if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        if event.key() == Qt.Key.Key_Left:
            _navigate_panels(widget_with_app_ref.app, "left")
            return True
        elif event.key() == Qt.Key.Key_Right:
            _navigate_panels(widget_with_app_ref.app, "right")
            return True
    return False

# --- Popup Navigation Helpers ---

class _PopupEventFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyPress:
            # --- THIS IS THE FIX ---
            # If the widget is one of our special navigable widgets, let it handle
            # key presses itself first. Returning False passes the event along.
            if isinstance(watched, (NavigableListWidget, NavigableRadioButton)):
                return False

            dialog = self.parent()
            if event.key() == Qt.Key.Key_Down:
                dialog.focusNextPrevChild(True)
                return True
            elif event.key() == Qt.Key.Key_Up:
                dialog.focusNextPrevChild(False)
                return True
        
        return super().eventFilter(watched, event)

def install_popup_navigation_filter(dialog):
    event_filter = _PopupEventFilter(dialog)
    
    focusable_widgets = dialog.findChildren((
        QLineEdit, QPushButton, QCheckBox, QRadioButton, QTextEdit, NavigableListWidget
    ))
    for widget in focusable_widgets:
        widget.installEventFilter(event_filter)
