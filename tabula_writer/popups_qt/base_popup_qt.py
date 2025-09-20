# tabula_writer/popups_qt/base_popup_qt.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor
from tabula_writer.utils.nav_qt import install_popup_navigation_filter

class BasePopup(QDialog):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.drag_pos = None

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(20, 20, 20, 20)

        self.shadow_frame = QFrame()
        self.shadow_frame.setObjectName("PopupFrame")
        self.shadow_frame.setStyleSheet(f"""
            #PopupFrame {{
                background-color: {self.theme['bg']};
                border: 1px solid {self.theme['select_bg']};
                border-radius: 15px;
            }}
        """)
        base_layout.addWidget(self.shadow_frame)

        self.main_layout = QVBoxLayout(self.shadow_frame)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(15)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.shadow_frame.setGraphicsEffect(shadow)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(150)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # --- MODIFICATION: Defer the filter installation to ensure all child widgets have been created ---
        # A single shot timer with a 0ms delay runs as soon as the event loop is idle,
        # which is after the subclass constructor has completed.
        QTimer.singleShot(0, lambda: install_popup_navigation_filter(self))

    def show_animated(self):
        """Shows the popup with a fade-in animation."""
        self.setWindowOpacity(0.0)
        self.show()
        self.animation.start()

    def keyPressEvent(self, event):
        """Closes the popup when the Escape key is pressed."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Initializes dragging the popup window."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Moves the popup window during a drag."""
        if self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Stops dragging the popup window."""
        self.drag_pos = None
        event.accept()
