from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from Frontend.Widgets.histogramWidget import histogramWidget
from Frontend.Widgets.radarHistogramWidget import radarWidget

class AnalysisWidget(QWidget):
    def __init__(self, nb_classes=8, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.nb_classes = nb_classes
        self.parent = parent

        # For now, only 2 graphics:
        self.histogram = histogramWidget(nb_classes= self.nb_classes, parent=self)
        self.radar     = radarWidget(nb_classes= self.nb_classes, parent=self)

        self.mainLayout = QHBoxLayout(self)
        self._init_ui()
        self.hide_graphs()

    def _init_ui(self):
        self.mainLayout.addWidget(self.histogram)
        self.mainLayout.addWidget(self.radar)

    def hide_graphs(self):
        self.histogram.hide()
        self.radar.hide()

    def show_graphs(self):
        self.histogram.show()
        self.radar.show()

