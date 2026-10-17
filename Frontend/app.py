import sys, os
import importlib.util
from model import GUIModel
import inspect
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Backend.backend import Backend


class MainWindow(QMainWindow):
    def __init__(self, backend, model):
        super().__init__()
        self.setWindowTitle("OpenMLGUI")
        self.resize(800, 600)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.backend = backend
        self.model = model

        # Nav bar:
        self.nav_layout = QHBoxLayout()
        main_layout.addLayout(self.nav_layout)
        self.nav_buttons = []

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
            page_instance = page_info["class"](self.model)
            self.stacked_widget.addWidget(page_instance)
            
            btn = QPushButton(page_info["name"])
            self.nav_buttons.append(btn)
            btn.clicked.connect(lambda checked, p=page_instance, b=btn: self.on_nav_button_clicked(p, b))
            
            self.nav_layout.addWidget(btn)
            
        self.nav_layout.addStretch()
        if self.nav_buttons and self.stacked_widget.count() > 0:
            self.on_nav_button_clicked(self.stacked_widget.widget(0), self.nav_buttons[0])

    def on_nav_button_clicked(self, page_instance, clicked_button):
        self.stacked_widget.setCurrentWidget(page_instance)
        for btn in self.nav_buttons:
            if btn == clicked_button:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2e7d32;
                        color: white;
                        padding: 8px 16px;
                        font-weight: bold;
                        border-radius: 4px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3c3c3c;
                        color: white;
                        padding: 8px 16px;
                        font-weight: bold;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #4c4c4c;
                    }
                """)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    backend = Backend()
    model = GUIModel(backend= backend, parent= app)

    style_path = Path(__file__).resolve().parent / "style.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Error : No QSS file at {style_path}")
    window = MainWindow(backend=backend, model= model)
    window.showMaximized()
    sys.exit(app.exec())