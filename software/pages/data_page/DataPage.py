# ==============================================================================
# DataPage.py — Data hub page for the SAMI UI.
#
# Presents two navigation buttons: Sensor Demo and Rating Data,
# linking to their respective sub-pages.
# ==============================================================================

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QToolButton,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

# ── Project imports ───────────────────────────────────────────────────────────
from components.home_button import HomeButton


# ==============================================================================
# Data Page (hub)
# ==============================================================================

class DataPage(QWidget):
    """
    Hub page replacing the old SensorPage.
    Presents two navigation buttons: Sensor Data and Rating Data.
    """

    def __init__(self, parent_ui):
        super().__init__()

        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # ── Page title ───────────────────────────────────────────────────────
        title = QLabel("Data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        layout.addStretch(1)

        # ── Navigation button grid ───────────────────────────────────────────
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(40)

        sections = [
            ("Sensor Demo", "icons/Sensor.svg"),
            ("Rating Data", "icons/Rating.png"),
        ]

        for col, (name, icon_path) in enumerate(sections):
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(QIcon(QPixmap(icon_path)))
            btn.setIconSize(QSize(170, 170))
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumSize(400, 400)
            btn.setStyleSheet("""
                QToolButton {
                    color: #000;
                    font-size: 48px;
                    font-weight: bold;
                    padding: 20px;
                    border-radius: 20px;
                    background: #FFCCCC;
                    border: 3px solid #333;
                }
                QToolButton:hover { background: #FFB3B3; }
            """)

            if name == "Sensor Demo":
                btn.clicked.connect(
                    lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.sensor_data_page)
                )
            elif name == "Rating Data":
                btn.clicked.connect(
                    lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.rating_data_page)
                )

            grid.addWidget(btn, 0, col)

        layout.addLayout(grid)
        layout.addStretch(1)

        # ── Home button ──────────────────────────────────────────────────────
        home_button = HomeButton("Return Home")
        home_button.clicked.connect(
            lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        layout.addWidget(home_button)
