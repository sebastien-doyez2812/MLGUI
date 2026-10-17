from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex


# Custom Roles:
LOAD_DATA_ROLE    = Qt.ItemDataRole.UserRole + 1
LOAD_CURRIMG_ROLE = Qt.ItemDataRole.UserRole + 2
NEXT_IMG_ROLE     = Qt.ItemDataRole.UserRole + 3
PREVIOUS_IMG_ROLE = Qt.ItemDataRole.UserRole + 4
GET_INDEX_ROLE    = Qt.ItemDataRole.UserRole + 5
GET_TOT_IMGS      = Qt.ItemDataRole.UserRole + 6
LOAD_AUG_DATASET  = Qt.ItemDataRole.UserRole + 7
GET_STATISTICS  = Qt.ItemDataRole.UserRole + 8