# ==============================================================================
# SAMI_UI.py — Main UI entry point for the SAMI robot control interface.
#
# Defines the ExercisePage, ExerciseOverlay, and the main SAMIControlUI window
# that ties all pages together with a QStackedWidget. Supports both a full
# presentation UI and a legacy debug UI via the USE_NEW_UI flag.
# ==============================================================================

import sys
import time
import os
import json
import csv
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ── PyQt6 imports ─────────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QToolButton, QButtonGroup,
    QDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize, QTimer

# ── Project imports ───────────────────────────────────────────────────────────
from SAMIControl import SAMIControl
from components.home_button import HomeButton
from components.button import Button
from pages.HomePage import HomePage
from pages.RatingPage import RatingPage
from pages.TriviaPage import TriviaPage, TriviaQuestionPage, TriviaAnswerPage, TriviaScorePage
from pages.data_page.DataPage import DataPage
from pages.data_page.SensorDataPage import SensorDataPage
from pages.data_page.RatingDataPage import RatingDataPage

# ── UI mode toggle ───────────────────────────────────────────────────────────
# Set to True  → full presentation UI  (pages, stack, trivia, etc.)
# Set to False → legacy debug UI       (joint dropdowns, raw commands)
USE_NEW_UI = True




# class HomePage(QWidget):
#     def __init__(self, parent_ui):
#         super().__init__()

#         self.parent_ui = parent_ui  # reference to main window

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         # Title
#         title = QLabel("Select an Interaction")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)
#         layout.addStretch(1)

#         # Grid
#         grid = QGridLayout()
#         grid.setHorizontalSpacing(40)
#         grid.setVerticalSpacing(40)

#         interactions = [
#             ("Exercises", "icons/Exercises.png"),
#             ("Trivia", "icons/Trivia.png"),
#             ("Data", "icons/data.svg")
#         ]

#         for col, (name, icon_path) in enumerate(interactions):
#             interaction_btn = QToolButton()
#             interaction_btn.setText(name)
#             interaction_btn.setIcon(QIcon(QPixmap(icon_path)))
#             interaction_btn.setIconSize(QSize(170, 170))
#             interaction_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
#             interaction_btn.setMinimumSize(400, 400)

#             interaction_btn.setStyleSheet("""
#             QToolButton {
#                 color: #000;
#                 font-size: 48px;
#                 font-weight: bold;
#                 padding: 20px;
#                 border-radius: 20px;
#                 background: #FFCCCC;
#                 border: 3px solid #333;
#             }
#             """)

#             if name == "Exercises":
#                 interaction_btn.clicked.connect(
#                     lambda: (
#                         self.parent_ui.move_to_home(),  # first move robot home
#                         self.parent_ui.stack.setCurrentWidget(self.parent_ui.exercise_page)  # then go to exercise page
#                     )
#                 )
#             elif name == "Data":
#                 interaction_btn.clicked.connect(
#                     lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.data_page)
#                 )
#             elif name == "Trivia":
#                 interaction_btn.clicked.connect(
#                     lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_page)
#                 )
#             else:
#                 interaction_btn.clicked.connect(
#                     lambda _, n=name: print(f"{n} clicked")
#                 )

#             grid.addWidget(interaction_btn, 0, col)

#         layout.addLayout(grid)
#         layout.addStretch(1)

#         # home_robot_btn = QPushButton("Home", self)
#         # home_robot_btn.clicked.connect(self.parent_ui.move_to_home)
#         # layout.addWidget(home_robot_btn)


# ==============================================================================
# Exercise Page
# ==============================================================================

class ExercisePage(QWidget):
    """Displays available exercises as GIF previews with action buttons."""

    def __init__(self, parent_ui):
        super().__init__()

        self.parent_ui = parent_ui 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(8)

        # ── Title ────────────────────────────────────────────────────────────
        title = QLabel("Select an Exercise to Perform")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        layout.addStretch(1)

        # ── Exercise grid ────────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(40)
        layout.addLayout(grid)

        # ── Exercise configuration ───────────────────────────────────────────
        # behaviors = self.parent_ui.get_behavior_files()
        self.exercise_config = [
            {"title": "Wave", "description": "Wave hello to the adoring fans", "file": "Wave.json", "video": "icons/Waving.gif",
             "why": "Waving engages the shoulder and elbow joints, promoting upper limb mobility and coordination."},
            {"title": "Shrug", "description": "What's Happening?", "file": "Shrug.json", "video": "icons/Shrug.gif",
             "why": "Shoulder shrugs strengthen the trapezius muscles and help release tension in the neck and upper back."},
            {"title": "Side Stretch", "description": "Helps with core strength", "file": "SideToSide.json", "video": "icons/SideToSide.gif",
             "why": "Side-to-side stretching improves spinal flexibility, activates the obliques, and enhances balance."},
        ]

        # ── Build exercise grid cells ────────────────────────────────────────
        positions = [(0, c) for c in range(3)]

        for (row, col), behavior in zip(positions, self.exercise_config[:3]):

            # ── Cell container ────────────────────────────────────────────
            cell_widget = QWidget()
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.setSpacing(10)

            # ── GIF preview ──────────────────────────────────────────────
            gif_label = QLabel()
            gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            movie = QMovie(behavior["video"])
            gif_label.setMovie(movie)
            movie.start()

            cell_layout.addWidget(gif_label)
            cell_layout.addStretch(1)

            # ── Exercise button ──────────────────────────────────────────
            btn = QPushButton(behavior["title"] + "\n" + behavior["description"])
            btn.setMinimumSize(400, 200)
            btn.setStyleSheet("""
            QPushButton {
                font-size: 32px;
                font-weight: bold;
                color: black;
                border-radius: 20px;
                background: #FFCCCC;
                border: 3px solid #333;
            }
            QPushButton:hover {
                background: #FFB3B3;
            }
            """)

            btn.clicked.connect(
                lambda _, f=behavior["file"], t=behavior["title"]:
                self.perform_behavior(f, t)
            )

            cell_layout.addWidget(btn)

            grid.addWidget(cell_widget, row, col)

        layout.addStretch(1)

        # ── Home button ──────────────────────────────────────────────────────
        home_button = HomeButton("Return Home")
        layout.addWidget(home_button)
   
        home_button.clicked.connect(lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page))
        layout.addWidget(home_button)

    # ── Load behavior files ──────────────────────────────────────────────────
    # def get_first_six_behaviors(self):
    #     folder = self.parent_ui.behavior_folder
    #     files = [f.replace(".json", "") for f in os.listdir(folder) if f.endswith(".json")]
    #     return files[:6]

    # ── Start behavior ───────────────────────────────────────────────────────
    def start_exercise(self, name):
        """Queue an exercise behavior and return home after a delay."""
        print(f"Starting behavior: {name}")

        # Start behavior from main UI
        self.parent_ui.start_behavior(name)

        # After behavior finishes, return to home
        # If behaviors are synchronous:
        self.return_home_after_delay(3000)

    def return_home_after_delay(self, delay_ms):
        """Schedule a return to the home page after *delay_ms* milliseconds."""
        QTimer.singleShot(delay_ms, self.go_home)

    # def go_home(self):
    #     self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)  # assuming home is a widget

    def load_behavior(self, behavior_file):
        """Load keyframes from a behavior JSON file."""
        with open(behavior_file, 'r') as file:
            return json.load(file)['Keyframes']

    def handle_send_command(self):
        """Parse angle/time inputs and send a single joint command."""
        joint_name = self.joint_name_dropdown.currentText()
        try:
            angle = int(self.angle_input.text())
            move_time = int(self.time_input.text())
        except ValueError:
            print("Please enter valid numbers for angle and move time.")
            return
        joint_id = self.get_joint_id(joint_name)
        self.send_joint_command([joint_id], [angle], move_time)

    def move_to_home(self):
        """Send the robot to its home position via the Home behavior file."""
        self.parent_ui.start_behavior("Home.json")

        # neutral_value = self.emote_mapping.get("Neutral", 1)
        # self._send_emote(neutral_value)

    # def move_to_home(self):
    #     joint_ids = [joint['JointID'] for joint in self.full_joint_config]
    #     home_angles = [joint['HomeAngle'] for joint in self.full_joint_config]
    #     self.send_joint_command(joint_ids, home_angles, 10)

    def set_buttons_enabled(self, enabled: bool):
        """Enable or disable all QPushButtons on this page."""
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(enabled)

    # ── Perform behavior ─────────────────────────────────────────────────────
    def perform_behavior(self, behavior_file, display_title):
        """Lock the UI, show the exercise overlay, and start the behavior."""

        self.set_buttons_enabled(False)

        self.parent_ui.selected_exercise = display_title

        # Find the matching exercise config entry for its GIF and why text
        exercise = next((e for e in self.exercise_config if e["title"] == display_title), None)
        video = exercise["video"] if exercise else None
        why   = exercise["why"]   if exercise else ""

        # Show exercise overlay with GIF and reason
        self.parent_ui.exercise_overlay.set_exercise(display_title, video, why)
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.exercise_overlay)

        # Start behavior with callback
        self.parent_ui.start_behavior(
            behavior_file,
            on_finished=self.on_behavior_finished
        )
        # self.parent_ui.move_to_home()


        # behavior_path = os.path.join(self.behavior_folder, selected_behavior)
        # behavior_motion = self.load_behavior(behavior_path)
        # for frame in behavior_motion:
        #     # Process Audio if available.
        #     if frame.get("AudioClip","") != "":
        #         # Use "AudioClip" if provided; otherwise fall back to the "Expression" or a default.
        #         #audio_clip = keyframe.get("AudioClip", keyframe.get("Expression", "default_audio"))
        #         audio_clip = frame.get("AudioClip")
        #         print("Processing audio keyframe – playing:", audio_clip)
        #         self.audio_manager.process_audio_call(audio_clip)
        #     # Process Emote if available.
        #     if frame.get("Expression","") != "":
        #         expression = frame.get("Expression", "Neutral")
        #         emote_value = self.emote_mapping.get(expression, 0)
        #         self.send_emote(emote_value)
        #     # Process Joint Commands if available.
        #     if frame["HasJoints"] == "True":
        #         joint_ids = [self.get_joint_id(j['Joint']) for j in frame['JointAngles']]
        #         angles = [j['Angle'] for j in frame['JointAngles']]
        #         move_time = frame["JointMoveTime"]
        #         self.send_joint_command(joint_ids, angles, move_time)
        #     self.delay(frame["WaitTime"] / 1000)

    def show_rating_page(self):
        """Navigate to the rating page."""
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.rating_page)

    def on_behavior_finished(self):
        """Called when a behavior completes — re-enable buttons and go home."""
        self.set_buttons_enabled(True)

        self.parent_ui.start_behavior("Home.json", on_finished=self._go_to_rating)

    def _go_to_rating(self):
        """Called once Home.json finishes — safe to show the rating page."""
        self.parent_ui.stack.setCurrentWidget(self.parent_ui.rating_page)


    def closeEvent(self, event):
        self.close_connection()
        event.accept()


# ==============================================================================
# Exercise Overlay
# ==============================================================================

class ExerciseOverlay(QWidget):
    """
    Shown while SAMI performs an exercise.
    Displays the exercise GIF, the exercise title, and a short
    explanation of why the movement is beneficial.
    Call set_exercise() before switching to this page.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # ── Animated GIF ──────────────────────────────────────────────────
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setSizePolicy(
            self.gif_label.sizePolicy().horizontalPolicy(),
            __import__('PyQt6.QtWidgets', fromlist=['QSizePolicy']).QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.gif_label, stretch=3)

        # ── Status label ─────────────────────────────────────────────────
        self.status_label = QLabel("SAMI is moving...")
        self.status_label.setStyleSheet(
            "color: black; font-size: 48px; font-weight: bold;"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label, stretch=1)

        # ── Why-this-exercise label ──────────────────────────────────────
        self.why_label = QLabel()
        self.why_label.setWordWrap(True)
        self.why_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.why_label.setStyleSheet(
            "color: #333; font-size: 28px; font-style: italic;"
        )
        layout.addWidget(self.why_label, stretch=1)

        self._movie = None

    def set_exercise(self, title: str, video_path: str | None, why: str):
        """Update overlay content before it is shown."""
        self.status_label.setText(f"SAMI is performing: {title}")

        # ── Load and start the GIF ───────────────────────────────────────
        if video_path:
            self._movie = QMovie(video_path)
            self.gif_label.setMovie(self._movie)
            self._movie.start()
            self.gif_label.setVisible(True)
        else:
            self.gif_label.setVisible(False)

        self.why_label.setText(why)


# # ==============================================================================
# # Data Page (hub)
# # ==============================================================================

# class DataPage(QWidget):
#     """
#     Hub page replacing the old SensorPage.
#     Presents two navigation buttons: Sensor Data and Rating Data.
#     """

#     def __init__(self, parent_ui):
#         super().__init__()

#         self.parent_ui = parent_ui

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         # -- Page title --
#         title = QLabel("Data")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)
#         layout.addStretch(1)

#         # -- Navigation button grid --
#         grid = QGridLayout()
#         grid.setHorizontalSpacing(40)
#         grid.setVerticalSpacing(40)

#         sections = [
#             ("Sensor Demo", "icons/Sensor.svg"),
#             ("Rating Data", "icons/Rating.png"),
#         ]

#         for col, (name, icon_path) in enumerate(sections):
#             btn = QToolButton()
#             btn.setText(name)
#             btn.setIcon(QIcon(QPixmap(icon_path)))
#             btn.setIconSize(QSize(170, 170))
#             btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
#             btn.setMinimumSize(400, 400)
#             btn.setStyleSheet("""
#                 QToolButton {
#                     color: #000;
#                     font-size: 48px;
#                     font-weight: bold;
#                     padding: 20px;
#                     border-radius: 20px;
#                     background: #FFCCCC;
#                     border: 3px solid #333;
#                 }
#                 QToolButton:hover { background: #FFB3B3; }
#             """)

#             if name == "Sensor Demo":
#                 btn.clicked.connect(
#                     lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.sensor_data_page)
#                 )
#             elif name == "Rating Data":
#                 btn.clicked.connect(
#                     lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.rating_data_page)
#                 )

#             grid.addWidget(btn, 0, col)

#         layout.addLayout(grid)
#         layout.addStretch(1)

#         # -- Home button --
#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
#         )
#         layout.addWidget(home_button)


# # ==============================================================================
# # Sensor Data Page
# # ==============================================================================

# class SensorDataPage(QWidget):
#     """
#     Displays a playable video (capstone-proof.mp4) using Qt's multimedia stack.
#     Provides Play/Pause and Stop controls beneath the video.
#     """

#     def __init__(self, parent_ui):
#         super().__init__()

#         self.parent_ui = parent_ui

#         from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
#         from PyQt6.QtMultimediaWidgets import QVideoWidget
#         from PyQt6.QtCore import QUrl

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(40, 20, 40, 20)
#         layout.setSpacing(16)

#         # -- Page title --
#         title = QLabel("Sensor Demo")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)

#         # -- Video widget --
#         self.video_widget = QVideoWidget()
#         self.video_widget.setMinimumHeight(480)
#         self.video_widget.setStyleSheet("background: #000; border-radius: 12px;")
#         layout.addWidget(self.video_widget)

#         # -- Media player wired to the video widget --
#         self.player = QMediaPlayer()
#         self.audio_output = QAudioOutput()
#         self.player.setAudioOutput(self.audio_output)
#         self.player.setVideoOutput(self.video_widget)
#         self.player.setSource(QUrl.fromLocalFile(
#             os.path.abspath("icons/capstone-proof.mp4")
#         ))

#         # -- Playback controls --
#         controls = QHBoxLayout()
#         controls.setSpacing(24)
#         controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         BTN = """
#             QPushButton {
#                 font-size: 32px; font-weight: bold; color: black;
#                 border-radius: 16px; background: #FFCCCC; border: 3px solid #333;
#                 padding: 12px 40px;
#             }
#             QPushButton:hover { background: #FFB3B3; }
#         """

#         play_btn = QPushButton("\u25b6  Play / Pause")
#         play_btn.setStyleSheet(BTN)
#         play_btn.setMinimumHeight(80)
#         play_btn.clicked.connect(self._toggle_play)
#         controls.addWidget(play_btn)

#         stop_btn = QPushButton("\u25a0  Stop")
#         stop_btn.setStyleSheet(BTN)
#         stop_btn.setMinimumHeight(80)
#         stop_btn.clicked.connect(self._stop)
#         controls.addWidget(stop_btn)

#         layout.addLayout(controls)
#         layout.addStretch(1)

#         # -- Back and Home buttons --
#         nav_row = QHBoxLayout()

#         back_btn = HomeButton("\u2190 Back")
#         back_btn.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.data_page)
#         )
#         nav_row.addWidget(back_btn)

#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
#         )
#         nav_row.addWidget(home_button)
#         layout.addLayout(nav_row)

#     def _toggle_play(self):
#         """Toggle between playing and paused."""
#         from PyQt6.QtMultimedia import QMediaPlayer
#         if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
#             self.player.pause()
#         else:
#             self.player.play()

#     def _stop(self):
#         """Stop playback and return to the beginning."""
#         self.player.stop()


# # ==============================================================================
# # Rating Data Page
# # ==============================================================================

# class RatingDataPage(QWidget):
#     """
#     Displays exercise rating history.
#     Shows per-exercise average summary cards and a full scrollable ratings table.
#     Reloads from disk every time the page is shown.
#     """

#     def __init__(self, parent_ui):
#         super().__init__()

#         self.parent_ui  = parent_ui
#         self.rating_file = "exercise_ratings.txt"

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(40, 20, 40, 20)
#         layout.setSpacing(16)

#         # -- Page title --
#         title = QLabel("Rating Data")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)

#         # -- Section heading --
#         ratings_title = QLabel("Exercise Ratings")
#         ratings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         ratings_title.setStyleSheet("font-size: 36px; font-weight: bold; color: #333;")
#         layout.addWidget(ratings_title)

#         # -- Per-exercise average summary cards (populated dynamically) --
#         self.summary_layout = QHBoxLayout()
#         self.summary_layout.setSpacing(20)
#         layout.addLayout(self.summary_layout)

#         # -- Full ratings table --
#         from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
#         self.table = QTableWidget()
#         self.table.setColumnCount(3)
#         self.table.setHorizontalHeaderLabels(["Timestamp", "Interaction", "Rating"])
#         self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
#         self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         self.table.setStyleSheet("""
#             QTableWidget {
#                 color: #000;
#                 font-size: 22px;
#                 background: #fff;
#                 border-radius: 12px;
#                 border: 2px solid #aaa;
#             }
#             QHeaderView::section {
#                 color: #000;
#                 font-size: 24px;
#                 font-weight: bold;
#                 background: #FFCCCC;
#                 border: 1px solid #aaa;
#                 padding: 6px;
#             }
#         """)
#         self.table.setMinimumHeight(400)
#         layout.addWidget(self.table)

#         # -- Back and Home buttons --
#         nav_row = QHBoxLayout()

#         back_btn = HomeButton("\u2190 Back")
#         back_btn.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.data_page)
#         )
#         nav_row.addWidget(back_btn)

#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
#         )
#         nav_row.addWidget(home_button)
#         layout.addLayout(nav_row)

#     def showEvent(self, event):
#         """Reload ratings from disk every time this page becomes visible."""
#         super().showEvent(event)
#         self._load_ratings()

#     def _load_ratings(self):
#         """
#         Parse exercise_ratings.txt, fill the table, and rebuild summary cards.
#         Each line is expected to be:  timestamp | exercise name | rating
#         """
#         from PyQt6.QtWidgets import QTableWidgetItem
#         from collections import defaultdict

#         # -- Parse the ratings file --
#         rows = []
#         if os.path.exists(self.rating_file):
#             with open(self.rating_file, "r") as f:
#                 for line in f:
#                     parts = [p.strip() for p in line.strip().split("|")]
#                     if len(parts) == 3:
#                         rows.append(parts)

#         # -- Populate the table, most-recent entry first --
#         self.table.setRowCount(len(rows))
#         for r, (ts, exercise, rating) in enumerate(reversed(rows)):
#             self.table.setItem(r, 0, QTableWidgetItem(ts))
#             self.table.setItem(r, 1, QTableWidgetItem(exercise))
#             rating_item = QTableWidgetItem(rating)
#             rating_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
#             self.table.setItem(r, 2, rating_item)
#         if self.table.rowCount() > 0:
#             self.table.setRowHeight(0, 48)

#         # -- Compute per-exercise averages (ignoring "None" entries) --
#         totals: dict = defaultdict(list)
#         for _, exercise, rating in rows:
#             if rating != "None":
#                 try:
#                     totals[exercise].append(int(rating))
#                 except ValueError:
#                     pass

#         # -- Rebuild summary cards, clearing any previous ones first --
#         while self.summary_layout.count():
#             item = self.summary_layout.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()

#         # Color scale mirrors the rating button colors on RatingPage
#         RATING_COLORS = {
#             "1": "#ff4d4d",
#             "2": "#ff944d",
#             "3": "#ffe666",
#             "4": "#b3ff66",
#             "5": "#66ff66",
#         }

#         for exercise, values in sorted(totals.items()):
#             avg   = sum(values) / len(values)
#             color = RATING_COLORS.get(str(round(avg)), "#ccc")
#             card  = QLabel(f"{exercise}\n\u2605 {avg:.1f} ({len(values)} rated)")
#             card.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             card.setWordWrap(True)
#             card.setStyleSheet(f"""
#                 background: {color};
#                 border-radius: 14px;
#                 border: 2px solid #333;
#                 font-size: 22px;
#                 font-weight: bold;
#                 padding: 16px 24px;
#                 color: #333;
#             """)
#             self.summary_layout.addWidget(card)

# class RatingPage(QWidget):
#     def __init__(self, parent_ui):
#         super().__init__()

#         self.parent_ui = parent_ui

#         layout = QVBoxLayout(self)

#         title = QLabel("Rate this Exercise")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)
#         layout.addStretch(1)

#         row = QHBoxLayout()
#         row.setSpacing(40)
#         layout.addLayout(row)

#         self.group = QButtonGroup(self)
#         self.group.setExclusive(True)

#         ratings = [
#             ("Bad", 1, "#ff4d4d", "icons/Bad.png"),
#             ("Poor", 2, "#ff944d", "icons/Poor.png"),
#             ("Neutral", 3, "#ffe666", "icons/Neutral.png"),
#             ("Good", 4, "#b3ff66", "icons/Good.png"),
#             ("Excellent", 5, "#66ff66", "icons/Excellent.png"),
#         ]

#         for label, value, color, icon_path in ratings:
#             rating_btn = QToolButton()
#             rating_btn.setText(label)
#             rating_btn.setCheckable(True)
#             rating_btn.setIcon(QIcon(QPixmap(icon_path)))
#             rating_btn.setIconSize(QSize(170, 170))
#             rating_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
#             rating_btn.setFixedSize(200, 400)
#             rating_btn.setStyleSheet(f"""
#                 QToolButton {{
#                     background-color: {color};
#                     border-radius: 20px;
#                     font-size: 32px;
#                     font-weight: bold;
#                     color: black;
#                     border: 3px solid #333;
#                     padding-top: 60px;
#                     padding-bottom: 40px;
#                 }}
#             """)

#             rating_btn.clicked.connect(lambda _, v=value: self.parent_ui.submit_rating(v))

#             self.group.addButton(rating_btn)
#             row.addWidget(rating_btn)

#         self.no_rate_btn = Button("Prefer Not To Rate", 300, 80, "#E6EEF3")
#         layout.addWidget(self.no_rate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
#         self.no_rate_btn.clicked.connect(lambda: self.parent_ui.submit_rating("None"))

#         layout.addStretch(1)

#         # Add a button to return home
#         home_button = HomeButton("Return Home")
#         layout.addWidget(home_button)

   
#         home_button.clicked.connect(lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page))
#         layout.addWidget(home_button)




# # ============================================================
# # TRIVIA HOME CONFIRMATION DIALOG
# # ============================================================

# class TriviaHomeConfirmDialog(QDialog):
#     """
#     Simple modal: asks the user to confirm before abandoning trivia.
#     Matches the existing #FFCCCC / border: 3px solid #333 aesthetic.
#     """
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Leave Trivia?")
#         self.setModal(True)
#         self.setMinimumWidth(600)
#         self.setStyleSheet("background-color: #96C4DB;")

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(56, 48, 56, 48)
#         layout.setSpacing(36)

#         msg = QLabel("⚠️  Your trivia progress will be lost.\nAre you sure you want to go home?")
#         msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         msg.setWordWrap(True)
#         msg.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; background: transparent;")
#         layout.addWidget(msg)

#         btn_row = QHBoxLayout()
#         btn_row.setSpacing(32)

#         stay_btn   = QPushButton("Cancel — Stay Here")
#         go_btn     = QPushButton("Yes, Go Home")

#         for btn, is_confirm in [(stay_btn, False), (go_btn, True)]:
#             btn.setMinimumHeight(80)
#             btn.setStyleSheet(f"""
#                 QPushButton {{
#                     font-size: 28px;
#                     font-weight: bold;
#                     color: black;
#                     border-radius: 16px;
#                     background: {'#ff6666' if is_confirm else '#FFCCCC'};
#                     border: 3px solid #333;
#                     padding: 12px 28px;
#                 }}
#                 QPushButton:hover {{
#                     background: {'#ff3333' if is_confirm else '#FFB3B3'};
#                 }}
#             """)
#             btn_row.addWidget(btn)

#         stay_btn.clicked.connect(self.reject)
#         go_btn.clicked.connect(self.accept)
#         layout.addLayout(btn_row)


# # ============================================================
# # TRIVIA PAGES
# # ============================================================

# class TriviaPage(QWidget):
#     """Landing page — choose 5 or 10 questions, then start."""
#     def __init__(self, parent_ui):
#         super().__init__()
#         self.parent_ui = parent_ui
#         self._selected_count = None  # will be 5 or 10

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         title = QLabel("Trivia")
#         title.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(title)
#         layout.addStretch(1)

#         # "How many questions?" label
#         choose_label = QLabel("How many questions?")
#         choose_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         choose_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #333;")
#         layout.addWidget(choose_label)

#         layout.addSpacing(16)

#         # 5 / 10 selector row
#         BTN_STYLE = """
#             QPushButton {{
#                 font-size: 48px;
#                 font-weight: bold;
#                 color: black;
#                 border-radius: 20px;
#                 background: {bg};
#                 border: {border};
#             }}
#             QPushButton:hover {{ background: #FFB3B3; }}
#         """
#         NORMAL_BG     = "#FFCCCC"
#         SELECTED_BG   = "#FF8080"
#         NORMAL_BORDER = "3px solid #333"
#         SELECTED_BORDER = "5px solid #000"

#         count_row = QHBoxLayout()
#         count_row.setSpacing(40)
#         count_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         self._btn5  = QPushButton("5 Questions")
#         self._btn10 = QPushButton("10 Questions")

#         for btn in (self._btn5, self._btn10):
#             btn.setMinimumSize(360, 140)
#             btn.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
#             count_row.addWidget(btn)

#         def select_count(count):
#             self._selected_count = count
#             if count == 5:
#                 self._btn5.setStyleSheet(BTN_STYLE.format(bg=SELECTED_BG, border=SELECTED_BORDER))
#                 self._btn10.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
#             else:
#                 self._btn10.setStyleSheet(BTN_STYLE.format(bg=SELECTED_BG, border=SELECTED_BORDER))
#                 self._btn5.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))
#             self._start_btn.setEnabled(True)
#             self._start_btn.setStyleSheet(BTN_STYLE.format(bg=NORMAL_BG, border=NORMAL_BORDER))

#         self._btn5.clicked.connect(lambda: select_count(5))
#         self._btn10.clicked.connect(lambda: select_count(10))

#         layout.addLayout(count_row)
#         layout.addSpacing(32)

#         # Start button — disabled until a count is chosen
#         self._start_btn = QPushButton("Start Trivia")
#         self._start_btn.setMinimumSize(400, 140)
#         self._start_btn.setEnabled(False)
#         self._start_btn.setStyleSheet("""
#             QPushButton {
#                 font-size: 48px;
#                 font-weight: bold;
#                 color: #888;
#                 border-radius: 20px;
#                 background: #e0e0e0;
#                 border: 3px solid #aaa;
#             }
#         """)
#         self._start_btn.clicked.connect(self._start_trivia)
#         layout.addWidget(self._start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

#         layout.addStretch(1)

#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(
#             lambda _: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
#         )
#         layout.addWidget(home_button)

#     def showEvent(self, event):
#         """Reset selection every time the page is shown."""
#         super().showEvent(event)
#         self._selected_count = None
#         BTN_STYLE = """
#             QPushButton {{
#                 font-size: 48px; font-weight: bold; color: black;
#                 border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
#             }}
#             QPushButton:hover {{ background: #FFB3B3; }}
#         """
#         self._btn5.setStyleSheet(BTN_STYLE.format())
#         self._btn10.setStyleSheet(BTN_STYLE.format())
#         self._start_btn.setEnabled(False)
#         self._start_btn.setStyleSheet("""
#             QPushButton {
#                 font-size: 48px; font-weight: bold; color: #888;
#                 border-radius: 20px; background: #e0e0e0; border: 3px solid #aaa;
#             }
#         """)

#     def _start_trivia(self):
#         self.parent_ui.trivia_load_questions(limit=self._selected_count)
#         self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
#         self.parent_ui.trivia_question_page.load_question()

# class TriviaQuestionPage(QWidget):
#     """Shows the current question and four answer buttons."""
#     def __init__(self, parent_ui):
#         super().__init__()
#         self.parent_ui = parent_ui

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         # Counter + score row
#         info_row = QHBoxLayout()
#         self.counter_label = QLabel("Question 1 / ?")
#         self.counter_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
#         self.score_label = QLabel("Score: 0 / 0")
#         self.score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
#         info_row.addWidget(self.counter_label)
#         info_row.addStretch()
#         info_row.addWidget(self.score_label)
#         layout.addLayout(info_row)

#         self.question_label = QLabel()
#         self.question_label.setWordWrap(True)
#         self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.question_label.setStyleSheet("""
#             font-size: 36px;
#             font-weight: bold;
#             color: #333;
#             background: #fff;
#             border-radius: 16px;
#             border: 3px solid #333;
#             padding: 24px 32px;
#         """)
#         layout.addWidget(self.question_label)
#         layout.addStretch(1)

#         self.answers_grid = QGridLayout()
#         self.answers_grid.setSpacing(24)
#         layout.addLayout(self.answers_grid)
#         self.answer_buttons = []

#         layout.addStretch(1)

#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(self._confirm_go_home)
#         layout.addWidget(home_button)

#     def _confirm_go_home(self, *_):
#         dlg = TriviaHomeConfirmDialog(self)
#         if dlg.exec() == QDialog.DialogCode.Accepted:
#             self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

#     def load_question(self):
#         q = self.parent_ui.trivia_current_question()
#         if not q:
#             return

#         total   = len(self.parent_ui.trivia_questions)
#         current = self.parent_ui.trivia_index + 1
#         score   = self.parent_ui.trivia_score

#         self.counter_label.setText(f"Question {current} / {total}")
#         self.score_label.setText(f"Score: {score} / {self.parent_ui.trivia_index}")
#         self.question_label.setText(q["question"])

#         # Rebuild answer buttons
#         for btn in self.answer_buttons:
#             self.answers_grid.removeWidget(btn)
#             btn.deleteLater()
#         self.answer_buttons = []

#         options = [("A", q["option_a"]), ("B", q["option_b"]),
#                    ("C", q["option_c"]), ("D", q["option_d"])]

#         for i, (letter, text) in enumerate(options):
#             row, col = divmod(i, 2)
#             btn = QPushButton(f"{letter}.  {text}")
#             btn.setMinimumSize(600, 130)
#             btn.setStyleSheet("""
#                 QPushButton {
#                     font-size: 28px;
#                     font-weight: bold;
#                     color: black;
#                     border-radius: 20px;
#                     background: #FFCCCC;
#                     border: 3px solid #333;
#                     text-align: left;
#                     padding-left: 24px;
#                 }
#                 QPushButton:hover { background: #FFB3B3; }
#             """)
#             btn.clicked.connect(lambda _, l=letter: self._submit(l))
#             self.answers_grid.addWidget(btn, row, col)
#             self.answer_buttons.append(btn)

#     def _submit(self, letter):
#         self.parent_ui.trivia_submit_answer(letter)
#         self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_answer_page)
#         self.parent_ui.trivia_answer_page.refresh()


# class TriviaAnswerPage(QWidget):
#     """Shows correct/wrong feedback and a Next button."""
#     def __init__(self, parent_ui):
#         super().__init__()
#         self.parent_ui = parent_ui

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         layout.addStretch(1)

#         self.result_label = QLabel()
#         self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(self.result_label)

#         self.correct_label = QLabel()
#         self.correct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.correct_label.setStyleSheet("font-size: 36px; color: #333;")
#         layout.addWidget(self.correct_label)

#         self.score_label = QLabel()
#         self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
#         layout.addWidget(self.score_label)

#         layout.addStretch(1)

#         next_btn = QPushButton("Next Question")
#         next_btn.setMinimumSize(400, 120)
#         next_btn.setStyleSheet("""
#             QPushButton {
#                 font-size: 40px;
#                 font-weight: bold;
#                 color: black;
#                 border-radius: 20px;
#                 background: #FFCCCC;
#                 border: 3px solid #333;
#             }
#             QPushButton:hover { background: #FFB3B3; }
#         """)
#         next_btn.clicked.connect(self._next)
#         layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

#         layout.addStretch(1)

#         home_button = HomeButton("Return Home")
#         home_button.clicked.connect(self._confirm_go_home)
#         layout.addWidget(home_button)

#     def _confirm_go_home(self, *_):
#         dlg = TriviaHomeConfirmDialog(self)
#         if dlg.exec() == QDialog.DialogCode.Accepted:
#             self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)

#     def refresh(self):
#         was_correct = self.parent_ui.trivia_last_correct
#         q = self.parent_ui.trivia_current_question(offset=-1)
#         correct_text = q["correct_answer"] if q else ""

#         if was_correct:
#             self.result_label.setText("✅  Correct!")
#             self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #2a9d2a;")
#         else:
#             self.result_label.setText("❌  Wrong!")
#             self.result_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #cc2222;")

#         self.correct_label.setText(f"Answer: {correct_text}")
#         answered = self.parent_ui.trivia_index
#         self.score_label.setText(
#             f"Score: {self.parent_ui.trivia_score} / {answered}"
#         )

#     def _next(self):
#         if self.parent_ui.trivia_index >= len(self.parent_ui.trivia_questions):
#             self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_score_page)
#             self.parent_ui.trivia_score_page.refresh()
#         else:
#             self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
#             self.parent_ui.trivia_question_page.load_question()


# class TriviaScorePage(QWidget):
#     """Final score screen with Play Again and Go Home options."""
#     def __init__(self, parent_ui):
#         super().__init__()
#         self.parent_ui = parent_ui

#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(10, 0, 10, 10)
#         layout.setSpacing(8)

#         layout.addStretch(2)

#         trophy = QLabel("🏆")
#         trophy.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         trophy.setStyleSheet("font-size: 100px;")
#         layout.addWidget(trophy)

#         self.score_label = QLabel()
#         self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.score_label.setStyleSheet("font-size: 64px; font-weight: bold; color: #333;")
#         layout.addWidget(self.score_label)

#         self.msg_label = QLabel()
#         self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.msg_label.setStyleSheet("font-size: 36px; color: #333;")
#         layout.addWidget(self.msg_label)

#         layout.addStretch(1)

#         btn_row = QHBoxLayout()
#         btn_row.setSpacing(40)

#         play_again_btn = QPushButton("Play Again")
#         play_again_btn.setMinimumSize(360, 120)
#         play_again_btn.setStyleSheet("""
#             QPushButton {
#                 font-size: 40px; font-weight: bold; color: black;
#                 border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
#             }
#             QPushButton:hover { background: #FFB3B3; }
#         """)
#         play_again_btn.clicked.connect(self._play_again)
#         btn_row.addWidget(play_again_btn)

#         home_btn = QPushButton("Go Home")
#         home_btn.setMinimumSize(360, 120)
#         home_btn.setStyleSheet("""
#             QPushButton {
#                 font-size: 40px; font-weight: bold; color: black;
#                 border-radius: 20px; background: #FFCCCC; border: 3px solid #333;
#             }
#             QPushButton:hover { background: #FFB3B3; }
#         """)
#         home_btn.clicked.connect(
#             lambda: self.parent_ui.stack.setCurrentWidget(self.parent_ui.home_page)
#         )
#         btn_row.addWidget(home_btn)

#         layout.addLayout(btn_row, )
#         layout.addStretch(2)

#     def refresh(self):
#         total = len(self.parent_ui.trivia_questions)
#         score = self.parent_ui.trivia_score
#         self.score_label.setText(f"Final Score:  {score} / {total}")
#         pct = int(score / total * 100) if total else 0
#         if pct == 100:
#             msg = "Perfect score! Amazing! 🎉"
#         elif pct >= 70:
#             msg = "Great job! Keep it up! 👍"
#         elif pct >= 40:
#             msg = "Good effort! Want to try again?"
#         else:
#             msg = "Better luck next time! 💪"
#         self.msg_label.setText(msg)

#     def _play_again(self):
#         self.parent_ui.trivia_load_questions()
#         self.parent_ui.stack.setCurrentWidget(self.parent_ui.trivia_question_page)
#         self.parent_ui.trivia_question_page.load_question()


# ==============================================================================
# SAMIControlUI  —  Main application window
# ==============================================================================

class SAMIControlUI(SAMIControl, QMainWindow):
    """
    Top-level window that combines SAMIControl (robot comms) with a
    QMainWindow (PyQt6 UI).  Manages the page stack, trivia state, and
    exercise ratings.
    """

    def __init__(self, 
                 arduino_port='/dev/tty.usbserial-10', 
                 baud_rate=115200,
                 joint_config_file='Joint_config.json',
                 behavior_folder='behaviors',
                 emote_file='Emote.json',
                 audio_folder='audio',
                 starting_voice='Matt'):
        SAMIControl.__init__(self, arduino_port, baud_rate, joint_config_file,behavior_folder, emote_file, audio_folder, starting_voice)
        # QWidget.__init__(self)
        QMainWindow.__init__(self)
        with open(joint_config_file, 'r') as f:
            self.full_joint_config = json.load(f)['JointConfig']
        self.full_joint_map = {joint['JointName']: joint for joint in self.full_joint_config}
        self.behavior_folder = behavior_folder if os.path.exists(behavior_folder) else 'behaviors'
        self.emote_mapping = self.load_emote_mapping(emote_file)

        self.selected_exercise = None
        self.last_rating = None
        self.rating_file = "exercise_ratings.txt"

        # ── Trivia state ─────────────────────────────────────────────────
        self.trivia_questions = []
        self.trivia_index = 0
        self.trivia_score = 0
        self.trivia_last_correct = False
        self.trivia_csv = "trivia_questions.csv"

        self.initUI()

        if arduino_port:
            try:
                self.initialize_serial_connection()
            except Exception as e:
                print(f"Could not connect to Arduino: {e} — running in UI-only mode.")

    def delay(self, t):
        """Block the current thread for *t* seconds."""
        time.sleep(t)

    # ── UI entry point ─────────────────────────────────────────────────────────
    def initUI(self):
        """Dispatch to the appropriate UI based on the USE_NEW_UI flag at the top of the file."""
        if USE_NEW_UI:
            self._initUI_new()
        else:
            self._initUI_legacy()

    # ── New presentation UI ────────────────────────────────────────────────────
    def _initUI_new(self):
        """Full presentation UI: stacked pages, trivia, exercise overlay, data pages."""
        self.setWindowTitle("SAMI UI")
        self.resize(1920, 1080)
        self.setStyleSheet("background-color: #96C4DB;")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page          = HomePage(self);          self.stack.addWidget(self.home_page)
        self.exercise_page      = ExercisePage(self);      self.stack.addWidget(self.exercise_page)
        self.exercise_overlay   = ExerciseOverlay();       self.stack.addWidget(self.exercise_overlay)
        self.data_page          = DataPage(self);          self.stack.addWidget(self.data_page)
        self.sensor_data_page   = SensorDataPage(self);    self.stack.addWidget(self.sensor_data_page)
        self.rating_data_page   = RatingDataPage(self);    self.stack.addWidget(self.rating_data_page)
        self.rating_page        = RatingPage(self);        self.stack.addWidget(self.rating_page)
        self.trivia_page        = TriviaPage(self);        self.stack.addWidget(self.trivia_page)
        self.trivia_question_page = TriviaQuestionPage(self); self.stack.addWidget(self.trivia_question_page)
        self.trivia_answer_page = TriviaAnswerPage(self);  self.stack.addWidget(self.trivia_answer_page)
        self.trivia_score_page  = TriviaScorePage(self);   self.stack.addWidget(self.trivia_score_page)

        self.stack.setCurrentWidget(self.home_page)

    # ── Legacy debug UI ────────────────────────────────────────────────────────
    def _initUI_legacy(self):
        """Original debug UI: joint dropdowns, angle inputs, raw command buttons."""
        from PyQt6.QtWidgets import QLineEdit, QComboBox

        self.resize(600, 400)
        self.setWindowTitle("SAMI Control")

        container = QWidget()
        layout = QVBoxLayout(container)
        self.setCentralWidget(container)

        self.joint_name_dropdown = QComboBox(self)
        self.joint_name_dropdown.addItems(list(self.full_joint_map.keys()))
        layout.addWidget(self.joint_name_dropdown)

        self.angle_input = QLineEdit(self)
        self.angle_input.setPlaceholderText("Enter Angle")
        layout.addWidget(self.angle_input)

        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Enter Move Time")
        layout.addWidget(self.time_input)

        send_button = QPushButton("Send Command", self)
        send_button.clicked.connect(self.handle_send_command)
        layout.addWidget(send_button)

        home_button = QPushButton("Home", self)
        home_button.clicked.connect(self.move_to_home)
        layout.addWidget(home_button)

        self.behavior_dropdown = QComboBox(self)
        self.behavior_dropdown.addItems(self.get_behavior_files())
        layout.addWidget(self.behavior_dropdown)

        behavior_button = QPushButton("Perform Behavior", self)
        behavior_button.clicked.connect(self.perform_behavior)
        layout.addWidget(behavior_button)


    def load_behavior(self, behavior_file):
        """Load keyframes from a behavior JSON file."""
        with open(behavior_file, 'r') as file:
            return json.load(file)['Keyframes']

    def handle_send_command(self):
        """Parse the angle/time inputs and send a single joint command."""
        joint_name = self.joint_name_dropdown.currentText()
        try:
            angle = int(self.angle_input.text())
            move_time = int(self.time_input.text())
        except ValueError:
            print("Please enter valid numbers for angle and move time.")
            return
        joint_id = self.get_joint_id(joint_name)
        self.send_joint_command([joint_id], [angle], move_time)

    def move_to_home(self):
        """Send all joints to their home angles."""
        joint_ids = [joint['JointID'] for joint in self.full_joint_config]
        home_angles = [joint['HomeAngle'] for joint in self.full_joint_config]
        self.send_joint_command(joint_ids, home_angles, 10)

    def get_behavior_files(self):
        """Return a list of .json files in the behavior folder."""
        return [f for f in os.listdir(self.behavior_folder) if f.endswith('.json')]

    def perform_behavior(self):
        """Start the behavior selected in the legacy dropdown."""
        selected_behavior = self.behavior_dropdown.currentText()
        self.start_behavior(selected_behavior)
        # behavior_path = os.path.join(self.behavior_folder, selected_behavior)
        # behavior_motion = self.load_behavior(behavior_path)
        # for frame in behavior_motion:
        #     # Process Audio if available.
        #     if frame.get("AudioClip","") != "":
        #         # Use "AudioClip" if provided; otherwise fall back to the "Expression" or a default.
        #         #audio_clip = keyframe.get("AudioClip", keyframe.get("Expression", "default_audio"))
        #         audio_clip = frame.get("AudioClip")
        #         print("Processing audio keyframe – playing:", audio_clip)
        #         self.audio_manager.process_audio_call(audio_clip)
        #     # Process Emote if available.
        #     if frame.get("Expression","") != "":
        #         expression = frame.get("Expression", "Neutral")
        #         emote_value = self.emote_mapping.get(expression, 0)
        #         self.send_emote(emote_value)
        #     # Process Joint Commands if available.
        #     if frame["HasJoints"] == "True":
        #         joint_ids = [self.get_joint_id(j['Joint']) for j in frame['JointAngles']]
        #         angles = [j['Angle'] for j in frame['JointAngles']]
        #         move_time = frame["JointMoveTime"]
        #         self.send_joint_command(joint_ids, angles, move_time)
        #     self.delay(frame["WaitTime"] / 1000)

    def closeEvent(self, event):
        """Close the serial connection before the window is destroyed."""
        self.close_connection()
        event.accept()

    # ── Rating helpers ─────────────────────────────────────────────────────────

    def submit_rating(self, value):
        """Persist the user's exercise rating to disk, then return home."""
        import datetime

        interaction = self.selected_exercise or "Unknown"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"{timestamp} | {interaction} | {value}\n"

        with open(self.rating_file, "a") as f:
            f.write(line)

        self.last_rating = value

        # ── Return to home page after rating ─────────────────────────────
        self.stack.setCurrentWidget(self.home_page)

    # ── Trivia helpers ─────────────────────────────────────────────────────────

    def trivia_load_questions(self, limit=None):
        """Shuffle trivia CSV and optionally cap at *limit* questions."""
        path = self.trivia_csv
        if not os.path.exists(path):
            print(f"Trivia CSV not found: {path}")
            self.trivia_questions = []
            return
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_questions = list(reader)
        random.shuffle(all_questions)
        if limit:
            all_questions = all_questions[:limit]
        self.trivia_questions = all_questions
        self.trivia_index = 0
        self.trivia_score = 0
        self.trivia_last_correct = False

    def trivia_current_question(self, offset=0):
        """Return the question dict at the current index (+ optional offset)."""
        idx = self.trivia_index + offset
        if 0 <= idx < len(self.trivia_questions):
            return self.trivia_questions[idx]
        return None

    def trivia_submit_answer(self, letter):
        """Check the chosen letter against the correct answer and advance."""
        q = self.trivia_current_question()
        if not q:
            return
        correct_text = q["correct_answer"].strip().lower()
        chosen_text  = q[f"option_{letter.lower()}"].strip().lower()
        self.trivia_last_correct = (chosen_text == correct_text)
        if self.trivia_last_correct:
            self.trivia_score += 1
        self.trivia_index += 1


def main():
    app = QApplication([])
    window = SAMIControlUI(audio_folder="audio", starting_voice="Matt")
    window.show()  
    app.exec()

if __name__ == "__main__":
    main()