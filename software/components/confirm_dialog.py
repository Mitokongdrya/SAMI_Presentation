# ==============================================================================
# confirm_dialog.py — Reusable confirmation dialog component.
# ==============================================================================

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class ConfirmDialog(QDialog):
    """
    Modal confirmation dialog matching the app's #96C4DB / #FFCCCC aesthetic.

    Returns QDialog.DialogCode.Accepted when the user confirms and
    QDialog.DialogCode.Rejected when they cancel.

    Parameters
    ----------
    message : str
        The question / warning text to display.
    confirm_text : str
        Label for the confirm button (default "Yes, Go Home").
    cancel_text : str
        Label for the cancel button (default "Cancel — Stay Here").
    parent : QWidget | None
        Optional parent widget.
    """

    def __init__(
        self,
        message: str = "⚠️  Your progress will be lost.\nAre you sure you want to go home?",
        confirm_text: str = "Yes, Go Home",
        cancel_text: str = "Cancel — Stay Here",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setStyleSheet("background-color: #96C4DB;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(56, 48, 56, 48)
        layout.setSpacing(36)

        # ── Message label ────────────────────────────────────────────────
        msg = QLabel(message)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #333; background: transparent;"
        )
        layout.addWidget(msg)

        # ── Button row ───────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(32)

        cancel_btn = QPushButton(cancel_text)
        confirm_btn = QPushButton(confirm_text)

        for btn, is_confirm in [(cancel_btn, False), (confirm_btn, True)]:
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

        cancel_btn.clicked.connect(self.reject)
        confirm_btn.clicked.connect(self.accept)
        layout.addLayout(btn_row)
