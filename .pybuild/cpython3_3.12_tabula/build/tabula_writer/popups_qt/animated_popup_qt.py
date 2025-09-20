from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal

class AnimatedPopup(QDialog):
    """A QDialog base class that fades in when shown."""
    finished_with_result = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = None

    def show_animated(self):
        """Shows the dialog with a fade-in animation."""
        self.setWindowOpacity(0.0)
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.finished.connect(self.on_finished)
        
        self.animation.start()
        self.open()

    def on_finished(self, result):
        """Emits our custom signal when the dialog is closed."""
        self.finished_with_result.emit(result)
