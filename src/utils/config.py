import sys
from pathlib import Path


class AppConfig:
    """
    Configuration File
    """

    APP_NAME: str = "БФТ-КПЭ"

    APP_ROOT: Path = Path(sys.argv[0]).resolve().parent.parent
    FONT_SIZE: int = 12

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
