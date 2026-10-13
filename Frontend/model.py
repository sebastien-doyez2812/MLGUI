from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from roles import LOAD_DATA_ROLE, LOAD_CURRIMG_ROLE, NEXT_IMG_ROLE, PREVIOUS_IMG_ROLE

class GUIModel(QAbstractTableModel):
    def __init__(self, backend, parent = None):
        super().__init__(parent)
        self.backend = backend

    def data(self, index, role):
        if (int(role) == int(LOAD_DATA_ROLE)):
            return self.backend.getDatasetPath()
        elif (int(role) == int(LOAD_CURRIMG_ROLE)):
            return self.backend.get_current_img_path()
        
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

    