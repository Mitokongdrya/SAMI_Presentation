# ==============================================================================
# RatingDataPage.py — Exercise rating history viewer.
#
# Displays per-exercise average summary cards and a full scrollable ratings
# table. Reloads from disk every time the page is shown.
# ==============================================================================

import os

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt

# ── Project imports ───────────────────────────────────────────────────────────
from components.home_button import HomeButton


# ==============================================================================
# Rating Data Page
# ==============================================================================

class RatingDataPage(QWidget):
    """
    Displays exercise rating history.
    Shows per-exercise average summary cards and a full scrollable ratings table.
    Reloads from disk every time the page is shown.
    """

    def __init__(self, parent_ui):
        super().__init__()

        self.parent_ui  = parent_ui
        self.rating_file = "exercise_ratings.txt"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # ── Page title ───────────────────────────────────────────────────────
        title = QLabel("Rating Data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # ── Section heading ──────────────────────────────────────────────────
        ratings_title = QLabel("Exercise Ratings")
        ratings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ratings_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #333;")
        layout.addWidget(ratings_title)

        # ── Per-exercise average summary cards (populated dynamically) ───────
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(20)
        layout.addLayout(self.summary_layout)

        # ── Full ratings table ───────────────────────────────────────────────
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Interaction", "Rating"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                color: #000;
                font-size: 22px;
                background: #fff;
                border-radius: 12px;
                border: 2px solid #aaa;
            }
            QHeaderView::section {
                color: #000;
                font-size: 24px;
                font-weight: bold;
                background: #FFCCCC;
                border: 1px solid #aaa;
                padding: 6px;
            }
        """)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        # ── Back and Home buttons ────────────────────────────────────────────
        nav_row = QHBoxLayout()

        back_btn = HomeButton("\u2190 Back")
        back_btn.clicked.connect(
            lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.data_page)
        )
        nav_row.addWidget(back_btn)

        home_button = HomeButton("Return Home")
        home_button.clicked.connect(
            lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
        )
        nav_row.addWidget(home_button)
        layout.addLayout(nav_row)

    def showEvent(self, event):
        """Reload ratings from disk every time this page becomes visible."""
        super().showEvent(event)
        self._load_ratings()

    def _load_ratings(self):
        """
        Parse exercise_ratings.txt, fill the table, and rebuild summary cards.
        Each line is expected to be:  timestamp | exercise name | rating
        """
        from PyQt6.QtWidgets import QTableWidgetItem
        from collections import defaultdict

        # ── Parse the ratings file ────────────────────────────────────────────
        rows = []
        if os.path.exists(self.rating_file):
            with open(self.rating_file, "r") as f:
                for line in f:
                    parts = [p.strip() for p in line.strip().split("|")]
                    if len(parts) == 3:
                        rows.append(parts)

        # ── Populate the table, most-recent entry first ──────────────────────
        self.table.setRowCount(len(rows))
        for r, (ts, exercise, rating) in enumerate(reversed(rows)):
            self.table.setItem(r, 0, QTableWidgetItem(ts))
            self.table.setItem(r, 1, QTableWidgetItem(exercise))
            rating_item = QTableWidgetItem(rating)
            rating_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, rating_item)
        if self.table.rowCount() > 0:
            self.table.setRowHeight(0, 48)

        # ── Compute per-exercise averages (ignoring "None" entries) ──────────
        totals: dict = defaultdict(list)
        for _, exercise, rating in rows:
            if rating != "None":
                try:
                    totals[exercise].append(int(rating))
                except ValueError:
                    pass

        # ── Rebuild summary cards, clearing any previous ones first ──────────
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Color scale mirrors the rating button colors on RatingPage
        RATING_COLORS = {
            "1": "#ff4d4d",
            "2": "#ff944d",
            "3": "#ffe666",
            "4": "#b3ff66",
            "5": "#66ff66",
        }

        for exercise, values in sorted(totals.items()):
            avg   = sum(values) / len(values)
            color = RATING_COLORS.get(str(round(avg)), "#ccc")
            card  = QLabel(f"{exercise}\n\u2605 {avg:.1f} ({len(values)} rated)")
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setWordWrap(True)
            card.setStyleSheet(f"""
                background: {color};
                border-radius: 14px;
                border: 2px solid #333;
                font-size: 22px;
                font-weight: bold;
                padding: 16px 24px;
                color: #333;
            """)
            self.summary_layout.addWidget(card)