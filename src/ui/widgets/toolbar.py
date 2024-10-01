from PyQt6.QtCore import QModelIndex, QSize, Qt
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel
from PyQt6.QtWidgets import QComboBox, QLabel, QSizePolicy, QToolBar, QWidget

from src.ui.widgets.multiselect_combobox import CustomMultiSelectComboBox


class ToolBar(QToolBar):
    def __init__(
        self,
        parent,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        style: Qt.ToolButtonStyle = Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        icon_size: tuple[int, int] = (32, 32),
        font_size: int = 12,
    ) -> None:
        super().__init__(parent)
        self.actions_call: dict[str, QAction] = {}
        self.setOrientation(orientation)
        self.setToolButtonStyle(style)
        self.setIconSize(QSize(icon_size[0], icon_size[1]))

        self.font_size = font_size
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

    def add_button(self, text: str, icon: str, trigger_action) -> None:
        self.actions_call[text] = QAction(QIcon(icon), text, self)
        self.actions_call[text].triggered.connect(trigger_action)
        self.addAction(self.actions_call[text])

    def add_separator(self) -> None:
        separator = QWidget(self)
        separator.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(separator)

    def add_fixed_separator(self, size: int) -> None:
        separator = QWidget(self)
        separator.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        separator.setMinimumWidth(size)
        self.addWidget(separator)

    def add_label(self, text: str) -> None:
        label = QLabel(text, self)
        font = label.font()
        font.setPointSize(self.font_size)
        label.setFont(font)
        self.addWidget(label)

    def add_option_list(self, label: str, options: list[str], on_change) -> None:
        combo_box = QComboBox(self)
        combo_box.addItems(options)
        combo_box.currentIndexChanged.connect(on_change)  # Connect change event

        self.add_label(label)
        self.add_fixed_separator(10)
        self.addWidget(combo_box)  # Add the combo box to the toolbar

    def add_multiselect_option_list(self, label: str, options: list[str], on_change) -> None:
        combo_box = CustomMultiSelectComboBox(self)
        combo_box.addItems(options)
        combo_box.setCurrentIndexes(list(range(len(options))))

        def model() -> QStandardItemModel:
            return combo_box.model()

        selecting = False

        def on_data_changed(x: QModelIndex):
            nonlocal selecting
            changed = True
            item_0 = model().item(0)
            if item_0 is None:
                return
            if x.row() == 0:
                selecting = True
                if item_0.checkState() == Qt.CheckState.Checked:
                    if len(combo_box.getCurrentIndexes()) == len(options):
                        changed = False
                    combo_box.setCurrentIndexes(list(range(len(options))))
                else:
                    if len(combo_box.getCurrentIndexes()) == 0:
                        changed = False
                    combo_box.setCurrentIndexes([])
                selecting = False
            if not selecting and changed:
                data_list = combo_box.currentData()
                if "(все)" in data_list:
                    data_list.remove("(все)")
                on_change(data_list)
            if all(combo_box.checked_mask()) and item_0.checkState() != Qt.CheckState.Checked:
                selecting = True
                item_0.setCheckState(Qt.CheckState.Checked)
                selecting = False
            elif not any(combo_box.checked_mask()) and item_0.checkState() != Qt.CheckState.Unchecked:
                selecting = True
                item_0.setCheckState(Qt.CheckState.Unchecked)
                selecting = False

        model().dataChanged.connect(on_data_changed)  # Connect change event

        self.add_label(label)
        self.add_fixed_separator(10)
        self.addWidget(combo_box)  # Add the combo box to the toolbar
