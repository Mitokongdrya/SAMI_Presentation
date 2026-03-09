# PyQt6 — widgets, gui helpers, and core utilities
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QToolButton, QButtonGroup,
    QDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize, QTimer

from components.home_button import HomeButton

# ============================================================
# TRIVIA HOME CONFIRMATION DIALOG
# ============================================================

class TriviaHomeConfirmDialog(QDialog):
    """
    Simple modal: asks the user to confirm before abandoning trivia.
    Matches the existing #FFCCCC / border: 3px solid #333 aesthetic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Leave Trivia?")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setStyleSheet("background-color: #96C4DB;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(56, 48, 56, 48)
        layout.setSpacing(36)

        msg = QLabel("⚠️  Your trivia progress will be lost.\nAre you sure you want to go home?")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; background: transparent;")
        layout.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(32)

        stay_btn   = QPushButton("Cancel — Stay Here")
        go_btn     = QPushButton("Yes, Go Home")

        for btn, is_confirm in [(stay_btn, False), (go_btn, True)]:
            btn.setMinimumHeight(80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 28px;
                    font-weight: bold;
                    color: black;
                    border-radius: 16px;
                    background: {'#ff6666' if is_confirm else '#FFCCCC'};
                    border: 3px solid #333;
                    padding: 12px 28px;
                }}
                QPushButton:hover {{
                    background: {'#ff3333' if is_confirm else '#FFB3B3'};
                }}
            """)
            btn_row.addWidget(btn)

        stay_btn.clicked.connect(self.reject)
        go_btn.clicked.connect(self.accept)
        layout.addLayout(btn_row)

# ============================================================
# TRIVIA PAGES
# ============================================================

class TriviaPage(QWidget):
    """Landing page — choose 5 or 10 questions, then start."""
    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui
        self._selected_count = None  # will be 5 or 10

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Trivia")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        layout.addStretch(1)

        # "How many questions?" label
        choose_label = QLabel("How many questions?")
        choose_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        choose_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #333;")
        layout.addWidget(choose_label)

        layout.addSpacing(16)

        # 5 / 10 selector row
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

        # Start button — disabled until a count is chosen
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

        home_button = HomeButton("Return Home")
        home_button.clicked.connect(
            lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        layout.addWidget(home_button)

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
        self.parent_ui.trivia_load_questions(limit=self._selected_count)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
        self.parent_ui.trivia_question_page.load_question()

class TriviaQuestionPage(QWidget):
    """Shows the current question and four answer buttons."""
    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # Counter + score row
        info_row = QHBoxLayout()
        self.counter_label = QLabel("Question 1 / ?")
        self.counter_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        self.score_label = QLabel("Score: 0 / 0")
        self.score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        info_row.addWidget(self.counter_label)
        info_row.addStretch()
        info_row.addWidget(self.score_label)
        layout.addLayout(info_row)

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

        self.answers_grid = QGridLayout()
        self.answers_grid.setSpacing(24)
        layout.addLayout(self.answers_grid)
        self.answer_buttons = []

        layout.addStretch(1)

        home_button = HomeButton("Return Home")
        home_button.clicked.connect(self._confirm_go_home)
        layout.addWidget(home_button)

    def _confirm_go_home(self, *_):
        dlg = TriviaHomeConfirmDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

    def load_question(self):
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
            btn = QPushButton(f"{letter}.  {text}")
            btn.setMinimumSize(600, 130)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 28px;
                    font-weight: bold;
                    color: black;
                    border-radius: 20px;
                    background: #FFCCCC;
                    border: 3px solid #333;
                    text-align: left;
                    padding-left: 24px;
                }
                QPushButton:hover { background: #FFB3B3; }
            """)
            btn.clicked.connect(lambda _, l=letter: self._submit(l))
            self.answers_grid.addWidget(btn, row, col)
            self.answer_buttons.append(btn)

    def _submit(self, letter):
        self.parent_ui.trivia_submit_answer(letter)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_answer_page)
        self.parent_ui.trivia_answer_page.refresh()


class TriviaAnswerPage(QWidget):
    """Shows correct/wrong feedback and a Next button."""
    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        layout.addStretch(1)

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

        next_btn = QPushButton("Next Question")
        next_btn.setMinimumSize(400, 120)
        next_btn.setStyleSheet("""
            QPushButton {
                font-size: 40px;
                font-weight: bold;
                color: black;
                border-radius: 20px;
                background: #FFCCCC;
                border: 3px solid #333;
            }
            QPushButton:hover { background: #FFB3B3; }
        """)
        next_btn.clicked.connect(self._next)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        home_button = HomeButton("Return Home")
        home_button.clicked.connect(self._confirm_go_home)
        layout.addWidget(home_button)

    def _confirm_go_home(self, *_):
        dlg = TriviaHomeConfirmDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

    def refresh(self):
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
        if self.parent_ui.trivia_index >= len(self.parent_ui.trivia_questions):
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_score_page)
            self.parent_ui.trivia_score_page.refresh()
        else:
            self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
            self.parent_ui.trivia_question_page.load_question()


class TriviaScorePage(QWidget):
    """Final score screen with Play Again and Go Home options."""
    def __init__(self, parent_ui):
        super().__init__()
        self.parent_ui = parent_ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        layout.addStretch(2)

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

        btn_row = QHBoxLayout()
        btn_row.setSpacing(40)

        play_again_btn = QPushButton("Play Again")
        play_again_btn.setMinimumSize(360, 120)
        play_again_btn.setStyleSheet("""
            QPushButton {
                font-size: 40px; font-weight: bold; color: black;
                border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
            }
            QPushButton:hover { background: #FFB3B3; }
        """)
        play_again_btn.clicked.connect(self._play_again)
        btn_row.addWidget(play_again_btn)

        home_btn = QPushButton("Go Home")
        home_btn.setMinimumSize(360, 120)
        home_btn.setStyleSheet("""
            QPushButton {
                font-size: 40px; font-weight: bold; color: black;
                border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
            }
            QPushButton:hover { background: #FFB3B3; }
        """)
        home_btn.clicked.connect(
            lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        btn_row.addWidget(home_btn)

        layout.addLayout(btn_row, )
        layout.addStretch(2)

    def refresh(self):
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
        self.parent_ui.trivia_load_questions()
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
        self.parent_ui.trivia_question_page.load_question()


