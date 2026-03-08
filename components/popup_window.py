from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from styles.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_BLUE, ACCENT_BLUE_DK,
    BORDER_COLOR, RADIUS_LG, RADIUS_MD, FONT_BODY
)


class PopupWindow(QDialog):
    """
    Modal confirmation dialog.
    Accepted = user confirmed (go home).
    Rejected = user cancelled (stay on page).
    """
    def __init__(self, state, nav,
                 message="Are you sure you want to go home?\nUnsaved progress will be lost."):
        super().__init__()
        self.state = state
        self.nav   = nav

        self.setWindowTitle("Confirm Navigation")
        self.setModal(True)
        self.setMinimumWidth(620)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_CARD};
                border-radius: {RADIUS_LG};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(56, 48, 56, 48)
        layout.setSpacing(36)

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        font = QFont(FONT_BODY)
        font.setPointSize(22)
        label.setFont(font)
        label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(label)

        button_row = QHBoxLayout()
        button_row.setSpacing(24)

        cancel_btn  = QPushButton("Cancel — Stay Here")
        confirm_btn = QPushButton("Yes, Go Home")

        for btn, primary in [(cancel_btn, False), (confirm_btn, True)]:
            btn.setMinimumHeight(72)
            btn.setFont(QFont(FONT_BODY, 18))
            if primary:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ACCENT_BLUE};
                        color: #FFFFFF;
                        border: none;
                        border-radius: {RADIUS_MD};
                        font-weight: 700;
                        padding: 12px 36px;
                    }}
                    QPushButton:hover {{ background-color: {ACCENT_BLUE_DK}; }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #FFCCCC;
                        color: #000000;
                        border: 2px solid #000000;
                        border-radius: {RADIUS_MD};
                        font-weight: 700;
                        padding: 12px 36px;
                    }}
                    QPushButton:hover {{ background-color: #FFB3B3; }}
                """)
            button_row.addWidget(btn)

        cancel_btn.clicked.connect(self.reject)
        confirm_btn.clicked.connect(lambda: (self.accept(), self.nav.go_home()))

        layout.addLayout(button_row)

# from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
# from PyQt6.QtCore import Qt

# class PopupWindow(QDialog):
#     def __init__(self, state, nav, message="Are you sure you want to go home? Unsaved progress will be lost."):
#         super().__init__()
#         self.state = state
#         self.nav = nav
#         self.setWindowTitle("Confirm Navigation")
#         self.setModal(True)

#         layout = QVBoxLayout(self)

#         label = QLabel(message)
#         label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         layout.addWidget(label)

#         button_row = QHBoxLayout()

#         cancel_btn = QPushButton("Cancel")
#         confirm_btn = QPushButton("Yes, go home")

#         cancel_btn.clicked.connect(self.nav.go_home)
#         confirm_btn.clicked.connect(self.nav.go_home)

#         button_row.addWidget(cancel_btn)
#         button_row.addWidget(confirm_btn)

#         layout.addLayout(button_row)
