import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt6.QtGui import QFont

from src.utils.config import AppConfig


class PandasTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, index_name: str = "") -> None:
        super().__init__()
        self._dataframe = dataframe
        self._index_name = index_name

    def rowCount(self, _=None):  # noqa: N802
        return len(self._dataframe.index)

    def columnCount(self, _=None):  # noqa: N802
        return len(self._dataframe.columns) + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        if index.column() == 0 and role == Qt.ItemDataRole.DisplayRole:
            value = self._dataframe.index[index.row()]
            return QVariant(str(value))

        if role in [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]:
            value = self._dataframe.iloc[index.row(), index.column() - 1]
            return QVariant(str(value))

        return QVariant()

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):  # noqa: N802
        if role == Qt.ItemDataRole.EditRole:
            self._dataframe.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setPointSize(AppConfig.FONT_SIZE)  # Increase font size
            return font

        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return QVariant(self._index_name)
            return QVariant(self._dataframe.columns[section - 1])

        return QVariant()

    def flags(self, _):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
