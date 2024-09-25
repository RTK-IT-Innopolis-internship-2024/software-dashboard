from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget

from ui.widgets.registry_tab import RegistryTab
from utils.config import AppConfig


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setGeometry(200, 200, 1200, 900)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        central_widget.setLayout(layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { font-size: 18px; }")
        layout.addWidget(self.tabs)

        self.registry_tab = RegistryTab(self)
        self.tabs.addTab(self.registry_tab, "Наличие в реестре")

    def initialize(self) -> None:
        self.registry_tab.initialize()

    def settings_window(self) -> None:
        """
        Event handler for the "Settings" button. Displays the "Settings" window.
        """
