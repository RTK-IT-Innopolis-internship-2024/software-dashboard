import re
from typing import Any

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.utils import utils
from src.utils.config import AppConfig, ConfigParam, ParamEditWidget


class ParamWidget(QWidget):
    """
    A widget for editing a configuration parameter.
    Displays the parameter's name, an input field for its value, and a button to reset to default.
    """

    def __init__(self, param: ConfigParam, parent=None) -> None:
        super().__init__(parent)

        self.param = param
        self.label = QLabel(param.label, self)
        self.label.setWordWrap(True)
        self.label.setMaximumHeight(40)
        self.label.setFixedWidth(200)
        self.setContentsMargins(0, 0, 0, 0)

        self.input: ParamEditWidget | QLineEdit | None = None

        # Create the label, input field, and reset button
        if param.edit_widget is not None and isinstance(param.edit_widget, type):
            self.input = param.edit_widget(parent=self)
            self.set_value(self.param.default)
        elif param.edit_widget is not None and isinstance(param.edit_widget, ParamEditWidget):
            self.input = param.edit_widget
            self.set_value(self.param.default)

        if self.input is None:
            self.input = QLineEdit(str(param.default), self)

        # Create the reset button with an icon
        self.reset_button = QPushButton(self)
        reset_icon = QIcon.fromTheme("system-reboot")
        self.reset_button.setIcon(reset_icon)
        self.reset_button.setIconSize(QSize(12, 12))
        self.reset_button.setFlat(True)
        self.reset_button.setFixedSize(QSize(16, 16))
        self.reset_button.setToolTip("Сбросить к значению по умолчанию")

        # Set the tooltip and widget value
        # self.label.setToolTip(param.tooltip)
        self.input.setToolTip(param.tooltip)

        # Set up the layout
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input, stretch=1)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)

        # Connect the reset button signal
        self.reset_button.clicked.connect(self.reset_to_default)
        self.setMinimumHeight(0)

    def reset_to_default(self):
        """Reset the value in the input field to the default value."""
        self.set_value(self.param.default)

    def get_value(self) -> Any:
        """Get the current value from the input field."""
        if isinstance(self.input, QLineEdit):
            return self.input.text()
        if isinstance(self.input, ParamEditWidget):
            return self.input.get_value()

        raise NotImplementedError

    def set_value(self, value: Any):
        """Set a value in the input field."""
        if isinstance(self.input, QLineEdit):
            self.input.setText(str(value))
        elif isinstance(self.input, ParamEditWidget):
            self.input.set_value(value)
        else:
            raise NotImplementedError


# Number Widget
class NumberWidget(ParamEditWidget):
    def __init__(self, min_value=0, max_value=10000, parent=None) -> None:
        super().__init__(parent)
        self.spinbox = QSpinBox(self)
        self.spinbox.setRange(min_value, max_value)

        layout = QHBoxLayout()
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def get_value(self) -> int:
        return self.spinbox.value()

    def set_value(self, value: int):
        self.spinbox.setValue(value)


# Open File Widget
class FileWidget(ParamEditWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.filepath = QLineEdit(self)
        self.browse_button = QPushButton("", self)
        self.browse_button.setIcon(QIcon.fromTheme("document-open"))
        self.browse_button.setIconSize(QSize(14, 14))
        self.browse_button.setFixedSize(QSize(24, 24))

        layout = QHBoxLayout()
        layout.addWidget(self.filepath)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)

        # Connect button to open file dialog
        self.browse_button.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            self.filepath.setText(file_name)

    def get_value(self) -> str:
        return self.filepath.text()

    def set_value(self, value: str):
        self.filepath.setText(value)


# Color Widget
class ColorWidget(ParamEditWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.color_button = QPushButton("Выбрать", self)
        self.color_string = QLineEdit(self)
        self.color_string.setReadOnly(True)
        self.color_preview = QLabel(self)
        self.color_preview.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setFrameStyle(QFrame.Shape.StyledPanel)
        self.color_string.setReadOnly(True)

        layout = QHBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.color_string)
        layout.addWidget(self.color_preview)
        self.setLayout(layout)

        # Connect button to open color dialog
        self.color_button.clicked.connect(self.open_color_dialog)
        self.color_preview.mousePressEvent = lambda *_: self.open_color_dialog()  # type: ignore [method-assign]

    def open_color_dialog(self) -> None:
        initial_color = QColor(255, 255, 255, 255) if not self.color_string.text() else self.parse_color(self.color_string.text())
        color_dialog = QColorDialog.getColor(initial=initial_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color_dialog.isValid():
            rgba_str = f"rgba({color_dialog.red()}, {color_dialog.green()}, {color_dialog.blue()}, {color_dialog.alpha()})"
            self.set_value(rgba_str)

    def get_value(self) -> str:
        return self.color_string.text()

    def parse_color(self, value: str) -> QColor:
        """Parse a rgba string into a QColor object."""
        if not re.match(r"rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)", value):
            return QColor(255, 255, 255, 255)
        rgba = value[5:-1].split(", ")
        return QColor(int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3]))

    def to_rgba(self, color: QColor) -> str:
        """Convert a QColor object into a rgba string."""
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})"

    def set_value(self, value: str):
        """Set the value from an rgba string."""
        color = self.parse_color(value)
        rgba = self.to_rgba(color)
        self.color_string.setText(rgba)
        self.color_preview.setStyleSheet(f"background-color: {rgba};")


class SettingsWindow(QDialog):
    """
    A window containing multiple ParamWidgets for editing configuration parameters grouped by categories.
    """

    saved = pyqtSignal()

    def __init__(self, config_params: dict[str, ConfigParam], parent=None) -> None:
        super().__init__(parent)
        # set font size
        font = self.font()
        font.setPointSize(10)
        self.setFont(font)

        self.setWindowTitle("Настройки")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon.fromTheme("document-properties"))
        self.config_params = config_params

        # Create a layout for the window
        main_layout = QHBoxLayout()

        # Create a QListWidget for selecting groups
        self.group_list = QListWidget()
        self.group_list.setFixedWidth(250)
        self.group_list.itemClicked.connect(self.change_group)

        # Create a stacked widget to hold settings for each group
        self.settings_stack = QStackedWidget(self)
        self.settings_stack.setContentsMargins(0, 0, 0, 0)

        # Create Save and Close buttons
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_settings)

        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close)

        # Create a dictionary to hold ParamWidgets by group
        self.param_widgets_by_group: dict[str, list[ParamWidget]] = {}

        # Add the groups and populate the ParamWidgets
        self.populate_groups()

        # Add group_list and settings_stack to the layout
        main_layout.addWidget(self.group_list)
        main_layout.addWidget(self.settings_stack)

        # Add buttons at the bottom
        button_layout = QHBoxLayout()
        # Add separator
        button_layout.addStretch(1)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.close_button)

        # Create main layout (settings + buttons at the bottom)
        main_window_layout = QVBoxLayout()
        main_window_layout.addLayout(main_layout, stretch=1)
        main_window_layout.addLayout(button_layout)

        self.setLayout(main_window_layout)
        self.setMinimumHeight(500)
        self.setMinimumWidth(300)

    def populate_groups(self) -> None:
        """Populate the group list and create ParamWidgets for each group."""
        groups = list({param.group for param in self.config_params.values()})  # Get unique groups
        groups = sorted(groups)
        group_order = AppConfig.config_group_order
        extra_groups = [group for group in groups if group not in group_order]
        groups = group_order + extra_groups

        # Create a QListWidgetItem for each group and a page in the stack
        for group in groups:
            # Create a new QListWidgetItem for the group
            group_item = QListWidgetItem(group)
            self.group_list.addItem(group_item)

            # Create a new QWidget (page) for the group settings
            group_widget = QWidget()
            group_layout = QVBoxLayout()
            group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            group_layout.setSpacing(0)

            # Create ParamWidgets for each parameter in this group
            param_widgets = []
            for param_name, param in self.config_params.items():
                if param.group == group:
                    param_widget = ParamWidget(param)
                    param_widget.set_value(AppConfig.get_param(param_name))
                    param_widgets.append(param_widget)
                    group_layout.addWidget(param_widget)

            group_layout.addStretch(1)
            group_widget.setLayout(group_layout)
            self.settings_stack.addWidget(group_widget)

            # Store the param widgets for this group
            self.param_widgets_by_group[group] = param_widgets

        # Show the first group by default
        self.group_list.setCurrentRow(0)
        self.settings_stack.setCurrentIndex(0)

    def change_group(self, item: QListWidgetItem):
        """Change the displayed group when a new group is selected."""
        group_index = self.group_list.row(item)
        self.settings_stack.setCurrentIndex(group_index)

    def save_settings(self):
        """Save the settings by updating the configuration parameters."""
        require_reload = False
        for param_widgets in self.param_widgets_by_group.values():
            for widget in param_widgets:
                param_value = widget.get_value()
                param_name = widget.param.name
                if param_value != AppConfig.get_param(param_name):
                    if AppConfig.get_param_info(param_name).require_reload:
                        require_reload = True
                    AppConfig.set_param(param_name, param_value)

        # Save the configuration to the file
        AppConfig.save_config()
        if require_reload:
            utils.show_info_dialog("Информация", "Для применения изменений требуется перезагрузка приложения.")
        self.saved.emit()
        self.close()
