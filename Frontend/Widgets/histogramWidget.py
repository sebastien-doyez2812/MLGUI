import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class histogramWidget(QWidget):
    def __init__(self, nb_classes = 8, parent = None):
        super().__init__(parent=parent)
        self.parent = parent
        self.nb_classes = nb_classes
        self.fig = None
        self.ax = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.fig.patch.set_facecolor('#2c2c2e')
        self.ax.set_facecolor('#1e1e1e')

        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)
        
        self.update_histogram(np.zeros(self.nb_classes))

    def update_histogram(self, pixel_counts):
        print(f"in update histo: {pixel_counts}")
        assert len(pixel_counts) == self.nb_classes, "We should have len(pixel_counts) == self.nb_classes"
        
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        classes = [f"C{i}" for i in range(self.nb_classes)]
        colors = [
            '#ff4d4d', '#2ecc71', '#3498db', '#f1c40f',
            '#9b59b6', '#1abc9c', '#e67e22', '#e84393'
        ]
        bars = self.ax.bar(classes, pixel_counts, color=colors[:len(classes)])
        
        self.ax.set_title("Pixels per class (current image)", color='white', fontsize=10, fontweight='bold')
        self.ax.tick_params(colors='white', labelsize=8)
        self.ax.grid(axis='y', linestyle='--', alpha=0.2)
        for spine in self.ax.spines.values():
            spine.set_color('#3a3a3c')

        self.fig.tight_layout()
        self.canvas.draw()