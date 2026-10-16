# from PyQt6.QtCore import Qt
# from PyQt6.QtWidgets import (
#     QFrame,
#     QGraphicsScene,
#     QGraphicsView,
#     QHBoxLayout,
#     QVBoxLayout,
#     QLabel,
#     QPushButton,
#     QSizePolicy,
#     QWidget,
# )
# from Frontend.Widgets.navigationWidget import NavigationWidget


# class DatasetViewerPage(QWidget):
#   name = "Viewer"
#   index_nav_bar = 2

#   def __init__(self, model_ref=None):
#     super().__init__()
    
#     self.model = model_ref  
#     self.init_ui()

#     self.mainLayout = QVBoxLayout(self)
    
#     self.navWidget = NavigationWidget()



#   def init_ui(self):
#     pass
    

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)
from Frontend.Widgets.navigationWidget import NavigationWidget


class DatasetViewerPage(QWidget):
    name = "Viewer"
    index_nav_bar = 2

    def __init__(self, model_ref=None):
        super().__init__()
        self.model = model_ref  
        
        # 1. Initialiser les layouts et widgets principaux d'abord
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        self.navWidget = NavigationWidget()
        
        # 2. Construire l'interface visuelle
        self.init_ui()

    def init_ui(self):
        # Titre de la page
        title = QLabel("Analyse et Visualisation du Dataset")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: #ffffff;")
        self.mainLayout.addWidget(title)

        # Grille pour les 10 emplacements (1 Raw + 8 Classes + 1 Overlay)
        # On peut organiser ça sur 2 ou 3 colonnes par exemple
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Dictionnaire ou liste pour stocker nos labels/conteneurs d'images
        self.preview_panels = {}

        # --- 1. Image Brute (Raw Image) ---
        raw_card = self.create_preview_card("Image Brute (Raw)")
        grid_layout.addWidget(raw_card["frame"], 0, 0, 2, 2) # Prend un peu plus de place
        self.preview_panels["raw"] = raw_card["label"]

        # --- 2. Overlay Final ---
        overlay_card = self.create_preview_card("Overlay Final")
        grid_layout.addWidget(overlay_card["frame"], 0, 2, 2, 2)
        self.preview_panels["overlay"] = overlay_card["label"]

        # --- 3. Les 8 Masques de classes (Class 0 à 7) ---
        # On les dispose par exemple sur les lignes suivantes
        row, col = 2, 0
        for i in range(8):
            class_card = self.create_preview_card(f"Classe {i}")
            grid_layout.addWidget(class_card["frame"], row, col)
            self.preview_panels[f"class_{i}"] = class_card["label"]
            
            col += 1
            if col > 3: # 4 éléments par ligne pour les classes
                col = 0
                row += 1

        self.mainLayout.addLayout(grid_layout)

        # Ajout du widget de navigation en bas
        self.mainLayout.addWidget(self.navWidget)

    def create_preview_card(self, title_text):
        """Helper pour créer un conteneur propre (carte) avec un titre et un cadre pour l'image"""
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
        
        img_label = QLabel("Aucune image")
        img_label.setStyleSheet("color: #545456; font-size: 10px; border: none; background: #1e1e1e;")
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setMinimumSize(120, 100)
        img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(title)
        layout.addWidget(img_label)

        return {"frame": frame, "label": img_label}