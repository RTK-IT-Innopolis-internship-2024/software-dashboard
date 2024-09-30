from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QLabel, QSizePolicy, QToolBar, QWidget


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
