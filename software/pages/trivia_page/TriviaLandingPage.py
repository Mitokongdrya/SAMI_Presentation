# ==============================================================================
# TriviaLandingPage.py — Trivia landing page for the SAMI UI.
#
# Lets the user choose 5 or 10 questions, then starts the trivia game.
# ==============================================================================

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
)
from PyQt6.QtCore import Qt

# ── Project imports ───────────────────────────────────────────────────────────
from components.home_button import HomeButton
from components.page_title import PageTitle


# ==============================================================================
# Trivia Landing Page
# ==============================================================================

class TriviaLandingPage(QWidget):
    """Landing page — choose 5 or 10 questions, then start."""

    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui
        self._selected_count = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # ── Title ────────────────────────────────────────────────────────────
        layout.addWidget(PageTitle("Trivia"))
        layout.addStretch(1)

        # ── Question count prompt ────────────────────────────────────────────
        choose_label = QLabel("How many questions?")
        choose_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        choose_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #333;")
        layout.addWidget(choose_label)

        layout.addSpacing(16)

        # ── 5 / 10 selector row ─────────────────────────────────────────────
        BTN_STYLE = """
            QPushButton {{
                font-size: 48px;
                font-weight: bold;
                color: black;
                border-radius: 20px;
                background: {bg};
                border: {border};
            }}
            QPushButton:hover {{ background: #FFB3B3; }}
        """
        NORMAL_BG     = "#FFCCCC"
        SELECTED_BG   = "#FF8080"
        NORMAL_BORDER = "3px solid #333"
        SELECTED_BORDER = "5px solid #000"

        count_row = QHBoxLayout()
        count_row.setSpacing(40)
        count_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn5  = QPushButton("5 Questions")
        self._btn10 = QPushButton("10 Questions")

        for btn in (self._btn5, self._btn10):
            btn.setMinimumSize(360, 140)
            btn.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
            count_row.addWidget(btn)

        def select_count(count):
            self._selected_count = count
            if count == 5:
                self._btn5.setStyleSheet(BTN_STYLE.format(bg=SELECTED_BG, border=SELECTED_BORDER))
                self._btn10.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
            else:
                self._btn10.setStyleSheet(BTN_STYLE.format(bg=SELECTED_BG, border=SELECTED_BORDER))
                self._btn5.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
            self._start_btn.setEnabled(True)
            self._start_btn.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))

        self._btn5.clicked.connect(lambda: select_count(5))
        self._btn10.clicked.connect(lambda: select_count(10))

        layout.addLayout(count_row)
        layout.addSpacing(32)

        # ── Start button (disabled until a count is chosen) ──────────────────
        self._start_btn = QPushButton("Start Trivia")
        self._start_btn.setMinimumSize(400, 140)
        self._start_btn.setEnabled(False)
        self._start_btn.setStyleSheet("""
            QPushButton {
                font-size: 48px;
                font-weight: bold;
                color: #888;
                border-radius: 20px;
                background: #e0e0e0;
                border: 3px solid #aaa;
            }
        """)
        self._start_btn.clicked.connect(self._start_trivia)
        layout.addWidget(self._start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        # ── Home button ──────────────────────────────────────────────────────
        home_button = HomeButton("Return Home")
        home_button.clicked.connect(
            lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        layout.addWidget(home_button)

    # ── Events ───────────────────────────────────────────────────────────────
    def showEvent(self, event):
        """Reset selection every time the page is shown."""
        super().showEvent(event)
        self._selected_count = None
        BTN_STYLE = """
            QPushButton {{
                font-size: 48px; font-weight: bold; color: black;
                border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
            }}
            QPushButton:hover {{ background: #FFB3B3; }}
        """
        self._btn5.setStyleSheet(BTN_STYLE.format())
        self._btn10.setStyleSheet(BTN_STYLE.format())
        self._start_btn.setEnabled(False)
        self._start_btn.setStyleSheet("""
            QPushButton {
                font-size: 48px; font-weight: bold; color: #888;
                border-radius: 20px; background: #e0e0e0; border: 3px solid #aaa;
            }
        """)

    def _start_trivia(self):
        """Load questions and navigate to the first question page."""
        self.parent_ui.trivia_load_questions(limit=self._selected_count)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
        self.parent_ui.trivia_question_page.load_question()
