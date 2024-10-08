import webbrowser
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QProgressDialog, QTabWidget, QVBoxLayout, QWidget

from src.backend.controllers.dashboard_controller import parse_data_sheet0
from src.ui.widgets.dashboard_tab import DashboardTab
from src.ui.widgets.existance_tab import ExistanceTab
from src.ui.widgets.registry_tab import RegistryTab
from src.ui.widgets.settings_window import SettingsWindow
from src.ui.widgets.toolbar import ToolBar
from src.utils import utils
from src.utils.config import AppConfig


class MainWindow(QMainWindow):
    filter_changed = pyqtSignal(list, list, list, list)

    def __init__(self) -> None:
        super().__init__()
        self.current_status: list[str] = []
        self.current_stage: list[str] = []
        self.current_landscape: list[str] = []
        self.current_import: list[str] = []
        self.data = pd.DataFrame()
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setGeometry(50, 50, 1200, 900)
        self.setMinimumSize(*AppConfig.WINDOW_MINIMIUM_SIZE)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        central_widget.setLayout(layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { font-size: 18px; }")
        self.tabs.tabBarClicked.connect(self.tab_changed)
        layout.addWidget(self.tabs)

        self.registry_tab = RegistryTab(self, self.filter_changed, self.get_data)
        self.tabs.addTab(self.registry_tab, "Наличие в реестре")

        self.OS_existance_tab = ExistanceTab("Наличие имз ОС", "OS", self, self.filter_changed, self.get_data)
        self.tabs.addTab(self.OS_existance_tab, "Наличие имз ОС")

        self.virtualization_existance_tab = ExistanceTab("Наличие имз Виртуализации", "virtualization", self, self.filter_changed, self.get_data)
        self.tabs.addTab(self.virtualization_existance_tab, "Наличие имз Виртуализации")

        self.DBMS_existance_tab = ExistanceTab("Наличие имз СУБД", "DBMS", self, self.filter_changed, self.get_data)
        self.tabs.addTab(self.DBMS_existance_tab, "Наличие имз СУБД")

        self.dashboard_tab = DashboardTab(
            self,
            [
                self.registry_tab.plot.plot_updated,
                self.OS_existance_tab.plot.plot_updated,
                self.virtualization_existance_tab.plot.plot_updated,
                self.DBMS_existance_tab.plot.plot_updated,
            ],
        )
        self.tabs.addTab(self.dashboard_tab, "Дашборд")

        self.tab_list: list[RegistryTab | ExistanceTab] = [
            self.registry_tab,
            self.OS_existance_tab,
            self.virtualization_existance_tab,
            self.DBMS_existance_tab,
        ]

        self.topbar: ToolBar | None = None

    def tab_changed(self, index: int) -> None:
        if index == self.tabs.count() - 1:
            self.dashboard_tab.selected()

    def load_data(self) -> None:
        try:
            # Load file path and data
            file_path: Path = AppConfig.get_param("data_path")
            while file_path == "":
                utils.show_info_dialog("Не выбран файл", "Пожалуйста, выберите файл.")
                self.load_document(initialize=False)
                file_path = AppConfig.get_param("data_path")
            data: pd.DataFrame = parse_data_sheet0(file_path)
            self.data = data

        except FileNotFoundError:
            utils.show_error_dialog(
                "Ошибка: Файл не найден", f"Файл <i>{file_path!s}</i> не существует. Пожалуйста, проверьте правильность пути или выберите другой файл."
            )
            AppConfig.reset_param("data_path")

        except pd.errors.EmptyDataError:
            utils.show_error_dialog("Ошибка: Пустой файл данных", f"Файл <i>{file_path!s}</i> пуст. Пожалуйста, убедитесь, что файл содержит данные.")
            AppConfig.reset_param("data_path")

        except pd.errors.ParserError:
            utils.show_error_dialog(
                "Ошибка: Некорректный файл данных",
                f"Файл <i>{file_path!s}</i> имеет некорректные данные. Пожалуйста, проверьте правильность данных в файле.",
            )
            AppConfig.reset_param("data_path")

        except ValueError as e:
            utils.show_error_dialog(
                "Ошибка: Некорректный файл данных",
                f"Файл <i>{file_path!s}</i> имеет некорректные данные.<br>{e!s}",
            )
            AppConfig.reset_param("data_path")

        except Exception as e:  # noqa: BLE001
            utils.show_error_dialog(
                "Неизвестная ошибка", f"Произошла неизвестная ошибка с файлом <i>{file_path!s}</i>:<br><span style='color:red'>{e!s}</span>"
            )
            AppConfig.reset_param("data_path")

        else:
            return

        self.data = pd.DataFrame()

    def get_data(self) -> pd.DataFrame:
        return self.data

    def create_toolbar(self) -> None:
        if self.topbar is not None:
            self.removeToolBar(self.topbar)
        self.topbar = ToolBar(
            self,
            orientation=Qt.Orientation.Horizontal,
            style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
            icon_size=(30, 30),
            font_size=AppConfig.get_param("font_size"),
        )

        data: pd.DataFrame = self.get_data()

        if not data.empty and data is not None:
            self.status_options = ["(все)", *data["Статус принадлежности к целевой архитектуре / Наименование"].unique()]
            if "(пусто)" in self.status_options:
                self.status_options.remove("(пусто)")
                self.status_options.append("(пусто)")
            self.current_status = self.status_options.copy()
            self.topbar.add_multiselect_option_list(
                "Целевая архитектура",
                self.status_options,
                self.on_status_change,
            )

            self.topbar.add_fixed_separator(30)

            self.stage_options = ["(все)", *data["Этап ЖЦ / Наименование"].unique()]
            if "(пусто)" in self.stage_options:
                self.stage_options.remove("(пусто)")
                self.stage_options.append("(пусто)")
            self.current_stage = self.stage_options.copy()
            self.topbar.add_multiselect_option_list(
                "Этап ЖЦ",
                self.stage_options,
                self.on_stage_change,
            )

            self.topbar.add_fixed_separator(30)

            self.landscape_options = ["(все)", *data["ИТ-ландшафт / Наименование"].unique()]
            if "(пусто)" in self.landscape_options:
                self.landscape_options.remove("(пусто)")
                self.landscape_options.append("(пусто)")
            self.current_landscape = self.landscape_options.copy()
            self.topbar.add_multiselect_option_list(
                "ИТ-ландшафт",
                self.landscape_options,
                self.on_landscape_change,
            )

            self.topbar.add_fixed_separator(30)

            self.import_options = ["(все)", *data["Целевая ИС для задач импортозамещения"].unique()]
            if "(пусто)" in self.import_options:
                self.import_options.remove("(пусто)")
                self.import_options.append("(пусто)")
            self.current_import = self.import_options.copy()
            self.topbar.add_multiselect_option_list(
                "Целевая ИС",
                self.import_options,
                self.on_import_change,
            )

        self.topbar.add_separator()
        self.topbar.add_button(
            "Загрузить данные", AppConfig.get_resource_path("resources/assets/icons/windows/shell32-276.ico"), lambda: self.load_document(initialize=True)
        )
        self.topbar.add_button("Экспорт графика", AppConfig.get_resource_path("resources/assets/icons/windows/shell32-265.ico"), self.export_plot)
        self.topbar.add_button("Настройки", AppConfig.get_resource_path("resources/assets/icons/windows/shell32-315.ico"), self.open_settings)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topbar)

    def open_settings(self) -> None:
        self.settings_window = SettingsWindow(AppConfig.config_info, self)
        self.settings_window.saved.connect(self.initialize)
        self.settings_window.show()

    def get_filter(self) -> tuple[list[str], list[str], list[str], list[str]]:
        return (self.current_status, self.current_stage, self.current_landscape, self.current_import)

    def on_status_change(self, values: list[str]) -> None:
        self.current_status = values
        self.filter_changed.emit(*self.get_filter())

    def on_stage_change(self, values: list[str]) -> None:
        self.current_stage = values
        self.filter_changed.emit(*self.get_filter())

    def on_landscape_change(self, values: list[str]) -> None:
        self.current_landscape = values
        self.filter_changed.emit(*self.get_filter())

    def on_import_change(self, values: list[str]) -> None:
        self.current_import = values
        self.filter_changed.emit(*self.get_filter())

    def load_document(self, initialize: bool = True) -> None:  # noqa: FBT001, FBT002
        """
        Opens a file dialog to select an .xlsx file. If a valid file is selected,
        updates the 'data_path' configuration. Displays an error dialog for invalid files.
        """
        # Open a file dialog to select an .xlsx file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None,
            "Выберите файл",
            AppConfig.get_param("data_path"),  # Start path
            "Excel Files (*.xlsx)",
        )

        if file_path:  # If a file was selected
            selected_file = Path(file_path)

            # Check if the file has an .xlsx extension
            if selected_file.suffix == ".xlsx":
                # Update the 'data_path' parameter
                try:
                    AppConfig.set_param("data_path", str(selected_file))
                    if initialize:
                        self.initialize()
                except Exception as e:  # noqa: BLE001
                    utils.show_error_dialog("Ошибка", f"Не удалось обновить путь к файлу:<br><span style='color:red'>{e!s}</span>")
            else:
                # If the file is not an .xlsx file, show an error dialog
                utils.show_error_dialog("Неверный файл", "Выбранный файл не является файлом .xlsx. Пожалуйста, выберите файл с правильным расширением.")
        else:
            # If no file was selected, do nothing
            pass

    def export_plot(self) -> None:
        """
        Exports the plot of the currently active tab as a PNG file.
        Prompts the user to choose the file path using a file dialog, handles any errors,
        and opens the exported image upon success.
        """
        try:
            # Get current date and active tab name
            current_date = datetime.now(tz=UTC).strftime("%d.%m.%Y")
            active_tab_index = self.tabs.currentIndex()
            active_tab_name = self.tabs.tabText(active_tab_index)

            if active_tab_index == self.tabs.count() - 1:
                utils.show_info_dialog("Не поддерживается", "Экспорт графиков для данной вкладки не поддерживается.")
                return

            export_folder = Path(AppConfig.get_some_path("exports"))

            if not export_folder.exists():
                export_folder.mkdir()

            # Default file name for the export
            default_file_name = AppConfig.get_some_path(f"exports/{current_date} - {active_tab_name}.png")

            # Open a file dialog for saving the PNG file
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                None,
                "Сохранить график как",
                default_file_name,
                "PNG Files (*.png)",  # Filter to PNG files
            )

            # If a valid file path is chosen
            if file_path:
                selected_file = Path(file_path)

                # Check if the file extension is '.png'
                if selected_file.suffix != ".png":
                    # Show error if the file extension is not '.png'
                    utils.show_error_dialog("Неверный формат", "Пожалуйста, выберите файл с расширением .png.")
                    return

                self.tab_list[active_tab_index].export_plot(str(selected_file))

                # If export is successful, open the PNG file
                if selected_file.exists():
                    webbrowser.open(str(selected_file))
                else:
                    utils.show_error_dialog("Ошибка экспорта", "Не удалось найти созданный файл после экспорта.")

        except Exception as e:  # noqa: BLE001
            # Handle any other unexpected errors
            utils.show_error_dialog("Ошибка при экспорте", f"Произошла ошибка во время экспорта:<br><span style='color:red'>{e!s}</span>")

    def initialize(self) -> None:
        # Create a progress dialog
        progress_dialog = QProgressDialog("Загрузка данных", None, 0, 6)
        current_progress = 0
        progress_dialog.setMinimumSize(400, 120)
        progress_dialog.setWindowTitle("Загрузка данных")
        progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress_dialog.setAutoClose(True)  # Automatically close when done
        progress_dialog.setAutoReset(True)  # Reset progress bar after close
        progress_dialog.show()

        # Load data and Initialize toolbar and update progress
        self.load_data()
        self.create_toolbar()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Initialize registry_tab and update progress
        self.registry_tab.initialize()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Initialize OS_existance_tab and update progress
        self.OS_existance_tab.initialize()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Initialize virtualization_existance_tab and update progress
        self.virtualization_existance_tab.initialize()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Initialize DBMS_existance_tab and update progress
        self.DBMS_existance_tab.initialize()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Initialize dashboard_tab and update progress
        self.dashboard_tab.initialize()
        current_progress += 1
        progress_dialog.setValue(current_progress)

        # Close the dialog when done
        progress_dialog.close()
