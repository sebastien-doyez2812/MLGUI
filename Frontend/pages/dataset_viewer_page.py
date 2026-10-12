from PyQt6.QtCore import Qt
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
)


class DatasetViewerPage(QWidget):
  name = "Viewer"
  index_nav_bar = 3

  def __init__(self, model_ref=None):
    super().__init__()
    # self.name = name
    self.model = model_ref  
    self.init_ui()

  def init_ui(self):
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    top_bar = QFrame()
    top_bar.setObjectName("TopBar")
    top_bar.setFixedHeight(60)
    top_bar.setStyleSheet(
        "background-color: #2b2b2b; color: white; border-bottom: 1px solid"
        " #3f3f3f;"
    )

    top_layout = QHBoxLayout(top_bar)
    top_layout.setContentsMargins(15, 0, 15, 0)

    title_label = QLabel("Dataview 2D")
    title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

    btn_open = QPushButton("Ouvrir Image")
    btn_save = QPushButton("Sauvegarder")
    for btn in [btn_open, btn_save]:
      btn.setStyleSheet(
          "background-color: #3c3c3c; color: white; border: none; padding:"
          " 6px 12px; border-radius: 4px;"
      )

    top_layout.addWidget(title_label)
    top_layout.addStretch()
    top_layout.addWidget(btn_open)
    top_layout.addWidget(btn_save)

    main_layout.addWidget(top_bar)

    center_container = QWidget()
    center_layout = QHBoxLayout(center_container)
    center_layout.setContentsMargins(0, 0, 0, 0)
    center_layout.setSpacing(0)

    menu_bar = QFrame()
    menu_bar.setObjectName("MenuLeft")
    menu_bar.setFixedWidth(220)
    menu_bar.setStyleSheet(
        "background-color: #323232; color: white; border-right: 1px solid"
        " #3f3f3f;"
    )

    menu_layout = QVBoxLayout(menu_bar)
    menu_layout.setContentsMargins(10, 15, 10, 15)
    menu_layout.setSpacing(10)

    menu_title = QLabel("Outils de Segmentation")
    menu_title.setStyleSheet("font-weight: bold; color: #b0b0b0;")

    btn_brush = QPushButton("Pinceau")
    btn_eraser = QPushButton("Gomme")
    btn_polygon = QPushButton("Polygone")
    btn_threshold = QPushButton("Seuillage")
    btn_AI = QPushButton()

    for btn in [btn_brush, btn_eraser, btn_polygon, btn_threshold]:
      btn.setStyleSheet(
          "background-color: #3f3f3f; color: white; border: none; padding:"
          " 8px; border-radius: 4px; text-align: left;"
      )
      menu_layout.addWidget(btn)

    menu_layout.addStretch()  # Pousse les éléments vers le haut

    center_layout.addWidget(menu_bar)

    # ==========================================
    # 3. GRANDE ZONE DE GAUCHE/CENTRE (SCÈNE)
    # ==========================================
    # Utilisation d'un QGraphicsView / QGraphicsScene, idéal pour afficher
    # et manipuler des images, zoomer, placer des masques, etc.
    self.graphics_scene = QGraphicsScene(self)
    self.graphics_view = QGraphicsView(self.graphics_scene)
    self.graphics_view.setStyleSheet(
        "background-color: #1e1e1e; border: none;"
    )
    self.graphics_view.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
    )

    # Optionnel : Texte indicatif dans la scène vide
    placeholder_text = self.graphics_scene.addText(
        "Glissez ou ouvrez une image pour commencer l'étiquetage"
    )
    placeholder_text.setDefaultTextColor(Qt.GlobalColor.gray)

    center_layout.addWidget(self.graphics_view)

    main_layout.addWidget(center_container)