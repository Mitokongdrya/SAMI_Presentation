# ==============================================================================
# action_button.py — Reusable pink action button component.
# ==============================================================================

from PyQt6.QtWidgets import QPushButton


class ActionButton(QPushButton):
    """
    Styled QPushButton with the app's signature pink (#FFCCCC) theme.

    Parameters
    ----------
    text : str
        Button label.
    min_width : int
        Minimum width in pixels (default 400).
    min_height : int
        Minimum height in pixels (default 120).
    font_size : int
        Font size in pixels (default 32).
    bg : str
        Background colour (default "#FFCCCC").
    bg_hover : str
        Hover background colour (default "#FFB3B3").
    text_align : str
        CSS text-align value (default "center").
    """

    def __init__(
        self,
        text: str,
        min_width: int = 400,
        min_height: int = 120,
        font_size: int = 32,
        bg: str = "#FFCCCC",
        bg_hover: str = "#FFB3B3",
        text_align: str = "center",
    ):
        super().__init__(text)
        self.setMinimumSize(min_width, min_height)
        self.setStyleSheet(f"""
            QPushButton {{
                font-size: {font_size}px;
                font-weight: bold;
                color: black;
                border-radius: 20px;
                background: {bg};
                border: 3px solid #333;
                text-align: {text_align};
                padding-left: 24px;
                padding-right: 24px;
            }}
            QPushButton:hover {{ background: {bg_hover}; }}
        """)
