import typing

if typing.TYPE_CHECKING:
    from collections.abc import Callable

from typing import Any

import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QRect, Qt, QVariant, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QStyle, QStyleOptionButton, QTableView

from src.utils.config import AppConfig


class CheckableHeaderView(QHeaderView):
    """A custom header with a checkbox in the first section."""

    def __init__(self, orientation, parent=None) -> None:
        super().__init__(orientation, parent)
        self.isChecked = True  # Tracks if the checkbox is checked
        self.setSectionsClickable(True)  # Make the header sections clickable
        self.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def paintSection(self, painter, rect, logical_index):  # noqa: N802
        """Custom rendering of the section."""
        super().paintSection(painter, rect, logical_index)

        # Draw a checkbox only in the first section (index 0)
        if logical_index == 0:
            option = QStyleOptionButton()
            option.rect = QRect(3, rect.top() + 40, 20, 20)  # Position checkbox within header
            option.state = QStyle.StateFlag.State_Enabled | (QStyle.StateFlag.State_On if self.isChecked else QStyle.StateFlag.State_Off)

            # Use QStylePainter to draw the checkbox
            painter.save()
            painter.translate(rect.x(), rect.y())
            style = self.style()
            if style is not None:
                style.drawControl(QStyle.ControlElement.CE_CheckBox, option, painter)
            painter.restore()

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse click events to toggle the checkbox."""
        if event.button() == Qt.MouseButton.LeftButton and self.logicalIndexAt(event.pos()) == 0:
            self.isChecked = not self.isChecked
            self.updateSection(0)  # Update the header to reflect the checkbox state
            self.sectionClicked.emit(0)  # Emit signal when header is clicked
        super().mousePressEvent(event)


class CheckableTableView(QTableView):
    checked_updated = pyqtSignal(name="checkedUpdated_table")

    def __init__(self, parent=None, minimum_width: int = 0):
        super().__init__(parent)
        self.setMinimumWidth(minimum_width)
        font = self.font()
        font.setPointSize(AppConfig.FONT_SIZE)  # Increase font size
        self.setFont(font)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Set custom header view with checkbox
        self._horizontalHeader = CheckableHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self._horizontalHeader)

        # Connect header click to toggle checkboxes in the model
        self._horizontalHeader.sectionClicked.connect(self.toggle_all_checkboxes)

    def get_checked_mask(self) -> pd.Series:
        """Returns a mask of all the checked rows as a pandas boolean mask."""
        model = self.model()
        if model is not None and isinstance(model, PandasTableModel):
            return model.get_checked_mask()

        return pd.Series()

    def toggle_all_checkboxes(self, index):
        """Toggle all checkboxes in the model based on header checkbox state."""
        if index == 0:  # Only react if the checkbox header is clicked
            model = self.model()
            if model is not None and isinstance(model, PandasTableModel):
                all_checked = self._horizontalHeader.isChecked
                model.toggle_all_checkboxes(all_checked)

    def toggle_row(self, index):
        """Toggle the checkbox state of a single row."""
        model = self.model()
        if model is not None and isinstance(model, PandasTableModel):
            model.toggle_row(index)

    def set_table_model(self, dataframe: pd.DataFrame, index_name: str = "", column_widths: list[int | None] | None = None):
        """Set a new table model to the view."""
        if dataframe is None:
            return

        self.setModel(None)
        # Set the custom PandasTableModel
        model = PandasTableModel(dataframe, index_name)
        self.setModel(model)
        model.checkedUpdated = lambda: self.checked_updated.emit()

        # Configure header and column widths
        self._horizontalHeader.setMinimumSectionSize(1)
        self._horizontalHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 20)
        self._horizontalHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(2, len(dataframe.columns) + 2):
            if column_widths is not None and i - 2 < len(column_widths):
                width = column_widths[i - 2]
                if width is not None:
                    self._horizontalHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                    self.setColumnWidth(i, width)
                else:
                    self._horizontalHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                self._horizontalHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                self.setColumnWidth(i, 70)

        self._horizontalHeader.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self._horizontalHeader.setMinimumHeight(int(30 * 2))
        self._horizontalHeader.setMaximumSectionSize(250)
        self._horizontalHeader.setStyleSheet(
            "::section { background-color: #f0f0f0; border-width: 1px; border-style: solid; border-color: #b0b0b0 #b0b0b0 #b0b0b0 #f0f0f0; }"
            "::section::first { background-color: #f0f0f0; border-width: 1px; border-style: solid; border-color: #b0b0b0 #b0b0b0 #b0b0b0 #b0b0b0; }"
        )

        vertical_header = self.verticalHeader()
        if vertical_header is not None:
            vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)


class PandasTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame, index_name: str = "") -> None:
        super().__init__()
        self._dataframe = dataframe
        self._index_name = index_name
        self.checked_rows = [True] * len(self._dataframe)  # Track checkbox state for each row
        self.checkedUpdated: Callable[[], None] = lambda: None

    def rowCount(self, _=None):  # noqa: N802
        return len(self._dataframe.index)

    def columnCount(self, _=None):  # noqa: N802
        return len(self._dataframe.columns) + 2  # Extra column for the checkbox

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return Qt.CheckState.Checked if self.checked_rows[index.row()] else Qt.CheckState.Unchecked

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 1:
                value = self._dataframe.index[index.row()]
                return QVariant(str(value))

            if index.column() > 1:
                value = self._dataframe.iloc[index.row(), index.column() - 2]
                return QVariant(str(value))

        # Gray out text for unchecked rows
        if role == Qt.ItemDataRole.ForegroundRole and not self.checked_rows[index.row()]:
            return QBrush(QColor("gray"))

        return QVariant()

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole):  # noqa: N802
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.checked_rows[index.row()] = value != 0
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            self.layoutChanged.emit()
            self.checkedUpdated()
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setPointSize(AppConfig.FONT_SIZE)  # Increase font size
            return font

        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 1:
                return QVariant(self._index_name)
            if section > 1:
                return QVariant(self._dataframe.columns[section - 2])

        return QVariant()

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def toggle_all_checkboxes(self, check_state: bool):  # noqa: FBT001
        """Toggle the checkbox state of all rows."""
        self.checked_rows = [check_state] * len(self.checked_rows)
        self.checkedUpdated()
        self.layoutChanged.emit()

    def toggle_row(self, index: int):
        """Toggle the checkbox state of a single row."""
        self.checked_rows[index] = not self.checked_rows[index]
        if index < 0:
            index = len(self.checked_rows) + index
        self.dataChanged.emit(self.createIndex(index, 0), self.createIndex(index, 0), [Qt.ItemDataRole.CheckStateRole])
        self.checkedUpdated()
        self.layoutChanged.emit()

    def get_checked_mask(self) -> pd.Series:
        """Returns a mask of all the checked rows as a pandas boolean mask."""
        return pd.Series(self.checked_rows, index=self._dataframe.index)
