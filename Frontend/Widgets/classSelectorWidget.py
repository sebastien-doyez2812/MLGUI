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
import os, json

class EditableButton(QPushButton):
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class ClassSelector(QWidget):
    bitSelected = pyqtSignal(int)

    def __init__(self, parent, num_bits=8, name_bits=None):
        super().__init__()
        self.parent = parent
        if name_bits is None:
            name_bits = [f"class{i}" for i in range(num_bits)]

        assert len(name_bits) == num_bits, f"name_bits should contain {num_bits} elements!"

        self.num_bits = num_bits
        self.name_bits = name_bits
        self.active_bit_index = 0  
        self.colors = [
            "#FF3B30",  
            "#FF9500",  
            "#FFCC00",  
            "#34C759",  
            "#00C7BE",   
            "#007AFF",  
            "#5856D6",  
            "#AF52DE"    
        ]

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)

        self.class_buttons = []
        for idx in range(self.num_bits):
            btn = EditableButton(self.name_bits[idx])
            btn.doubleClicked.connect(lambda checked=False, i=idx: self.prompt_rename_bit(i))
            btn.clicked.connect(lambda checked=False, i=idx: self.set_active_bit(i))
            
            self.class_buttons.append(btn)
            self.main_layout.addWidget(btn)

        self.checkbox = QCheckBox()
        self.show_all_label = QLabel("Show All")
        self.show_all_label.setStyleSheet("background: transparent; color: #aeaeb2;")
        
        self.checkbox.stateChanged.connect(self.update_buttons_style)

        show_all_layout = QHBoxLayout()
        show_all_layout.addWidget(self.checkbox)
        show_all_layout.addWidget(self.show_all_label)
        show_all_layout.addStretch()

        self.main_layout.addSpacing(6)
        self.main_layout.addLayout(show_all_layout)

        self.update_buttons_style()

    def set_active_bit(self, index):
        self.num_bits 
        if 0 <= index < self.num_bits:
            self.active_bit_index = index
            self.update_buttons_style()
            self.bitSelected.emit(index)

    def update_buttons_name(self, names = None):
        assert len(names) == len(self.class_buttons), "Number of names don't match the real number of classes!"
        for idx, current_btn in enumerate(self.class_buttons):
            current_btn.setText(names[idx])

    def update_buttons_style(self):
        show_all = self.checkbox.isChecked()

        for idx, btn in enumerate(self.class_buttons):
            color = self.colors[idx % len(self.colors)]
            is_active = (idx == self.active_bit_index)
            
            if show_all:
                if is_active:
                    # Style en mode "Show All" mais POUR LA CLASSE ACTIVE : bordure blanche épaisse et prononcée
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            color: #ffffff;
                            border: 3px solid #ffffff;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: 800;
                        }}
                    """)
                else:
                    # Style en mode "Show All" pour les autres classes (couleur pleine, mais bordure discrète)
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            color: rgba(255, 255, 255, 0.7);
                            border: 1px solid rgba(255, 255, 255, 0.2);
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: 500;
                        }}
                    """)
            else:
                if is_active:
                    # Style normal quand "Show All" est décoché (classe active)
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {color};
                            color: #ffffff;
                            border: 2px solid #ffffff;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: 700;
                        }}
                    """)
                else:
                    # Style normal pour les classes inactives
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2c2c2e;
                            color: #8e8e93;
                            border: 1px solid rgba(255, 255, 255, 0.05);
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-weight: 500;
                        }
                        QPushButton:hover {
                            background-color: #3a3a3c;
                            color: #f5f5f7;
                        }
                    """)
    def prompt_rename_bit(self, index):
        current_name = self.name_bits[index]
        new_name, ok = QInputDialog.getText(
            self, 
            "Rename the class", 
            f"New name for '{current_name}' :", 
            text=current_name
        )
        if os.path.exists(self.parent.config_path):
            self.name_bits[index] = new_name
            config_names = {
                            "class0": self.name_bits[0],
                            "class1": self.name_bits[1],
                            "class2": self.name_bits[2],
                            "class3": self.name_bits[3],
                            "class4": self.name_bits[4],
                            "class5": self.name_bits[5],
                            "class6": self.name_bits[6],
                            "class7": self.name_bits[7]
                        }
            with open(self.parent.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_names, f, indent=4, ensure_ascii=False)
        else:
            print(f"[-] Error in ClassSelector: no config path at {self.parent.config_path}")
        
        if ok and new_name.strip():
            self.rename_bit(index, new_name.strip())

    def rename_bit(self, index, new_name):
        if 0 <= index < self.num_bits:
            self.name_bits[index] = new_name
            self.class_buttons[index].setText(new_name)