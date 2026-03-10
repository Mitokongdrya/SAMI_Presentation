# ==============================================================================
# HomePage.py — Main landing page for the SAMI UI.
#
# Presents interaction buttons (Exercises, Trivia, Data) that navigate
# to their respective pages via the parent's QStackedWidget.
# ==============================================================================

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QToolButton,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize


# ==============================================================================
# Home Page
# ==============================================================================

class HomePage(QWidget):
    """Main landing page — presents interaction buttons."""

    def __init__(self, parent_ui):
        super().__init__()

        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # ── Title ────────────────────────────────────────────────────────────
        title = QLabel("Select an Interaction")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        layout.addStretch(1)

        # ── Interaction grid ─────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(40)

        interactions = [
            ("Exercises", "icons/Exercises.png"),
            ("Trivia", "icons/Trivia.png"),
            ("Data", "icons/data.svg")
        ]

        for col, (name, icon_path) in enumerate(interactions):
            interaction_btn = QToolButton()
            interaction_btn.setText(name)
            interaction_btn.setIcon(QIcon(QPixmap(icon_path)))
            interaction_btn.setIconSize(QSize(170, 170))
            interaction_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            interaction_btn.setMinimumSize(400, 400)

            interaction_btn.setStyleSheet("""
            QToolButton {
                color: #000;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                border-radius: 20px;
                background: #FFCCCC;
                border: 3px solid #333;
            }
            """)

            if name == "Exercises":
                interaction_btn.clicked.connect(
                    lambda: (
                        self.parent_ui.move_to_home(),  # first move robot home
                        self.parent_ui.stack.setCurrentWidget(self.parent_ui.exercise_page)  # then go to exercise page
                    )
                )
            elif name == "Data":
                interaction_btn.clicked.connect(
                    lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.data_page)
                )
            elif name == "Trivia":
                interaction_btn.clicked.connect(
                    lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_page)
                )
            else:
                interaction_btn.clicked.connect(
                    lambda _, n=name: print(f"{n} clicked")
                )

            grid.addWidget(interaction_btn, 0, col)

        layout.addLayout(grid)
        layout.addStretch(1)

        # home_robot_btn = QPushButton("Home", self)
        # home_robot_btn.clicked.connect(self.parent_ui.move_to_home)
        # layout.addWidget(home_robot_btn)
