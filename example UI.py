import sys
from PyQt6 import *
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect, QTextEdit, QCheckBox,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QColor, QPalette, QBrush, QLinearGradient, QPainter, QFont, QPen, QPainterPath

# Constants for Styling
BACKGROUND_GRADIENT_START = QColor("#141E30")
BACKGROUND_GRADIENT_END = QColor("#243B55")
NEON_TEAL = QColor("#00F2FF")
NEON_PURPLE = QColor("#BC13FE")
GLASS_COLOR = QColor(255, 255, 255, 15)  # Low opacity white
GLASS_BORDER = QColor(255, 255, 255, 40)
TEXT_COLOR = QColor(255, 255, 255)
SECONDARY_TEXT_COLOR = QColor(200, 200, 200)

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create path for rounded rect
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)

        # Fill with semi-transparent color
        painter.fillPath(path, GLASS_COLOR)

        # Draw border
        pen = QPen(GLASS_BORDER, 1)
        painter.setPen(pen)
        painter.drawPath(path)

class NeonToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw track
        track_color = NEON_TEAL if self.isChecked() else QColor(255, 255, 255, 30)
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 50, 26, 13, 13)

        # Draw thumb
        thumb_x = 26 if self.isChecked() else 2
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(thumb_x, 2, 22, 22)

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 65  # Example value
        self.setFixedSize(100, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background ring
        pen = QPen(QColor(255, 255, 255, 20), 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(10, 10, 80, 80, 0, 360 * 16)

        # Draw progress ring
        pen.setColor(NEON_TEAL)
        painter.setPen(pen)
        # Angle is in 1/16th of a degree. Start at 90 deg (12 o'clock) = 90 * 16
        # Span is negative for clockwise
        span = int(-self.value * 3.6 * 16)
        painter.drawArc(10, 10, 80, 80, 90 * 16, span)

        # Draw Text
        painter.setPen(TEXT_COLOR)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self.value}%")

class StyledButton(QPushButton):
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg_color = NEON_TEAL if self.primary else QColor(255, 255, 255, 20)
        text_color = QColor(0, 0, 0) if self.primary else TEXT_COLOR

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)

        painter.fillPath(path, bg_color)
        
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academia Assistant")
        self.resize(1100, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Center on screen logic could go here
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Grid)
        self.main_layout = QGridLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- Sidebar (Left) ---
        self.setup_sidebar()

        # --- Dashboard Grid (Right) ---
        # Top-Left: AI Cheatsheet
        self.setup_cheatsheet_card()
        
        # Bottom-Left: Notes & Mini-Tests
        self.setup_notes_card()

        # Top-Right: Productivity
        self.setup_productivity_card()

        # Bottom-Right: Study Tasks
        self.setup_tasks_card()

        # Set stretch factors to give the dashboard the "Bento" feel
        # Columns: 0=Sidebar, 1=LeftCards, 2=RightCards
        self.main_layout.setColumnStretch(0, 0) # Sidebar fixed width
        self.main_layout.setColumnStretch(1, 2) # Left side wider
        self.main_layout.setColumnStretch(2, 1) # Right side narrower

        # Rows
        self.main_layout.setRowStretch(0, 1)
        self.main_layout.setRowStretch(1, 1)

        # Dragging variables
        self.old_pos = None

    def paintEvent(self, event):
        # Draw the main gradient background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#1e130c")) # Deep dark (slightly warm)
        gradient.setColorAt(0.4, QColor("#2a0845")) # Deep Purple
        gradient.setColorAt(1.0, QColor("#000000")) # Black

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        painter.fillPath(path, gradient)

    # --- Setup Functions ---
    def setup_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(60)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(30)

        # Mock Icons (using text for simplicity)
        icons = ["🤖", "📅", "⚙️"]
        for icon in icons:
            lbl = QLabel(icon)
            lbl.setFont(QFont("Segoe UI Emoji", 24))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: rgba(255,255,255,0.7);")
            layout.addWidget(lbl)
        
        layout.addStretch()
        
        # Add sidebar to grid (Row 0-2, Col 0)
        self.main_layout.addWidget(sidebar, 0, 0, 2, 1)

    def setup_cheatsheet_card(self):
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("AI CHEATSHEET GENERATOR")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {NEON_TEAL.name()}; letter-spacing: 1px;")
        
        desc = QLabel("Upload your course PDF to extract key definitions, formulas, and dates automatically.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR.name()}; font-size: 13px; margin-top: 5px;")

        btn = StyledButton("UPLOAD PDF", primary=True)
        
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(btn)

        self.main_layout.addWidget(card, 0, 1)

    def setup_notes_card(self):
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("SUMMARIZED NOTES")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: white; letter-spacing: 1px;")

        text_area = QTextEdit()
        text_area.setPlaceholderText("Paste your messy notes here for AI processing...")
        text_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 30);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 10px;
                color: white;
                padding: 10px;
                font-family: 'Segoe UI';
            }
        """)

        mini_test_lbl = QLabel("AI MINI-TESTS READY")
        mini_test_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mini_test_lbl.setStyleSheet(f"color: {NEON_PURPLE.name()}; font-weight: bold; margin-top: 10px;")

        layout.addWidget(title)
        layout.addWidget(text_area)
        layout.addWidget(mini_test_lbl)

        self.main_layout.addWidget(card, 1, 1)

    def setup_productivity_card(self):
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)

        header_layout = QHBoxLayout()
        title = QLabel("PRODUCTIVITY STACK")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Focus Mode Row
        focus_row = QHBoxLayout()
        focus_lbl = QLabel("FOCUS MODE")
        focus_lbl.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR.name()}; font-size: 12px;")
        
        toggle = NeonToggle()
        
        focus_row.addWidget(focus_lbl)
        focus_row.addStretch()
        focus_row.addWidget(toggle)
        
        layout.addStretch()
        layout.addLayout(focus_row)
        layout.addStretch()

        self.main_layout.addWidget(card, 0, 2)

    def setup_tasks_card(self):
        card = GlassCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)

        title = QLabel("STUDY TASKS")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        layout.addWidget(title)
        layout.addSpacing(15)

        # Mock Tasks
        tasks = ["Review Linear Algebra", "Finish History Essay", "Call Mom"]
        for t in tasks:
            chk = QCheckBox(t)
            chk.setStyleSheet(f"""
                QCheckBox {{ color: {SECONDARY_TEXT_COLOR.name()}; font-size: 13px; }}
                QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid #555; background: none; }}
                QCheckBox::indicator:checked {{ background-color: {NEON_TEAL.name()}; border: 1px solid {NEON_TEAL.name()}; }}
            """)
            layout.addWidget(chk)
        
        layout.addStretch()
        
        # Progress Ring
        progress_container = QHBoxLayout()
        progress_container.addStretch()
        ring = CircularProgress()
        progress_container.addWidget(ring)
        progress_container.addStretch()
        
        layout.addLayout(progress_container)

        self.main_layout.addWidget(card, 1, 2)

    # --- Dragging Logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Font Setup
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
