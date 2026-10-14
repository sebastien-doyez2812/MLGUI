from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, 
    QPushButton, 
    QCheckBox, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout, 
    QInputDialog
)

class EditableButton(QPushButton):
    """Un bouton personnalisé qui détecte le double-clic pour lancer le renommage."""
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class ClassSelector(QWidget):
    def __init__(self, num_bits=1, name_bits=None):
        super().__init__()
        
        if name_bits is None:
            name_bits = [f"class{i}" for i in range(num_bits)]

        assert len(name_bits) == num_bits, f"name_bits should contain {num_bits} elements!"

        self.num_bits = num_bits
        self.name_bits = name_bits

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Création et ajout des boutons interactifs
        self.class_buttons = []
        for idx in range(self.num_bits):
            btn = EditableButton(self.name_bits[idx])
            # On connecte le double-clic du bouton à la fonction de renommage
            btn.doubleClicked.connect(lambda checked=False, i=idx: self.prompt_rename_bit(i))
            
            self.class_buttons.append(btn)
            self.main_layout.addWidget(btn)

        # Checkbox "Show All"
        self.checkbox = QCheckBox()
        self.show_all_label = QLabel("Show All")

        show_all_layout = QHBoxLayout()
        show_all_layout.addWidget(self.checkbox)
        show_all_layout.addWidget(self.show_all_label)
        show_all_layout.addStretch()

        self.main_layout.addLayout(show_all_layout)

    def prompt_rename_bit(self, index):
        """Ouvre une boîte de dialogue pour saisir le nouveau nom du bit."""
        current_name = self.name_bits[index]
        new_name, ok = QInputDialog.getText(
            self, 
            "Renommer la classe", 
            f"Entrez le nouveau nom pour '{current_name}' :", 
            text=current_name
        )
        
        # Si l'utilisateur clique sur OK et que le champ n'est pas vide
        if ok and new_name.strip():
            self.rename_bit(index, new_name.strip())

    def rename_bit(self, index, new_name):
        """Met à jour le nom dans la liste interne et sur le bouton."""
        if 0 <= index < self.num_bits:
            self.name_bits[index] = new_name
            self.class_buttons[index].setText(new_name)