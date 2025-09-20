# popups_qt/pomodoro_popup_qt.py
from PyQt6.QtWidgets import QLabel, QPushButton, QGridLayout, QFrame, QHBoxLayout
from .base_popup_qt import BasePopup
from tabula_writer.ui.widgets_qt import NavigableSpinBox

class PomodoroPopup(BasePopup):
    def __init__(self, timer_instance, theme, parent=None):
        super().__init__(theme=theme, parent=parent)
        self.timer = timer_instance
        self.setWindowTitle("Pomodoro Timer")

        layout = QGridLayout()
        layout.setSpacing(10)
        
        self.time_label = QLabel("25:00")
        self.time_label.setStyleSheet("font-size: 36pt; font-weight: bold;")
        layout.addWidget(self.time_label, 0, 0, 1, 2)

        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.timer.start_stop)
        layout.addWidget(self.start_stop_button, 0, 2)
        
        self.work_spinbox = self._add_spinbox_row(layout, 1, "Work Minutes:", self.timer.default_work_minutes)
        self.break_spinbox = self._add_spinbox_row(layout, 2, "Break Minutes:", self.timer.default_break_minutes)

        self.main_layout.addLayout(layout)
        
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.reset_button = QPushButton("Reset & Apply")
        self.reset_button.clicked.connect(self.reset_timer)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        self.main_layout.addWidget(button_container)
        
        self.timer.time_updated.connect(self.update_display)
        self.update_display(self.timer.time_left, self.timer.is_work_session, self.timer.is_running)

    def _add_spinbox_row(self, layout, row, label_text, value):
        layout.addWidget(QLabel(label_text), row, 0, 1, 2)
        spinbox = NavigableSpinBox()
        spinbox.setRange(1, 120)
        spinbox.setValue(value)
        layout.addWidget(spinbox, row, 2)
        return spinbox

    def reset_timer(self):
        self.timer.reset(self.work_spinbox.value(), self.break_spinbox.value())

    def update_display(self, time_left_or_str, is_work, is_running):
        if isinstance(time_left_or_str, int): # Handle both str and int inputs
            minutes = time_left_or_str // 60
            seconds = time_left_or_str % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
        else:
            time_str = time_left_or_str

        self.time_label.setText(time_str)
        self.start_stop_button.setText("Stop" if is_running else "Start")
