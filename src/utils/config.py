import json
import sys
from pathlib import Path
from typing import Any, ClassVar


class ConfigParam:
    def __init__(self, default: Any, description: str = ""):
        self.default = default
        self.description = description


class AppConfig:
    """
    Configuration File
    """

    APP_NAME: str = "БФТ-КПЭ"

    APP_ROOT: Path = Path(sys.argv[0]).resolve().parent
    CONFIG_FILE: Path = APP_ROOT / "app_config.json"  # File to save configuration

    # Widget customization variables
    FONT_SIZE: int = 12  # Font size for all widgets (does not affect plot widget)
    TABLE_MINIMUM_WIDTH: int = 510
    WINDOW_MINIMIUM_SIZE: tuple[int, int] = (1200, 700)

    # Plot customization variables
    PLOT_RED_COLOR: str = "rgb(220, 20, 60)"
    PLOT_GREEN_COLOR: str = "rgb(0, 176, 80)"
    PLOT_GRAY_COLOR: str = "rgb(200, 200, 200)"
    PLOT_ORANGE_COLOR: str = "rgb(255, 140, 0)"
    PLOT_DARK_GRAY_COLOR: str = "rgb(100, 100, 100)"
    PLOT_BACKGROUND_COLOR: str = "rgba(0, 0, 0, 0)"  # transparent

    PLOT_TICK_FONT_SIZE: int = 15
    PLOT_LEGEND_FONT_SIZE: int = 15
    PLOT_TITLE_FONT_SIZE: int = 22
    PLOT_HOVER_FONT_SIZE: int = 16
    PLOT_TEXT_INFO_FONT_SIZE: int = 14  # Used for info text in plot widget (e.g. "75%")

    PLOT_TRUNCATE_LEN: int = 30

    PLOT_MARGINS: ClassVar[dict] = {"l": 40, "r": 40, "t": 40, "b": 40}

    SCROLL_AREA_MIN_WIDTH: int = 600
    SCROLL_AREA_MIN_HEIGHT: int = 600

    SCROLL_AREA_MIN_WIDTH_DASHBOARD: int = 300
    SCROLL_AREA_MIN_HEIGHT_DASHBOARD: int = 300

    PLOT_MIN_WIDTH: int = 1200
    PLOT_MIN_HEIGHT: int = 800

    PLOT_MIN_WIDTH_DASHBOARD: int = 800
    PLOT_MIN_HEIGHT_DASHBOARD: int = 600

    EXPORT_PLOT_WIDTH: int = 1920
    EXPORT_PLOT_HEIGHT: int = 1080

    # Configurable parameters
    config_params: ClassVar[dict[str, Any]] = {}  # Store actual config values
    config_info: ClassVar[dict[str, ConfigParam]] = {}  # Store default values and descriptions

    @classmethod
    def initialize(cls) -> None:
        """Load configuration from the file, if it exists."""
        if cls.CONFIG_FILE.exists():
            with cls.CONFIG_FILE.open(encoding="utf-8") as f:
                cls.config_params = json.load(f)
        else:
            cls.config_params = {}  # Initialize with empty if no config file

    @classmethod
    def register_param(cls, name: str, default: Any, description: str = ""):
        """
        Register a configuration parameter with its default value and description.
        :param name: The name of the parameter.
        :param default: The default value of the parameter.
        :param description: Description of the parameter.
        """
        cls.config_info[name] = ConfigParam(default, description)

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
