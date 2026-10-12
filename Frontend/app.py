import sys
import importlib.util
import inspect
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projet PyQt Auto-découverte")
        self.resize(800, 600)
        
        # --- CORRECTION CRUCIALE POUR QMainWindow ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Nav bar:
        self.nav_layout = QHBoxLayout()
        main_layout.addLayout(self.nav_layout)
        
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)
        
        self._load_pages_from_folder("Frontend/pages")

    def _load_pages_from_folder(self, folder_pages = "Frontend/pages"):
        pages_dir = Path(folder_pages)
        pages_list = []

        if not pages_dir.exists():
            raise NameError(f"Folder {folder_pages} doesn't exist!")

        for file_path in pages_dir.glob("*py"):
            if file_path.name.startswith("__"):
                # ignore __init__.py
                continue 

            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__ and hasattr(obj, 'name'):
                    if not obj.__name__.endswith("Page"):
                        continue
                    page_name = obj.name
                    page_indx = obj.index_nav_bar
                    pages_list.append({"name": page_name, "idx": page_indx, "class":obj})
                    
        pages_list = sorted(pages_list, key=lambda x: x["idx"])

        for page_info in pages_list:
            page_instance = page_info["class"]()
            self.stacked_widget.addWidget(page_instance)
            
            btn = QPushButton(page_info["name"])
            btn.setStyleSheet("padding: 8px 16px; font-weight: bold;")
            
            btn.clicked.connect(lambda checked, p=page_instance: self.stacked_widget.setCurrentWidget(p))
            
            self.nav_layout.addWidget(btn)
            
        self.nav_layout.addStretch()

if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = MainWindow()
  window.show()
  sys.exit(app.exec())