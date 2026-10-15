from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)
from Frontend.Widgets.navigationWidget import NavigationWidget
from Frontend.Widgets.viewer3DWidget import Segmentation3DViewer

class Segmentation3DPage(QWidget):
    name = "Segmentation3D"
    index_nav_bar = 2

    def __init__(self, model_ref=None):
        super().__init__()
        self.model = model_ref  

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.menu_container = QFrame()
        self.menu_container.setFixedWidth(260)
        self.menu_container.setStyleSheet("background-color: #2b2b2b; border-right: 1px solid #3f3f3f;")
        
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(15)

        self.open_folder_btn = QPushButton("Open Folder")
        self.export_btn = QPushButton("Export")
        
        self.navigation_widget = NavigationWidget()

        self.opengl_viewer = Segmentation3DViewer(self)
        self.opengl_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.open_folder_btn.clicked.connect(self.open_folder_dialog)

        self.init_ui()

    def init_ui(self):
        open_and_export = QHBoxLayout()
        open_and_export.addWidget(self.open_folder_btn)
        open_and_export.addWidget(self.export_btn)
        
        self.menu_layout.addLayout(open_and_export)
        self.menu_layout.addWidget(self.navigation_widget)   

        self.menu_layout.addStretch()

        self.main_layout.addWidget(self.menu_container, stretch=0)
        self.main_layout.addWidget(self.opengl_viewer, stretch=1)

    def open_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if dir_path:
            print(f"Dossier 3D sélectionné : {dir_path}")