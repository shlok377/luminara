import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QTimeEdit, QListWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QTime, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen

# --- INTERNAL STYLES & CONSTANTS ---
# (Moved here so no external files are needed)
NEON_TEAL = QColor("#00F2FF")
NEON_PURPLE = QColor("#BC13FE")
NEON_RED = QColor("#FF0055")
SECONDARY_TEXT_COLOR = QColor(200, 200, 200)
TEXT_COLOR = QColor(255, 255, 255)

class StyledButton(QPushButton):
    """A modern button with neon hover effects (Embedded directly)."""
    def __init__(self, text, color=NEON_TEAL, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Change color if pressed or hovered
        bg_color = self.color if self.isEnabled() else QColor(255, 255, 255, 20)
        text_color = QColor(0, 0, 0) if self.isEnabled() else TEXT_COLOR

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)

        painter.fillPath(path, bg_color)
        
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

# --- MAIN TIMER LOGIC ---

class ProductivityTimer(QWidget):
    """
    A self-contained widget that handles Timer, Stopwatch, and Alarm.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Tabs for switching modes
        self.tabs = QTabWidget()
        # Styling the tabs to look modern and flat
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: rgba(255, 255, 255, 0.1);
                color: #bbb;
                padding: 8px 15px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {NEON_TEAL.name()};
                color: black;
                font-weight: bold;
            }}
        """)

        # Initialize the three modes
        self.timer_tab = TimerMode()
        self.stopwatch_tab = StopwatchMode()
        self.alarm_tab = AlarmMode()

        # Add them to the tab view
        self.tabs.addTab(self.timer_tab, "⏳ Timer")
        self.tabs.addTab(self.stopwatch_tab, "⏱️ Stopwatch")
        self.tabs.addTab(self.alarm_tab, "⏰ Alarm")

        self.layout.addWidget(self.tabs)

class TimerMode(QWidget):
    """Standard Countdown Timer (Pomodoro Style)"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Large Display
        self.lbl_display = QLabel("25:00")
        self.lbl_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_display.setFont(QFont("Consolas", 40, QFont.Weight.Bold))
        self.lbl_display.setStyleSheet(f"color: {NEON_RED.name()};")
        
        # Start/Reset Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = StyledButton("Start", NEON_RED)
        self.btn_reset = StyledButton("Reset", SECONDARY_TEXT_COLOR)
        
        self.btn_start.clicked.connect(self.toggle_timer)
        self.btn_reset.clicked.connect(self.reset_timer)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_reset)

        # Quick Select Buttons (5m, 15m, 25m)
        quick_layout = QHBoxLayout()
        for mins in [5, 15, 25, 45]:
            btn = QPushButton(f"{mins}m")
            btn.setStyleSheet("background: rgba(255,255,255,0.1); color: white; border: none; padding: 5px;")
            btn.clicked.connect(lambda checked, m=mins: self.set_time(m))
            quick_layout.addWidget(btn)

        layout.addWidget(self.lbl_display)
        layout.addLayout(btn_layout)
        layout.addLayout(quick_layout)
        
        # Logic Variables
        self.total_seconds = 25 * 60
        self.current_seconds = self.total_seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_running = False

    def set_time(self, minutes):
        self.stop_timer()
        self.total_seconds = minutes * 60
        self.current_seconds = self.total_seconds
        self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.btn_start.setText("Pause")
        self.timer.start(1000) # Tick every 1000ms (1 second)

    def stop_timer(self):
        self.is_running = False
        self.btn_start.setText("Start")
        self.timer.stop()

    def reset_timer(self):
        self.stop_timer()
        self.current_seconds = self.total_seconds
        self.update_display()

    def update_timer(self):
        if self.current_seconds > 0:
            self.current_seconds -= 1
            self.update_display()
        else:
            self.stop_timer()
            self.lbl_display.setText("DONE!")

    def update_display(self):
        m, s = divmod(self.current_seconds, 60)
        self.lbl_display.setText(f"{m:02d}:{s:02d}")

class StopwatchMode(QWidget):
    """Precise Stopwatch with Lap function"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.lbl_display = QLabel("00:00.00")
        self.lbl_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_display.setFont(QFont("Consolas", 40, QFont.Weight.Bold))
        self.lbl_display.setStyleSheet(f"color: {NEON_TEAL.name()};")

        btn_layout = QHBoxLayout()
        self.btn_start = StyledButton("Start", NEON_TEAL)
        self.btn_lap = StyledButton("Lap", NEON_PURPLE)
        self.btn_reset = StyledButton("Reset", SECONDARY_TEXT_COLOR)

        self.btn_start.clicked.connect(self.toggle_stopwatch)
        self.btn_lap.clicked.connect(self.record_lap)
        self.btn_reset.clicked.connect(self.reset_stopwatch)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_lap)
        btn_layout.addWidget(self.btn_reset)

        # List to show Laps
        self.laps_list = QListWidget()
        self.laps_list.setStyleSheet("background: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); font-family: Consolas;")
        self.laps_list.setFixedHeight(100)

        layout.addWidget(self.lbl_display)
        layout.addLayout(btn_layout)
        layout.addWidget(self.laps_list)

        # Logic
        self.timer = QTimer()
        self.timer.setInterval(10) # 10ms precision for 0.01s accuracy
        self.timer.timeout.connect(self.update_stopwatch)
        self.time_elapsed_ms = 0
        self.is_running = False

    def toggle_stopwatch(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("Start")
            self.is_running = False
        else:
            self.timer.start()
            self.btn_start.setText("Stop")
            self.is_running = True

    def update_stopwatch(self):
        self.time_elapsed_ms += 10
        self.update_display()

    def update_display(self):
        # Calculate minutes, seconds, and centiseconds
        seconds = (self.time_elapsed_ms // 1000) % 60
        minutes = (self.time_elapsed_ms // 60000)
        milliseconds = (self.time_elapsed_ms % 1000) // 10
        self.lbl_display.setText(f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}")

    def record_lap(self):
        if self.is_running or self.time_elapsed_ms > 0:
            lap_time = self.lbl_display.text()
            self.laps_list.insertItem(0, f"Lap {self.laps_list.count() + 1}: {lap_time}")

    def reset_stopwatch(self):
        self.timer.stop()
        self.is_running = False
        self.time_elapsed_ms = 0
        self.btn_start.setText("Start")
        self.update_display()
        self.laps_list.clear()

class AlarmMode(QWidget):
    """Simple Alarm Clock"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.lbl_status = QLabel("No Alarm Set")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #aaa; font-size: 14px;")

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setFont(QFont("Segoe UI", 20))
        self.time_edit.setStyleSheet("background: white; color: black; border-radius: 5px;")
        self.time_edit.setTime(QTime.currentTime().addSecs(60)) # Default to 1 min later

        self.btn_set = StyledButton("Set Alarm", NEON_PURPLE)
        self.btn_set.clicked.connect(self.set_alarm)

        layout.addWidget(self.lbl_status)
        layout.addWidget(self.time_edit)
        layout.addWidget(self.btn_set)
        layout.addStretch()

        self.alarm_time = None
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_alarm)
        self.check_timer.start(1000)

    def set_alarm(self):
        self.alarm_time = self.time_edit.time()
        self.lbl_status.setText(f"Alarm set for {self.alarm_time.toString('HH:mm')}")
        self.lbl_status.setStyleSheet(f"color: {NEON_PURPLE.name()}; font-weight: bold;")

    def check_alarm(self):
        if self.alarm_time:
            now = QTime.currentTime()
            # Check if hour and minute match, and second is 0 (so it only rings once)
            if now.hour() == self.alarm_time.hour() and now.minute() == self.alarm_time.minute() and now.second() == 0:
                self.alarm_time = None
                self.lbl_status.setText("ALARM RINGING!")
                self.lbl_status.setStyleSheet(f"color: {NEON_RED.name()}; font-size: 18px; font-weight: bold;")
                QMessageBox.warning(self, "Alarm", "⏰ Time to wake up!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create the standalone window
    window = ProductivityTimer()
    window.setWindowTitle("Standalone Timer Test")
    window.resize(400, 500)
    
    # Manual Dark Theme for Standalone testing
    window.setStyleSheet(f"background-color: #141E30; color: white;")
    
    window.show()
    sys.exit(app.exec())