import os
import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.widgets.settings_window import ColorWidget, FileWidget, NumberWidget
from src.utils.config import AppConfig


# https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
def sigint_handler(*args):  # noqa: ARG001
    """Handler for the SIGINT signal."""
    sys.stderr.write("\r")
    QApplication.quit()


def initialize_params() -> None:
    """
    Initializes the application parameters.
    """
    AppConfig.register_param("data_path", "", label="Файл с данными", group="Основное", tooltip="Путь к файлу с данными", edit_widget=FileWidget)

    # Registering general settings
    AppConfig.register_param(
        "font_size",
        12,
        label="Размер шрифта",
        group="Основное",
        tooltip="Размер шрифта для всех виджетов (не влияет на графики). Необходимо перезагрузить при изменении.",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "table_min_width",
        510,
        label="Минимальная ширина таблицы",
        group="Основное",
        tooltip="Минимальная ширина таблицы в пикселях",
        edit_widget=NumberWidget,
    )

    # Plot customization variables
    AppConfig.register_param(
        "plot_red_color",
        "rgba(220, 20, 60, 255)",
        label="Цвет графика - Красный",
        group="Графики - Основные настройки",
        tooltip="Красный цвет для графиков",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_green_color",
        "rgba(0, 176, 80, 255)",
        label="Цвет графика - Зеленый",
        group="Графики - Основные настройки",
        tooltip="Зеленый цвет для графиков",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_gray_color",
        "rgba(200, 200, 200, 255)",
        label="Цвет графика - Серый",
        group="Графики - Основные настройки",
        tooltip="Серый цвет для графиков",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_orange_color",
        "rgba(255, 140, 0, 255)",
        label="Цвет графика - Оранжевый",
        group="Графики - Основные настройки",
        tooltip="Оранжевый цвет для графиков",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_dark_gray_color",
        "rgba(100, 100, 100, 255)",
        label="Цвет графика - Темно-серый",
        group="Графики - Основные настройки",
        tooltip="Темно-серый цвет для графиков",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_background_color",
        "rgba(0, 0, 0, 0)",
        label="Фон графика",
        group="Графики - Основные настройки",
        tooltip="Фоновый цвет графика (прозрачный по умолчанию)",
        edit_widget=ColorWidget,
    )

    AppConfig.register_param(
        "plot_tick_font_size",
        15,
        label="Размер шрифта осей",
        group="Графики - Настройки шрифтов",
        tooltip="Размер шрифта для меток осей",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_legend_font_size",
        15,
        label="Размер шрифта легенды",
        group="Графики - Настройки шрифтов",
        tooltip="Размер шрифта для легенды на графике",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_title_font_size",
        22,
        label="Размер шрифта заголовка",
        group="Графики - Настройки шрифтов",
        tooltip="Размер шрифта для заголовков графиков",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_hover_font_size",
        16,
        label="Размер шрифта при наведении",
        group="Графики - Настройки шрифтов",
        tooltip="Размер шрифта всплывающей информации при наведении",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_text_info_font_size",
        14,
        label="Размер шрифта информации",
        group="Графики - Настройки шрифтов",
        tooltip="Размер шрифта для информационного текста на графике (например, 75%)",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_truncate_len",
        30,
        label="Длина обрезки текста",
        group="Графики - Основные настройки",
        tooltip="Максимальная длина текста для обрезки (в символах)",
        edit_widget=NumberWidget,
    )

    # Scroll area dimensions
    AppConfig.register_param(
        "scroll_area_min_width",
        600,
        label="Минимальная ширина области прокрутки",
        group="Дополнительное",
        tooltip="Минимальная ширина области прокрутки в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    AppConfig.register_param(
        "scroll_area_min_height",
        600,
        label="Минимальная высота области прокрутки",
        group="Дополнительное",
        tooltip="Минимальная высота области прокрутки в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    AppConfig.register_param(
        "scroll_area_min_width_dashboard",
        300,
        label="Минимальная ширина дашборда",
        group="Дополнительное",
        tooltip="Минимальная ширина дашборда в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    AppConfig.register_param(
        "scroll_area_min_height_dashboard",
        300,
        label="Минимальная высота дашборда",
        group="Дополнительное",
        tooltip="Минимальная высота дашборда в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    # Plot dimensions
    AppConfig.register_param(
        "plot_min_width",
        1200,
        label="Минимальная ширина графика",
        group="Графики - Дополнительные настройки",
        tooltip="Минимальная ширина графика в пикселях",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_min_height",
        800,
        label="Минимальная высота графика",
        group="Графики - Дополнительные настройки",
        tooltip="Минимальная высота графика в пикселях",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "plot_min_width_dashboard",
        800,
        label="Минимальная ширина графика на дашборде",
        group="Графики - Дополнительные настройки",
        tooltip="Минимальная ширина графика на дашборде в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    AppConfig.register_param(
        "plot_min_height_dashboard",
        600,
        label="Минимальная высота графика на дашборде",
        group="Графики - Дополнительные настройки",
        tooltip="Минимальная высота графика на дашборде в пикселях",
        edit_widget=NumberWidget,
        require_reload=True,
    )

    # Export plot dimensions
    AppConfig.register_param(
        "export_plot_width",
        1920,
        label="Ширина экспортируемого графика",
        group="Экспорт",
        tooltip="Ширина графика для экспорта в пикселях",
        edit_widget=NumberWidget,
    )

    AppConfig.register_param(
        "export_plot_height",
        1080,
        label="Высота экспортируемого графика",
        group="Экспорт",
        tooltip="Высота графика для экспорта в пикселях",
        edit_widget=NumberWidget,
    )

    AppConfig.set_group_order(
        ["Основное", "Графики - Основные настройки", "Графики - Настройки шрифтов", "Графики - Дополнительные настройки", "Дополнительное", "Экспорт"]
    )

    AppConfig.initialize()


def run() -> int:
    """
    Initializes the application and runs it.
    """
    # set env variable QT_QPA_PLATFORM
    if os.name == "nt":
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"
    signal.signal(signal.SIGINT, sigint_handler)

    initialize_params()
    app: QApplication = QApplication(sys.argv)
    timer = QTimer()
    timer.start(1000)  # run every second
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

    window: MainWindow = MainWindow()
    window.initialize()
    window.show()
    return sys.exit(app.exec())
