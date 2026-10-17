import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np
import mplcursors

class radarWidget(QWidget):
    def __init__(self, nb_classes=8, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.nb_classes = nb_classes

        self.figure = None
        self.ax = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fig, self.ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
        self.fig.patch.set_facecolor('#2c2c2e')
        self.ax.set_facecolor('#1e1e1e')

        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)

        self.update_radar(np.zeros(self.nb_classes))

    def update_radar(self, proportions):
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')

        classes = [f"C{i}" for i in range(self.nb_classes)]
        proportions = list(proportions)
        max_val = max(proportions) if proportions and max(proportions) > 0 else 100.0
        
        angles = np.linspace(0, 2 * np.pi, self.nb_classes, endpoint=False).tolist()
        angles += angles[:1]
        proportions += proportions[:1]

        line,  = self.ax.plot(angles, proportions, color='#34C759', linewidth=2, linestyle='solid')
        self.ax.fill(angles, proportions, color='#34C759', alpha=0.25)

        tick_angles = np.linspace(0, 2 * np.pi, self.nb_classes, endpoint=False)
        self.ax.set_xticks(tick_angles)
        self.ax.set_xticklabels(classes, color='white', size=8)

        self.ax.set_ylim(0, max_val * 1.15)
        self.ax.set_title("Profil Global Dataset", color='white', fontsize=10, fontweight='bold', pad=15)
        self.ax.tick_params(colors='white', labelsize=8)

        self.ax.grid(color='#3a3a3c', linestyle='--', linewidth=0.5)
        self.ax.spines['polar'].set_color('#3a3a3c')

        self.fig.tight_layout()
        self.canvas.draw()
        cursor = mplcursors.cursor(line, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            index = int(round(sel.index))
            if index >= self.nb_classes:
                index = 0

            real_proportions = proportions[:-1] if len(proportions) > self.nb_classes else proportions
            val = real_proportions[index] if index < len(real_proportions) else sel.target[1]

            sel.annotation.set_text(f"Classe {index}: {val:.2f}%")
            sel.annotation.get_bbox_patch().set(fc="#2c2c2e", ec="#34C759", alpha=0.9)
            sel.annotation.set_color("white")