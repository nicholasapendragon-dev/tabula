from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class PomodoroTimer(QObject):
    """
    Manages the state and timing of a Pomodoro timer.
    Emits signals to update the UI with the current time and state.
    """
    # Signal arguments: (current_time_str, is_work_session, is_running)
    time_updated = pyqtSignal(str, bool, bool)

    def __init__(self, work_minutes=25, break_minutes=5, parent=None):
        super().__init__(parent)
        self.default_work_minutes = work_minutes
        self.default_break_minutes = break_minutes
        
        self.work_duration = self.default_work_minutes * 60
        self.break_duration = self.default_break_minutes * 60
        
        self.is_work_session = True
        self.is_running = False
        self.time_left = self.work_duration
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # Update every second
        self.timer.timeout.connect(self.update_timer)

    def start_stop(self):
        """Toggles the timer on and off."""
        if self.is_running:
            self.is_running = False
            self.timer.stop()
        else:
            self.is_running = True
            self.timer.start()
        self.emit_update()

    def reset(self, work_minutes=None, break_minutes=None):
        """
        Resets the timer to the beginning of a work session.
        Optionally updates the work and break durations.
        """
        self.is_running = False
        self.timer.stop()
        
        if work_minutes is not None:
            self.default_work_minutes = work_minutes
        if break_minutes is not None:
            self.default_break_minutes = break_minutes
            
        self.work_duration = self.default_work_minutes * 60
        self.break_duration = self.default_break_minutes * 60

        self.is_work_session = True
        self.time_left = self.work_duration
        self.emit_update()

    def update_timer(self):
        """Called every second by the QTimer to decrement the time."""
        if self.is_running:
            self.time_left -= 1
            if self.time_left < 0:
                self._switch_session()
            self.emit_update()

    def _switch_session(self):
        """Switches between work and break sessions."""
        self.is_work_session = not self.is_work_session
        self.time_left = self.work_duration if self.is_work_session else self.break_duration

    def emit_update(self):
        """Formats the time and emits the time_updated signal."""
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.time_updated.emit(time_str, self.is_work_session, self.is_running)
