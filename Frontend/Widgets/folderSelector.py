from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog

class FolderSelector(QWidget):
    folderSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.browse_btn = QPushButton("📁 Select a dataset...")
        self.browse_btn.clicked.connect(self.open_folder_dialog)

        self.folder_label = QLabel("No dataset selected")
        self.folder_label.setStyleSheet("color: #8e8e93; font-style: italic; font-size: 12px;")

        layout.addWidget(self.browse_btn)
        layout.addWidget(self.folder_label)
        layout.addStretch()

    def open_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select the dataset")
        if dir_path:
            self.selected_path = dir_path
            
            shortened_path = f"...{dir_path[-35:]}" if len(dir_path) > 35 else dir_path
            self.folder_label.setText(shortened_path)
            self.folder_label.setStyleSheet("color: #ffffff; font-style: normal; font-size: 12px;")
            self.folder_label.setToolTip(dir_path) 

            self.folderSelected.emit(dir_path)