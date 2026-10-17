from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsView,
    QSizePolicy,
    QWidget,
    QGraphicsScene,
    QScrollArea,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage, QPainter
from Frontend.Widgets.navigationWidget import NavigationWidget
from Frontend.Widgets.folderSelector import FolderSelector
from Frontend.Widgets.ZoomableGraphicsView import ZoomableGraphicsView
from Frontend.Widgets.analysisWidget import AnalysisWidget
from Frontend.roles import LOAD_AUG_DATASET, GET_STATISTICS
import os, json, cv2
import numpy as np
from pathlib import Path


class DatasetViewerPage(QWidget):
    name = "Viewer"
    index_nav_bar = 2

    def __init__(self, model_ref=None, nb_classes = 8):
        super().__init__()
        self.model = model_ref  
        self.nb_classes = nb_classes
        self.current_idx = 0

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        self.navWidget = NavigationWidget(show_dataset_path= False, show_image_name= False, show_bin_icon= True)
        self.navWidget.next_button.clicked.connect(self.next_image)
        self.navWidget.previous_button.clicked.connect(self.prev_image)

        self.folderExplorer = FolderSelector()
        self.folderExplorer.folderSelected.connect(self.onFolderSelected)
        if self.model:
            self.model.dataChanged.connect(self.onDataChanged)

        self.analysisGraphs = AnalysisWidget(self.nb_classes, self)

        self.init_ui()

    def connexion(self):
        if self.model is None:
            print("[-] Error datasetViewerPage: model not set!")
        self.model.dataChanged.connect(self.onDataChanged)

    def onDataChanged(self, top_left, bottom_right, roles = None):
        for role in roles:
            if int(role) == int(LOAD_AUG_DATASET):
                path = self.model.data(self.model.index(0,0), LOAD_AUG_DATASET)
                self.load_data(path)

    def onFolderSelected(self, dataset_path):
        self.model.setData(self.model.index(0, 0), dataset_path, LOAD_AUG_DATASET)


    def init_ui(self):
        title = QLabel("Visualization and Dataset Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff; margin-bottom: 2px;")
        self.mainLayout.addWidget(title)

        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(15)
        
        self.folderExplorer.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        top_bar_layout.addWidget(self.folderExplorer)

        top_bar_layout.addStretch() 

        self.navWidget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        top_bar_layout.addWidget(self.navWidget)
        
        self.mainLayout.addLayout(top_bar_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)

        self.preview_panels = {}

        main_views_layout = QHBoxLayout()
        main_views_layout.setSpacing(15)

        raw_card = self.create_preview_card("Image Brute (Raw)", min_w=300, min_h=220)
        main_views_layout.addWidget(raw_card["frame"], stretch=1)
        self.preview_panels["raw"] = raw_card

        overlay_card = self.create_preview_card("Overlay Final", min_w=300, min_h=220)
        main_views_layout.addWidget(overlay_card["frame"], stretch=1)
        self.preview_panels["overlay"] = overlay_card

        content_layout.addLayout(main_views_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #3a3a3c; max-height: 1px;")
        content_layout.addWidget(separator)

        classes_title = QLabel("Masks by Classes (Bits)")
        classes_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #007AFF;")
        content_layout.addWidget(classes_title)

        classes_grid = QGridLayout()
        classes_grid.setSpacing(10)
        classes_grid.setContentsMargins(0, 0, 0, 0)

        row, col = 0, 0
        for i in range(self.nb_classes):
            class_card = self.create_preview_card(f"Class {i}", min_w=160, min_h=120)
            classes_grid.addWidget(class_card["frame"], row, col)
            self.preview_panels[f"class_{i}"] = class_card
            
            col += 1
            if col > 3:  
                col = 0
                row += 1

        content_layout.addLayout(classes_grid)
        content_layout.addWidget(self.analysisGraphs)
        scroll_area.setWidget(content_widget)

        self.mainLayout.addWidget(scroll_area)
    
    def create_preview_card(self, title_text, min_w=200, min_h=150):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2e;
                border: 1px solid #3a3a3c;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        title = QLabel(title_text)
        title.setStyleSheet("color: #8e8e93; font-size: 11px; font-weight: bold; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scene = QGraphicsScene(frame)
        view = ZoomableGraphicsView(scene)
        view.setMinimumSize(min_w, min_h)
        view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        view.setStyleSheet("background: #1e1e1e; border: none;")

        layout.addWidget(title)
        layout.addWidget(view)

        return {"frame": frame, "scene": scene, "view": view}

    def load_data(self, path):
        percent_class_stat = self.model.data(self.model.index(0, 0), GET_STATISTICS)


        # TODO: move that to the backend...
        self.dataset_path = path
        imgs_dir = os.path.join(path, "imgs")
        labels_dir = os.path.join(path, "labels")
        config_path = os.path.join(path, "config.json")

        if not os.path.exists(imgs_dir):
            QMessageBox.warning(self, "Error", f"Folder 'imgs' doesn't exist in:\n{path}")
            return

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.class_names = json.load(f)

        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
        self.img_list = sorted([
            os.path.join(imgs_dir, f) for f in os.listdir(imgs_dir) 
            if f.lower().endswith(valid_extensions)
        ])

        if not self.img_list:
            QMessageBox.warning(self, "Warning", "No image found in 'imgs'.")
            return

        self.current_idx = 0
        self.display_current_image()

        print(percent_class_stat)

        self.analysisGraphs.radar.update_radar(percent_class_stat)
        self.analysisGraphs.radar.show()

    def display_current_image(self):
        if not self.img_list:
            return

        img_path = self.img_list[self.current_idx]
        current_path_obj = Path(img_path)
        labels_dir = os.path.join(self.dataset_path, "labels")
        label_path = os.path.join(labels_dir, current_path_obj.stem + ".png")

        raw_img = cv2.imread(img_path)
        if raw_img is None:
            return
        raw_img_rgb = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
        self.set_image_to_panel(self.preview_panels["raw"], raw_img_rgb)

        mask_np = np.zeros(raw_img.shape[:2], dtype=np.uint8)
        if os.path.exists(label_path):
            mask_np = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)

        overlay_mask = np.zeros_like(raw_img_rgb)
        
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 128, 0)
        ]

        for i in range(self.nb_classes):
            class_mask = ((mask_np & (1 << i)) > 0).astype(np.uint8) * 255
            
            if f"class_{i}" in self.preview_panels:
                class_rgb = cv2.cvtColor(class_mask, cv2.COLOR_GRAY2RGB)
                self.set_image_to_panel(self.preview_panels[f"class_{i}"], class_rgb)

            if i < len(colors):
                colored_part = np.zeros_like(raw_img_rgb)
                colored_part[class_mask > 0] = colors[i]
                overlay_mask = cv2.addWeighted(overlay_mask, 1.0, colored_part, 0.5, 0)

        final_overlay = cv2.addWeighted(raw_img_rgb, 0.7, overlay_mask, 0.3, 0)
        self.set_image_to_panel(self.preview_panels["overlay"], final_overlay)

    def set_image_to_panel(self, panel_dict, numpy_img):
        scene = panel_dict["scene"]
        scene.clear()

        h, w, ch = numpy_img.shape
        bytes_per_line = ch * w
        q_img = QImage(numpy_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        scene.addPixmap(pixmap)
        panel_dict["view"].fitInView(scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def next_image(self):
        if not self.img_list:
            return
        self.current_idx = (self.current_idx + 1) % len(self.img_list)
        self.display_current_image()

    def prev_image(self):
        if not self.img_list:
            return
        self.current_idx = (self.current_idx - 1) % len(self.img_list)
        self.display_current_image()
