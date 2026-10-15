from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QPainter, QPen, QColor
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsLineItem
)
from Frontend.roles import *



class InteractiveGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._is_dragging     = False
        self._is_drawing      = False
        self._is_erasing      = False
        self._is_line_drawing = False
        self._is_l_pressed    = False

        self._drag_start_position = QPointF()
        self._last_mouse_pos      = QPointF()
        self._line_start_pos      = QPointF()
        self._preview_line_item   = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_L:
            self._is_l_pressed = True
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_L:
            self._is_l_pressed = False
            event.accept()
        else:
            super().keyReleaseEvent(event)  

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent):
        self.setFocus()
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self._is_dragging = True
            self._drag_start_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._is_dragging = True
            self._drag_start_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

        elif event.button() == Qt.MouseButton.LeftButton and self._is_l_pressed:
            self._is_line_drawing = True
            self._line_start_pos = scene_pos

            pen = QPen(QColor(255, 0, 0, 200), 2, Qt.PenStyle.DashLine)
            self._preview_line_item = QGraphicsLineItem(scene_pos.x(), scene_pos.y(), scene_pos.x(), scene_pos.y())
            self._preview_line_item.setPen(pen)
            self.scene().addItem(self._preview_line_item)

            event.accept()
        
        elif event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = True
            self._last_mouse_pos = scene_pos
            event.accept()

        elif event.button() == Qt.MouseButton.RightButton:
            self._is_erasing = True
            self._last_mouse_pos = self.mapToScene(event.pos())
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

        elif self._is_line_drawing:
            current_scene_pos = self.mapToScene(event.pos())
            self._preview_line_item.setLine(
                self._line_start_pos.x(), self._line_start_pos.y(),
                current_scene_pos.x(), current_scene_pos.y()
            )
            event.accept()

        elif self._is_drawing:
            current_scene_pos = self.mapToScene(event.pos())
            
            page = self.parent()
            if hasattr(page, "paint_on_active_mask"):
                page.paint_on_active_mask(self._last_mouse_pos, current_scene_pos)

            self._last_mouse_pos = current_scene_pos
            event.accept()

        elif self._is_erasing:
            current_scene_pos = self.mapToScene(event.pos())
            page = self.parent()
            if hasattr(page, "erase_on_active_mask"):
                page.erase_on_active_mask(self._last_mouse_pos, current_scene_pos)

            self._last_mouse_pos = current_scene_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            page = self.parent()
            if hasattr(page, "flood_fill_active_mask"):
                page.flood_fill_active_mask(scene_pos)
            event.accept()

        elif event.button() == Qt.MouseButton.RightButton:
            scene_pos = self.mapToScene(event.pos())
            page = self.parent()
            if hasattr(page, "flood_erase_active_mask"):
                page.flood_erase_active_mask(scene_pos)
            event.accept()

        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_dragging and (event.button() in [Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton]):
            self._is_dragging = False
            self.unsetCursor()
            event.accept()

        elif self._is_line_drawing and event.button() == Qt.MouseButton.LeftButton:
            self._is_line_drawing = False
            current_scene_pos = self.mapToScene(event.pos())
            
            if self._preview_line_item:
                self.scene().removeItem(self._preview_line_item)
                self._preview_line_item = None
            
            page = self.parent()
            if hasattr(page, "draw_straight_line_on_active_mask"):
                page.draw_straight_line_on_active_mask(self._line_start_pos, current_scene_pos)
            event.accept()

        elif self._is_drawing and event.button() == Qt.MouseButton.LeftButton:
            self._is_drawing = False
            event.accept()
        elif self._is_erasing and event.button() == Qt.MouseButton.RightButton:
            self._is_erasing = False
            event.accept()

        else:
            super().mouseReleaseEvent(event)