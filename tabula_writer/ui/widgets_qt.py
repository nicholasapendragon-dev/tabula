from PyQt6.QtWidgets import QRadioButton, QApplication, QFrame, QListWidget, QSpinBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QPainter, QColor, QBrush

class NavigableRadioButton(QRadioButton):
    """
    A custom radio button that allows selection with the Enter key and then
    advances focus. It also handles arrow key navigation within its group
    (Left/Right) and to exit the group (Up/Down).
    """
    def keyPressEvent(self, event):
        key = event.key()
        
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.setChecked(True)
            tab_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
            QApplication.postEvent(self, tab_event)
            event.accept()
            return

        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            is_next = key == Qt.Key.Key_Right
            self.focusNextPrevChild(is_next)
            event.accept()
            return
            
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            event.ignore() 
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

class NavigableListWidget(QListWidget):
    """
    A custom QListWidget that uses Up/Down arrows for internal selection.
    Pressing Enter advances focus to the next widget.
    """
    def keyPressEvent(self, event):
        key = event.key()
        
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.focusNextChild()
            event.accept()
            return
            
        super().keyPressEvent(event)

class NavigableSpinBox(QSpinBox):
    """
    A custom QSpinBox that advances focus when Enter is pressed.
    """
    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # On Enter, advance focus to the next widget in the tab order.
            self.focusNextChild()
            event.accept()
            return
        
        # Handle all other keys (like up/down arrows for changing value) normally.
        super().keyPressEvent(event)

class RoundedFrame(QFrame):
    """
    A custom QFrame that draws itself with rounded corners.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 15
        self.background_color = QColor("#FFFFFF")

    def set_properties(self, radius, background_color):
        self.radius = radius
        self.background_color = QColor(background_color)
        self.update() # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.background_color))
        painter.drawRoundedRect(self.rect(), self.radius, self.radius)
