# ==============================================================================
# page_title.py — Reusable page title label component.
# ==============================================================================

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class PageTitle(QLabel):
    """
    Centered, bold page title used at the top of every page.
    Default style: 64 px, bold, dark grey (#333).
    """

    def __init__(self, text: str, font_size: int = 64):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            f"font-size: {font_size}px; font-weight: bold; color: #333;"
        )
