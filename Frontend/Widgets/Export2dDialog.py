from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSpinBox, QPushButton, QFileDialog, QFrame

class DataAugmentationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export & Data Augmentation")
        self.setFixedWidth(360)
        self.output_dir = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        title = QLabel("Data Augmentation Configuration")
        main_layout.addWidget(title)

        self.browse_btn = QPushButton("📁 Select the output folder...")
       
        self.browse_btn.clicked.connect(self.select_folder)
        main_layout.addWidget(self.browse_btn)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(sep1)

        transform_group = QVBoxLayout()
        transform_group.setSpacing(10)
        
        transform_label = QLabel("Transformations (Augmentation)")
        transform_group.addWidget(transform_label)

        self.hflip_cb = QCheckBox("Horizontal Flip")
        self.vflip_cb = QCheckBox("Vertical Flip")
        self.rot_cb   = QCheckBox("Random Rotation / Zoom")
        self.elasticTransform = QCheckBox("Elastic Transform")
        self.gridTransform = QCheckBox("Grid Distortion")

        for cb in [self.hflip_cb, self.vflip_cb, self.rot_cb, self.elasticTransform, self.gridTransform]:
            transform_group.addWidget(cb)
            
        main_layout.addLayout(transform_group)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(sep2)

        count_layout = QHBoxLayout()
        count_label = QLabel("Image variations:")
        
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10)
        self.spin_count.setValue(1)
        self.spin_count.setFixedWidth(70)
        
        count_layout.addWidget(count_label)
        count_layout.addStretch()
        count_layout.addWidget(self.spin_count)
        main_layout.addLayout(count_layout)

        main_layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.cancel_btn = QPushButton("Cancel")

        self.export_action_btn = QPushButton("Export")
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.export_action_btn)
        main_layout.addLayout(btn_layout)

        self.export_action_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_settings(self):
        return {
            "hflip": self.hflip_cb.isChecked(),
            "vflip": self.vflip_cb.isChecked(),
            "rotation": self.rot_cb.isChecked(),
            "elastic": self.elasticTransform.isChecked(),
            "grid": self.gridTransform.isChecked(),
            "copies": self.spin_count.value()
        }

    def select_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if dir_path:
            self.output_dir = dir_path
            shortened_path = f"...{dir_path[-28:]}" if len(dir_path) > 28 else dir_path
            self.browse_btn.setText(f"📁 {shortened_path}")