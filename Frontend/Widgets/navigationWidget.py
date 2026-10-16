from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QLabel,
    QFrame
)
from PyQt6.QtGui import QIcon
from pathlib import Path

class NavigationWidget(QWidget):
    def __init__(self, show_dataset_path = True, show_image_name = True):
        super().__init__()

        assets_dir = Path("utils")
        self.num_data = QLabel("Total: 0")
        self.show_dataset_path = show_dataset_path
        self.show_image_name = show_image_name

        if self.show_dataset_path:
            self.current_dataset_path = QLabel("No dataset selected")

        if self.show_image_name:
            self.current_img_path = QLineEdit("No image available")
            self.current_img_path.setReadOnly(True)
            self.current_img_path.setStyleSheet(
                "background-color: #2c2c2e; "
                "color: #2c2c2e; "
                "border: none; " 
                "outline: none; "
                "border-radius: 0px; "
                "padding: 4px;"
            )
        self.num_data.setStyleSheet("color: #8e8e93; font-size: 11px; background: transparent;")
        self.num_data.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        if self.show_dataset_path:
            self.current_dataset_path.setStyleSheet("color: #8e8e93; font-size: 11px; background: transparent;")
            self.current_dataset_path.setAlignment(Qt.AlignmentFlag.AlignRight)

        if self.show_image_name:
            self.current_img_path.setStyleSheet("color: #8e8e93; font-size: 11px; background: transparent;")
            self.current_img_path.setAlignment(Qt.AlignmentFlag.AlignRight)

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

        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self._create_ui()
    
    def _create_ui(self):
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.num_data)

        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_layout.addStretch()       
        
        separator = QFrame()
        separator.setObjectName("SeparatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        if self.show_dataset_path:
            self.bottom_layout.addWidget(self.current_dataset_path)
        if self.show_image_name:
            self.bottom_layout.addWidget(self.current_img_path)
        
        self.bottom_layout.addSpacing(15)
        self.bottom_layout.addWidget(separator)
        self.bottom_layout.addSpacing(15)

        self.general_layout.addLayout(self.top_layout)
        self.nav_layout.addWidget(self.previous_button)
        self.nav_layout.addWidget(self.entry_index)
        self.nav_layout.addWidget(self.next_button)

        self.general_layout.addLayout(self.nav_layout)
        self.general_layout.addLayout(self.bottom_layout)


    def set_index(self, value):
        self.entry_index.setText(str(value))

    def set_total_images(self, total):
        self.num_data.setText(f"Total: {total}")

    def set_img_path(self, path):
        if self.show_image_name:
            self.current_img_path.setText(path)

    def set_dataset_path(self, path):
        if self.show_dataset_path:
            self.current_dataset_path.setText(path)