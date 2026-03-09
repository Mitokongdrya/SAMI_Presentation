from PyQt6.QtWidgets import QToolButton
from PyQt6.QtGui import QIcon, QPixmap 
from PyQt6.QtCore import Qt, QSize



class HomeButton(QToolButton):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setMinimumSize(400, 150)
        self.setIcon(QIcon(QPixmap("icons/home.png")))
        self.setIconSize(QSize(100, 100))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        # self.setMinimumSize(400, 400)
        self.setStyleSheet("""
            QToolButton {
                background-color: #E6EEF3;
                color: #2C3E50;
                border: 2px dashed #6BAED6;
                border-radius: 20px;
                font-size: 40px;
                font-weight: 600;
                padding: 16px 32px;
                padding-left: 48px;  
            }
        """)

    @property
    def home_clicked(self):
        return self.clicked