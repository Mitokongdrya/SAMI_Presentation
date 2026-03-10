# ==============================================================================
# SensorDataPage.py — Sensor demo video player page.
#
# Displays a playable video (capstone-proof.mp4) using Qt's multimedia stack.
# Provides Play/Pause and Stop controls beneath the video.
# ==============================================================================

import os

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
)
from PyQt6.QtCore import Qt

# ── Project imports ───────────────────────────────────────────────────────────
from components.home_button import HomeButton


# ==============================================================================
# Sensor Data Page
# ==============================================================================

class SensorDataPage(QWidget):
    """
    Displays a playable video (capstone-proof.mp4) using Qt's multimedia stack.
    Provides Play/Pause and Stop controls beneath the video.
    """

    def __init__(self, parent_ui):
        super().__init__()

        self.parent_ui = parent_ui

        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        from PyQt6.QtMultimediaWidgets import QVideoWidget
        from PyQt6.QtCore import QUrl

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # ── Page title ───────────────────────────────────────────────────────
        title = QLabel("Sensor Demo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # ── Video widget ─────────────────────────────────────────────────────
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(480)
        self.video_widget.setStyleSheet("background: #000; border-radius: 12px;")
        layout.addWidget(self.video_widget)

        # ── Media player wired to the video widget ───────────────────────────
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile(
            os.path.abspath("icons/capstone-proof.mp4")
        ))

        # ── Playback controls ────────────────────────────────────────────────
        controls = QHBoxLayout()
        controls.setSpacing(24)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        BTN = """
            QPushButton {
                font-size: 32px; font-weight: bold; color: black;
                border-radius: 16px; background: #FFCCCC; border: 3px solid #333;
                padding: 12px 40px;
            }
            QPushButton:hover { background: #FFB3B3; }
        """

        play_btn = QPushButton("\u25b6  Play / Pause")
        play_btn.setStyleSheet(BTN)
        play_btn.setMinimumHeight(80)
        play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(play_btn)

        stop_btn = QPushButton("\u25a0  Stop")
        stop_btn.setStyleSheet(BTN)
        stop_btn.setMinimumHeight(80)
        stop_btn.clicked.connect(self._stop)
        controls.addWidget(stop_btn)

        layout.addLayout(controls)
        layout.addStretch(1)

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

    def _toggle_play(self):
        """Toggle between playing and paused."""
        from PyQt6.QtMultimedia import QMediaPlayer
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _stop(self):
        """Stop playback and return to the beginning."""
        self.player.stop()