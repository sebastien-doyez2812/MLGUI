from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QLabel
)
from PyQt6.QtGui import QIcon
from pathlib import Path

class NavigationWidget(QWidget):
    def __init__(self):
        super().__init__()

        assets_dir = Path("utils")
        self.num_data = QLabel("Total: 0")
        self.num_data.setStyleSheet("color: #8e8e93; font-size: 11px; background: transparent;")
        self.num_data.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.previous_button = QPushButton()
        prev_icon_path = assets_dir / "previous.png"
        if prev_icon_path.exists():
            self.previous_button.setIcon(QIcon(str(prev_icon_path)))

        self.next_button = QPushButton()
        next_icon_path = assets_dir / "next.png"
        if next_icon_path.exists():
            self.next_button.setIcon(QIcon(str(next_icon_path)))
                   
        self.entry_index = QLineEdit("0")


        self.general_layout = QVBoxLayout(self)
        self.general_layout.setContentsMargins(0, 0, 0, 0)
        self.general_layout.setSpacing(4)

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.num_data)

        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self._create_ui()
    
    def _create_ui(self):
        self.general_layout.addLayout(self.top_layout)
        self.nav_layout.addWidget(self.previous_button)
        self.nav_layout.addWidget(self.entry_index)
        self.nav_layout.addWidget(self.next_button)
        
        self.general_layout.addLayout(self.nav_layout)

    def set_index(self, value):
        self.entry_index.setText(str(value))

    def set_total_images(self, total):
        self.num_data.setText(f"Total: {total}")
