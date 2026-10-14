from PyQt6.QtCore import Qt, QModelIndex, QRectF, QPointF, QPoint
from PyQt6.QtGui import QPixmap, QImage, QWheelEvent, QMouseEvent, QPainter, QPen, QColor
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
    QSlider,
    QMessageBox
)
from pathlib import Path
import os
from PIL import Image, ImageEnhance, ImageDraw
from Frontend.Widgets.navigationWidget import NavigationWidget
from Frontend.Widgets.classSelectorWidget import ClassSelector
from Frontend.roles import *

class Segmentation2DPage(QWidget):
    name = "Segmentation2D"
    index_nav_bar = 1

    def __init__(self, model_ref=None):
        super().__init__()
        self.model = model_ref  
        self.current_img_path = None  
        self.original_pil_img = None
        self.masks = {}  

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.menu_container = QFrame()
        self.menu_container.setObjectName("SidebarMenu")
        self.menu_container.setFixedWidth(260)
        
        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(15)

        self.open_folder_btn = QPushButton("Open Folder")
        self.export_btn = QPushButton("Export")
        self.navigation_widget = NavigationWidget()

        for btn in [self.open_folder_btn, self.export_btn]:
            btn.setStyleSheet("padding: 6px 12px; font-weight: bold;")

        self.bit_selector = ClassSelector(num_bits=8, name_bits=["class0", "class1", "class2", "class3", "class4", "class5", "class6", "class7"])
        
        self.bit_selector.checkbox.stateChanged.connect(self.update_image_display)
        for btn in self.bit_selector.class_buttons:
            btn.clicked.connect(self.update_image_display)


        # size of the pen:
        self.size_pen_layout = QHBoxLayout()
        self.size_pen_layout.setContentsMargins(0, 0, 0, 0)

        self.size_label = QLabel("Size of the pen:")
        self.size_val_label = QLabel("5")
        self.size_val_label.setStyleSheet("color: #8e8e93; background: transparent;")

        self.size_pen_layout.addWidget(self.size_label)
        self.size_pen_layout.addStretch()
        self.size_pen_layout.addWidget(self.size_val_label)

        self.size_cursor = QSlider(Qt.Orientation.Horizontal)
        self.size_cursor.setRange(2, 25)
        self.size_cursor.setValue(5)
        self.size_cursor.valueChanged.connect(lambda v: self.size_val_label.setText(str(v)))
        
        # Contrast:
        self.contrast_header_layout = QHBoxLayout()
        self.contrast_header_layout.setContentsMargins(0, 0, 0, 0)

        self.contrast_label = QLabel("Contrast")
        self.contrast_val_label = QLabel("50")
        self.contrast_val_label.setStyleSheet("color: #8e8e93; background: transparent;")

        self.contrast_header_layout.addWidget(self.contrast_label)
        self.contrast_header_layout.addStretch()
        self.contrast_header_layout.addWidget(self.contrast_val_label)

        self.contrast_cursor = QSlider(Qt.Orientation.Horizontal)
        self.contrast_cursor.setRange(0, 100)
        self.contrast_cursor.setValue(50)
        self.contrast_cursor.valueChanged.connect(lambda v: self.contrast_val_label.setText(str(v)))
        self.contrast_cursor.valueChanged.connect(self.update_image_display)

        # Luminosity:
        self.lum_header_layout = QHBoxLayout()
        self.lum_header_layout.setContentsMargins(0, 0, 0, 0)

        self.lum_label = QLabel("Luminosity")
        self.lum_val_label = QLabel("50")
        self.lum_val_label.setStyleSheet("color: #8e8e93; background: transparent;")

        self.lum_header_layout.addWidget(self.lum_label)
        self.lum_header_layout.addStretch()
        self.lum_header_layout.addWidget(self.lum_val_label)

        self.lum_cursor = QSlider(Qt.Orientation.Horizontal)
        self.lum_cursor.setRange(0, 100)
        self.lum_cursor.setValue(50)
        self.lum_cursor.valueChanged.connect(lambda v: self.lum_val_label.setText(str(v)))
        self.lum_cursor.valueChanged.connect(self.update_image_display)

        self.image_scene = QGraphicsScene(self)
        
        self.image_viewer = InteractiveGraphicsView(self.image_scene, self)
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

                    if img_path is None:
                        error_box = QMessageBox(self)
                        error_box.setIcon(QMessageBox.Icon.Critical)
                        error_box.setWindowTitle("Folder error")
                        error_box.setText("No image available in the subfolder 'imgs'...")
                        error_box.setInformativeText("Please select a proper dataset folder with subfolder 'img/' ('labels/' is optional.).")
                        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                        error_box.exec()

                    if img_path: 
                        self.current_img_path = str(img_path)
                        self.load_image_and_masks()

                case _:
                    return

    def load_image_and_masks(self):
        if not self.current_img_path or not os.path.exists(self.current_img_path):
            return
        try:
            self.original_pil_img = Image.open(self.current_img_path).convert("RGBA")
            w, h = self.original_pil_img.size
            self.masks = {i: Image.new("RGBA", (w, h), (0, 0, 0, 0)) for i in range(self.bit_selector.num_bits)}
            self.update_image_display()
        except Exception as e:
            print(f"Error during loading: {e}")

    def update_image_display(self):
        if self.original_pil_img is None:
            return

        try:
            working_img = self.original_pil_img.copy()

            lum_factor = self.lum_cursor.value() / 50.0
            working_img = ImageEnhance.Brightness(working_img).enhance(lum_factor)

            contrast_factor = self.contrast_cursor.value() / 50.0
            working_img = ImageEnhance.Contrast(working_img).enhance(contrast_factor)

            show_all = self.bit_selector.checkbox.isChecked()
            active_idx = self.bit_selector.active_bit_index

            for idx, mask in self.masks.items():
                if show_all or idx == active_idx:
                    alpha_factor = 0.6 
                    
                    r, g, b, a = mask.split()
                    a_adjusted = a.point(lambda p: int(p * alpha_factor))
                    semi_transparent_mask = Image.merge("RGBA", (r, g, b, a_adjusted))
                    
                    working_img = Image.alpha_composite(working_img, semi_transparent_mask)

            data = working_img.tobytes("raw", "RGBA")
            qimage = QImage(data, working_img.width, working_img.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)

            self.image_scene.clear()
            self.image_scene.addPixmap(pixmap)
            self.image_viewer.setSceneRect(QRectF(pixmap.rect()))

        except Exception as e:
            print(f"Error during the update: {e}")

    def paint_on_active_mask(self, p1, p2):
        if not self.original_pil_img:
            return

        active_idx = self.bit_selector.active_bit_index
        if active_idx not in self.masks:
            return

        w, h = self.original_pil_img.size
        if not (0 <= p1.x() < w and 0 <= p1.y() < h and 0 <= p2.x() < w and 0 <= p2.y() < h):
            return

        hex_color = self.bit_selector.colors[active_idx % len(self.bit_selector.colors)]
        qcolor = QColor(hex_color)
        pil_color = (qcolor.red(), qcolor.green(), qcolor.blue(), 255)

        draw = ImageDraw.Draw(self.masks[active_idx])
        draw.line([p1.x(), p1.y(), p2.x(), p2.y()], fill=pil_color, width=int(self.size_cursor.value()), joint="curve")
        
        self.update_image_display()

    def init_ui(self):
        open_and_export = QHBoxLayout()
        open_and_export.addWidget(self.open_folder_btn)
        open_and_export.addWidget(self.export_btn)
        self.menu_layout.addLayout(open_and_export)
        
        self.menu_layout.addWidget(self.navigation_widget)   
        
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.addWidget(self.bit_selector)
        controls_layout.addSpacing(15)

        separator = QFrame()
        separator.setObjectName("SeparatorLine")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        controls_layout.addLayout(self.size_pen_layout)
        controls_layout.addWidget(self.size_cursor)
        
        controls_layout.addSpacing(5)
        controls_layout.addWidget(separator)
        controls_layout.addSpacing(5)

        controls_layout.addLayout(self.contrast_header_layout)
        controls_layout.addWidget(self.contrast_cursor)

        controls_layout.addSpacing(10)

        controls_layout.addLayout(self.lum_header_layout)
        controls_layout.addWidget(self.lum_cursor)

        self.menu_layout.addLayout(controls_layout)
        self.menu_layout.addStretch()
        self.main_layout.addWidget(self.menu_container, stretch=0)

        self.main_layout.addWidget(self.image_viewer, stretch=1)

    def next_img(self):
        if self.model is not None:
            self.model.setData(self.model.index(0, 0), None, int(NEXT_IMG_ROLE))

    def previous_img(self):
        if self.model is not None:
            self.model.setData(self.model.index(0, 0), None, int(PREVIOUS_IMG_ROLE))

    def open_folder_dialog(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if dir_path:
            img_path = os.path.join(dir_path, "imgs")
            if not os.path.exists(img_path) :
                error_box = QMessageBox(self)
                error_box.setIcon(QMessageBox.Icon.Critical)
                error_box.setWindowTitle("Folder error")
                error_box.setText("The folder you selected doesn't contain a subfolder 'imgs'...")
                error_box.setInformativeText("Please select a proper dataset folder with subfolder 'img/' ('labels/' is optional.).")
                error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_box.exec()
            else:
                labels_path = os.path.join(dir_path, "labels")
                if not os.path.exists(labels_path):
                    os.makedirs(labels_path, exist_ok=True)
                if self.model is not None:
                    self.model.setData(self.model.index(0, 0), dir_path, int(LOAD_DATA_ROLE))


class InteractiveGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._is_dragging = False
        self._is_drawing = False
        self._drag_start_position = QPointF()
        self._last_mouse_pos = QPointF()

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self._is_dragging = True
            self._drag_start_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.MiddleButton or event.button() == Qt.MouseButton.RightButton:
            self._is_dragging = True
            self._drag_start_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            
        elif event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = True
            scene_pos = self.mapToScene(event.pos())
            self._last_mouse_pos = scene_pos
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            delta = event.position() - self._drag_start_position
            self._drag_start_position = event.position()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta.x()))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta.y()))
            event.accept()
        elif self._is_drawing:
            current_scene_pos = self.mapToScene(event.pos())
            
            page = self.parent()
            if hasattr(page, "paint_on_active_mask"):
                page.paint_on_active_mask(self._last_mouse_pos, current_scene_pos)

            self._last_mouse_pos = current_scene_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_dragging and (event.button() in [Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton]):
            self._is_dragging = False
            self.unsetCursor()
            event.accept()
        elif self._is_drawing and event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)