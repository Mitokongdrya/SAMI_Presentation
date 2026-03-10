# ==============================================================================
# TriviaPage.py — Trivia game pages for the SAMI UI.
#
# Contains the trivia landing page (question count selection), the question
# page, the answer feedback page, the final score page, and the confirmation
# dialog shown when the user tries to leave mid-game.
# ==============================================================================

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDialog,
)
from PyQt6.QtCore import Qt

# ── Project imports ───────────────────────────────────────────────────────────
from components.home_button import HomeButton
from components.page_title import PageTitle
from components.action_button import ActionButton
from components.confirm_dialog import ConfirmDialog

# ==============================================================================
# Trivia Landing Page
# ==============================================================================

class TriviaPage(QWidget):
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


# ==============================================================================
# Trivia Question Page
# ==============================================================================

class TriviaQuestionPage(QWidget):
    """Shows the current question and four answer buttons."""

    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # ── Counter + score row ──────────────────────────────────────────────
        info_row = QHBoxLayout()
        self.counter_label = QLabel("Question 1 / ?")
        self.counter_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        self.score_label = QLabel("Score: 0 / 0")
        self.score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        info_row.addWidget(self.counter_label)
        info_row.addStretch()
        info_row.addWidget(self.score_label)
        layout.addLayout(info_row)

        # ── Question text ────────────────────────────────────────────────────
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #333;
            background: #fff;
            border-radius: 16px;
            border: 3px solid #333;
            padding: 24px 32px;
        """)
        layout.addWidget(self.question_label)
        layout.addStretch(1)

        # ── Answer buttons grid ──────────────────────────────────────────────
        self.answers_grid = QGridLayout()
        self.answers_grid.setSpacing(24)
        layout.addLayout(self.answers_grid)
        self.answer_buttons = []

        layout.addStretch(1)

        # ── Home button ──────────────────────────────────────────────────────
        home_button = HomeButton("Return Home")
        home_button.clicked.connect(self._confirm_go_home)
        layout.addWidget(home_button)

    # ── Navigation ───────────────────────────────────────────────────────────
    def _confirm_go_home(self, *_):
        """Show a confirmation dialog before abandoning the trivia game."""
        dlg = ConfirmDialog(
            message="⚠️  Your trivia progress will be lost.\nAre you sure you want to go home?",
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

    def load_question(self):
        """Populate the page with the current question and answer choices."""
        q = self.parent_ui.trivia_current_question()
        if not q:
            return

        total   = len(self.parent_ui.trivia_questions)
        current = self.parent_ui.trivia_index + 1
        score   = self.parent_ui.trivia_score

        self.counter_label.setText(f"Question {current} / {total}")
        self.score_label.setText(f"Score: {score} / {self.parent_ui.trivia_index}")
        self.question_label.setText(q["question"])

        # Rebuild answer buttons
        for btn in self.answer_buttons:
            self.answers_grid.removeWidget(btn)
            btn.deleteLater()
        self.answer_buttons = []

        options = [("A", q["option_a"]), ("B", q["option_b"]),
                   ("C", q["option_c"]), ("D", q["option_d"])]

        for i, (letter, text) in enumerate(options):
            row, col = divmod(i, 2)
            btn = ActionButton(
                f"{letter}.  {text}",
                min_width=600, min_height=130, font_size=28, text_align="left",
            )
            btn.clicked.connect(lambda _, l=letter: self._submit(l))
            self.answers_grid.addWidget(btn, row, col)
            self.answer_buttons.append(btn)

    def _submit(self, letter):
        """Submit the chosen answer and navigate to the feedback page."""
        self.parent_ui.trivia_submit_answer(letter)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_answer_page)
        self.parent_ui.trivia_answer_page.refresh()


# ==============================================================================
# Trivia Answer Feedback Page
# ==============================================================================

class TriviaAnswerPage(QWidget):
    """Shows correct/wrong feedback and a Next button."""

    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        layout.addStretch(1)

        # ── Result labels ────────────────────────────────────────────────────
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(self.result_label)

        self.correct_label = QLabel()
        self.correct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.correct_label.setStyleSheet("font-size: 36px; color: #333;")
        layout.addWidget(self.correct_label)

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        layout.addWidget(self.score_label)

        layout.addStretch(1)

        # ── Next question button ─────────────────────────────────────────────
        next_btn = ActionButton("Next Question", min_width=400, min_height=120, font_size=40)
        next_btn.clicked.connect(self._next)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        # ── Home button ──────────────────────────────────────────────────────
        home_button = HomeButton("Return Home")
        home_button.clicked.connect(self._confirm_go_home)
        layout.addWidget(home_button)

    # ── Navigation ───────────────────────────────────────────────────────────
    def _confirm_go_home(self, *_):
        """Show a confirmation dialog before abandoning the trivia game."""
        dlg = ConfirmDialog(
            message="⚠️  Your trivia progress will be lost.\nAre you sure you want to go home?",
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

    def refresh(self):
        """Update the page with the result of the last answered question."""
        was_correct = self.parent_ui.trivia_last_correct
        q = self.parent_ui.trivia_current_question(offset=-1)
        correct_text = q["correct_answer"] if q else ""

        if was_correct:
            self.result_label.setText("✅  Correct!")
            self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #2a9d2a;")
        else:
            self.result_label.setText("❌  Wrong!")
            self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #cc2222;")

        self.correct_label.setText(f"Answer: {correct_text}")
        answered = self.parent_ui.trivia_index
        self.score_label.setText(
            f"Score: {self.parent_ui.trivia_score} / {answered}"
        )

    def _next(self):
        """Advance to the next question or show the final score."""
        if self.parent_ui.trivia_index >= len(self.parent_ui.trivia_questions):
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_score_page)
            self.parent_ui.trivia_score_page.refresh()
        else:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
            self.parent_ui.trivia_question_page.load_question()


# ==============================================================================
# Trivia Score Page
# ==============================================================================

class TriviaScorePage(QWidget):
    """Final score screen with Play Again and Go Home options."""

    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        layout.addStretch(2)

        # ── Trophy and score labels ──────────────────────────────────────────
        trophy = QLabel("🏆")
        trophy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trophy.setStyleSheet("font-size: 100px;")
        layout.addWidget(trophy)

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(self.score_label)

        self.msg_label = QLabel()
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setStyleSheet("font-size: 36px; color: #333;")
        layout.addWidget(self.msg_label)

        layout.addStretch(1)

        # ── Play Again / Go Home buttons ─────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(40)

        play_again_btn = ActionButton("Play Again", min_width=360, min_height=120, font_size=40)
        play_again_btn.clicked.connect(self._play_again)
        btn_row.addWidget(play_again_btn)

        home_btn = ActionButton("Go Home", min_width=360, min_height=120, font_size=40)
        home_btn.clicked.connect(
            lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        btn_row.addWidget(home_btn)

        layout.addLayout(btn_row)
        layout.addStretch(2)

    def refresh(self):
        """Compute and display the final score with a congratulatory message."""
        total = len(self.parent_ui.trivia_questions)
        score = self.parent_ui.trivia_score
        self.score_label.setText(f"Final Score:  {score} / {total}")
        pct = int(score / total * 100) if total else 0
        if pct == 100:
            msg = "Perfect score! Amazing! 🎉"
        elif pct >= 70:
            msg = "Great job! Keep it up! 👍"
        elif pct >= 40:
            msg = "Good effort! Want to try again?"
        else:
            msg = "Better luck next time! 💪"
        self.msg_label.setText(msg)

    def _play_again(self):
        """Reload questions and restart the trivia game."""
        self.parent_ui.trivia_load_questions(limit=self.parent_ui.trivia_index)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
        self.parent_ui.trivia_question_page.load_question()