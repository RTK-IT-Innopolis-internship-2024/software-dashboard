import json
import sys
from pathlib import Path
from typing import Any, ClassVar

from PyQt6.QtWidgets import QWidget


class ParamEditWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

    def get_value(self) -> Any:
        """Get the current value from the input field."""
        raise NotImplementedError

    def set_value(self, value: Any):
        """Set a value in the input field."""
        raise NotImplementedError


class ConfigParam:
    def __init__(
        self,
        name: str,
        default: Any,
        label: str = "",
        group: str = "",
        tooltip: str = "",
        edit_widget: type[ParamEditWidget] | ParamEditWidget | None = None,
        require_reload: bool = False,  # noqa: FBT001, FBT002
    ):
        self.default = default
        self.name = name
        self.label = label
        self.group = group
        self.tooltip = tooltip
        self.edit_widget = edit_widget
        self.require_reload = require_reload

    def __repr__(self):
        return f"ConfigParam(default={self.default}, name={self.name}, group={self.group}, tooltip={self.tooltip}, edit_widget={self.edit_widget})"

    def __str__(self):
        return f"ConfigParam(default={self.default}, name={self.name}, group={self.group}, tooltip={self.tooltip}, edit_widget={self.edit_widget})"


class AppConfig:
    """
    Configuration File
    """

    APP_NAME: str = "БФТ-КПЭ"

    APP_ROOT: Path = Path(sys.argv[0]).resolve().parent
    CONFIG_FILE: Path = APP_ROOT / "app_config.json"  # File to save configuration

    # Widget customization variables
    WINDOW_MINIMIUM_SIZE: tuple[int, int] = (1200, 700)

    # Plot customization variables
    PLOT_MARGINS: ClassVar[dict] = {"l": 40, "r": 40, "t": 40, "b": 40}

    # Configurable parameters
    config_params: ClassVar[dict[str, Any]] = {}  # Store actual config values
    config_info: ClassVar[dict[str, ConfigParam]] = {}  # Store default values and descriptions
    config_group_order: ClassVar[list[str]] = []  # List of groups in the order they should be displayed

    @classmethod
    def initialize(cls) -> None:
        """Load configuration from the file, if it exists."""
        if cls.CONFIG_FILE.exists():
            with cls.CONFIG_FILE.open(encoding="utf-8") as f:
                cls.config_params = json.load(f)
        else:
            cls.config_params = {}  # Initialize with empty if no config file

    @classmethod
    def register_param(
        cls,
        name: str,
        default: Any,
        label: str = "",
        group: str = "",
        tooltip: str = "",
        edit_widget: type[ParamEditWidget] | ParamEditWidget | None = None,
        require_reload: bool = False,  # noqa: FBT001, FBT002
    ):
        """
        Register a configuration parameter with its default value and description.
        :param name: The name of the parameter.
        :param default: The default value of the parameter.
        :param description: Description of the parameter.
        """
        cls.config_info[name] = ConfigParam(name, default, label, group, tooltip, edit_widget, require_reload)

    @classmethod
    def set_group_order(cls, group_order: list[str]):
        """
        Set the order of the groups in the config file.
        :param group_order: The order of the groups in the config file.
        """
        cls.config_group_order = group_order

    @classmethod
    def get_param_info(cls, name: str) -> ConfigParam:
        """
        Get the description of a configuration parameter.
        :param name: The name of the parameter.
        :return: The description of the parameter.
        :raises: Exception if the parameter is not found or not registered.
        """
        if name in cls.config_info:
            return cls.config_info[name]
        raise KeyError(f"Parameter '{name}' is not registered")

    @classmethod
    def get_param(cls, name: str) -> Any:
        """
        Get the value of a configuration parameter.
        :param name: The name of the parameter.
        :return: The value of the parameter or the default if not set.
        :raises: Exception if the parameter is not found or not registered.
        """
        if name in cls.config_info:
            return cls.config_params.get(name, cls.config_info[name].default)
        raise KeyError(f"Parameter '{name}' is not registered")

    @classmethod
    def set_param(cls, name: str, value: Any):
        """
        Set the value of a configuration parameter and save it to the file.
        :param name: The name of the parameter.
        :param value: The value to be set.
        :raises: Exception if the parameter is not found or not registered.
        """
        if name in cls.config_info:
            cls.config_params[name] = value
            cls.save_config()
        else:
            raise KeyError(f"Parameter '{name}' is not registered")

    @classmethod
    def reset_param(cls, name: str):
        """
        Reset the value of a configuration parameter to its default and save it to the file.
        :param name: The name of the parameter.
        :raises: Exception if the parameter is not found or not registered.
        """
        if name in cls.config_info:
            cls.config_params[name] = cls.config_info[name].default
            cls.save_config()
        else:
            raise KeyError(f"Parameter '{name}' is not registered")

    @classmethod
    def save_config(cls) -> None:
        """Save the configuration parameters to the config file."""
        with cls.CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(cls.config_params, f, ensure_ascii=False, indent=4)

    @classmethod
    def get_some_path(cls, relative_path: str) -> str:
        """
        Returns the absolute path to a resource, useful for handling files in PyInstaller-built applications.
        :param relative_path: Relative path to the resource.
        :return: Absolute path to the resource.
        """
        return str(cls.APP_ROOT / relative_path)

    @classmethod
    def get_resource_path(cls, relative_path: str) -> str:
        """
        Returns the absolute path to a resource, useful for handling files in PyInstaller-built applications.
        :param relative_path: Relative path to the resource.
        :return: Absolute path to the resource.
        """
        base_path = Path(getattr(sys, "_MEIPASS", cls.APP_ROOT))
        return str(base_path / relative_path)
