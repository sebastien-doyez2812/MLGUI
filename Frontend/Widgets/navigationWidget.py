from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLineEdit
)
from PyQt6.QtGui import QIcon
from pathlib import Path

class NavigationWidget(QWidget):
    def __init__(self):
        super().__init__()

        assets_dir = Path("utils")

        self.previous_button = QPushButton()
        prev_icon_path = assets_dir / "previous.png"
        if prev_icon_path.exists():
            self.previous_button.setIcon(QIcon(str(prev_icon_path)))

        self.next_button = QPushButton()
        next_icon_path = assets_dir / "next.png"
        if next_icon_path.exists():
            self.next_button.setIcon(QIcon(str(next_icon_path)))
                   
        self.entry_index = QLineEdit("0")
        self.layout = QHBoxLayout(self)

        self._create_ui()
    
    def _create_ui(self):
        self.layout.addWidget(self.previous_button)
        self.layout.addWidget(self.entry_index)
        self.layout.addWidget(self.next_button)

    def set_index(self, value):
        self.entry_index.setText(str(value))
