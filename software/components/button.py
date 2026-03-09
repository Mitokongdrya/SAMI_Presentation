from PyQt6.QtWidgets import QToolButton, QPushButton
from PyQt6.QtGui import QIcon, QPixmap 
from PyQt6.QtCore import Qt, QSize



class Button(QToolButton):
    def __init__(self, text, width, height, color):
        super().__init__()
        self.setText(text)
        self.setMinimumSize(width, height)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setStyleSheet(f"""
            QToolButton {{
                background-color: {color};
                color: #2C3E50;
                border: 2px solid #000;
                border-radius: 20px;
                font-size: 40px;
                font-weight: 600;
                padding: 16px 32px;
                padding-left: 48px;  
            }}
        """)
