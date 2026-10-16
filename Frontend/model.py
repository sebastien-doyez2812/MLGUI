from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from roles import LOAD_DATA_ROLE, LOAD_CURRIMG_ROLE, NEXT_IMG_ROLE, PREVIOUS_IMG_ROLE, GET_INDEX_ROLE, GET_TOT_IMGS

class GUIModel(QAbstractTableModel):
    def __init__(self, backend, parent = None):
        super().__init__(parent)
        self.backend = backend

    def save_mask(self, mask):
        self.backend.save_mask(mask)

    def load_mask(self):
        return self.backend.load_mask()

    def export_dataset(self, settings, output_path, progress = None):
        print("in model.export_dataset")
        self.backend.exportDataset(settings, output_path, progress)

    def data(self, index, role):
        if (int(role) == int(LOAD_DATA_ROLE)):
            return self.backend.getDatasetPath()
        
        elif (int(role) == int(LOAD_CURRIMG_ROLE)):
            return self.backend.get_current_img_path()
        
        elif (int(role) == int(GET_INDEX_ROLE)):
            return self.backend.get_current_index()

        elif (int(role) == int(GET_TOT_IMGS)):
            return self.backend.get_len_dataset()
        
        else:
            return
        
    def setData(self, index, value, role = Qt.ItemDataRole.UserRole):
        if (int(role) == int(LOAD_DATA_ROLE)):
            self.backend.setDatasetPath(value)
            self.dataChanged.emit(index, index, [LOAD_CURRIMG_ROLE])
            return True
        elif (int(role) == int(NEXT_IMG_ROLE)):
            self.backend.next_image()
            self.dataChanged.emit(index, index, [LOAD_CURRIMG_ROLE])
            return True
        elif (int(role) == int(PREVIOUS_IMG_ROLE)):
            self.backend.previous_image() 
            self.dataChanged.emit(index, index, [LOAD_CURRIMG_ROLE])
            return True
        else:
            return
        
    def rowCount(self, parent = ...):
        return 0

    def columnCount(self, parent = ...):
        return 0

    