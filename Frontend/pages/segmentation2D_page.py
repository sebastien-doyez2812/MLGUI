from PyQt6.QtCore import Qt, QModelIndex, QRectF
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QSlider
)
from pathlib import Path
import os
from Frontend.Widgets.navigationWidget import NavigationWidget
from Frontend.roles import *

class Segmentation2DPage(QWidget):
    name = "Segmentation2D"
    index_nav_bar = 1

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

        for btn in [self.open_folder_btn, self.export_btn]:
            btn.setStyleSheet("padding: 6px 12px; font-weight: bold;")

        self.contrast_label = QLabel("Contrast:")
        self.contrast_cursor = QSlider(Qt.Orientation.Horizontal)
        self.contrast_cursor.setRange(0, 100)
        self.contrast_cursor.setValue(50)

        self.lum_label = QLabel("Luminosity:")
        self.lum_cursor = QSlider(Qt.Orientation.Horizontal)
        self.lum_cursor.setRange(0, 100)
        self.lum_cursor.setValue(50)

        self.image_scene = QGraphicsScene(self)
        self.image_viewer = QGraphicsView(self.image_scene)
        self.image_viewer.setStyleSheet("background-color: #1e1e1e; border: none;")
        self.image_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        placeholder = self.image_scene.addText("No folder loaded")
        placeholder.setDefaultTextColor(Qt.GlobalColor.gray)

        self.open_folder_btn.clicked.connect(self.open_folder_dialog)
        self.navigation_widget.next_button.clicked.connect(self.next_img)
        self.navigation_widget.previous_button.clicked.connect(self.previous_img)

        self.connection()
        self.init_ui()

    def connection(self):
        if self.model is not None:
            self.model.dataChanged.connect(self.on_model_data_changed)

    def on_model_data_changed(self, top_left, bottom_right, roles ):
        for role in roles:
            match int(role):
                case int(LOAD_CURRIMG_ROLE):
                    img_path = self.model.data(self.model.index(0,0), role= LOAD_CURRIMG_ROLE)
                    if img_path: 
                        print(img_path)
                        self.image_scene.clear()
                        pixmap = QPixmap(str(img_path))
                        self.image_scene.addPixmap(pixmap)
                        self.image_viewer.setSceneRect(QRectF(pixmap.rect()))

                case int(NEXT_IMG_ROLE):
                    img_path = self.model.data(self.model.index(0,0), role= LOAD_CURRIMG_ROLE)

                case int(PREVIOUS_IMG_ROLE):
                    img_path = self.model.data(self.model.index(0,0), role= LOAD_CURRIMG_ROLE)

                case _:
                    return

    def init_ui(self):
        open_and_export = QHBoxLayout()
        open_and_export.addWidget(self.open_folder_btn)
        open_and_export.addWidget(self.export_btn)
        self.menu_layout.addLayout(open_and_export)
        
        self.menu_layout.addWidget(self.navigation_widget)   
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.contrast_label)
        controls_layout.addWidget(self.contrast_cursor)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.lum_label)
        controls_layout.addWidget(self.lum_cursor)
        self.menu_layout.addLayout(controls_layout)

        self.menu_layout.addStretch()
        self.main_layout.addWidget(self.menu_container, stretch=0)

        self.main_layout.addWidget(self.image_viewer, stretch=1)

    def next_img(self):
        if self.model is not None:
            self.model.setData(
                self.model.index(0, 0), 
                None, 
                int(NEXT_IMG_ROLE)
            )

    def previous_img(self):
        if self.model is not None:
            self.model.setData(
                self.model.index(0, 0), 
                None, 
                int(PREVIOUS_IMG_ROLE)
            )

    def open_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if dir_path:
            img_path = os.path.join(dir_path, "imgs")
            labels_path = os.path.join(dir_path, "labels")

            if os.path.exists(img_path) and os.path.exists(labels_path):
                if self.model is not None:
                    self.model.setData(
                        self.model.index(0, 0), 
                        dir_path, 
                        int(LOAD_DATA_ROLE)
                    )
            else:
                print(f"{img_path} or {labels_path} not ok")