from pathlib import Path

from PyQt6.QtCore import Qt, QUrl, pyqtBoundSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QSplitter, QVBoxLayout, QWidget

from src.utils.config import AppConfig


class DashboardTab(QWidget):
    def __init__(self, parent=None, on_plot_updated: list[pyqtBoundSignal] | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.plot_paths = [Path(AppConfig.get_some_path(f"html/{i}.html")) for i in ["registry", "virtualization", "DBMS", "OS"]]

        self.plots = [self.create_plot(path) for path in self.plot_paths]
        self.scroll_plots = [self.wrap_plot(plot) for plot in self.plots]

        vertical_splitter = QSplitter(Qt.Orientation.Vertical, self)
        vertical_splitter.setOpaqueResize(False)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setOpaqueResize(False)
        self.splitter.addWidget(self.scroll_plots[0])
        self.splitter.addWidget(self.scroll_plots[1])
        vertical_splitter.addWidget(self.splitter)

        self.splitter_2 = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter_2.setOpaqueResize(False)
        self.splitter_2.addWidget(self.scroll_plots[2])
        self.splitter_2.addWidget(self.scroll_plots[3])
        vertical_splitter.addWidget(self.splitter_2)

        parent_layout = QHBoxLayout()
        parent_layout.addWidget(vertical_splitter, stretch=1)
        layout.addLayout(parent_layout, stretch=1)

        if on_plot_updated is not None:
            for plot_updated in on_plot_updated:
                plot_updated.connect(self.update_plots)

    def initialize(self) -> None:
        self.update_plots()

    def wrap_plot(self, plot: QWebEngineView) -> QScrollArea:
        scroll_plot_area = QScrollArea(self)
        scroll_plot_area.setWidgetResizable(True)
        scroll_plot_area.setWidget(plot)
        scroll_plot_area.setMinimumWidth(AppConfig.SCROLL_AREA_MIN_WIDTH_DASHBOARD)
        scroll_plot_area.setMinimumHeight(AppConfig.SCROLL_AREA_MIN_HEIGHT_DASHBOARD)

        return scroll_plot_area

    # plot using plotly
    def create_plot(self, file_path: Path) -> QWebEngineView:
        plot = QWebEngineView(self)
        plot.setMinimumSize(AppConfig.PLOT_MIN_WIDTH_DASHBOARD, AppConfig.PLOT_MIN_HEIGHT_DASHBOARD)
        if file_path.exists():
            plot.load(QUrl.fromLocalFile(str(file_path)))

        return plot

    def selected(self) -> None:
        for i in range(4):
            self.scroll_plots[i].adjustSize()

    def update_plots(self, file_updated: str = "", is_pie: bool = False) -> None:  # noqa: FBT001, FBT002
        for i in range(4):
            if self.plot_paths[i].exists():
                self.plots[i].setMinimumSize(AppConfig.PLOT_MIN_WIDTH_DASHBOARD, AppConfig.PLOT_MIN_HEIGHT_DASHBOARD)
                if file_updated == str(self.plot_paths[i]) and is_pie:
                    self.plots[i].setMinimumSize(0, 0)
                self.plots[i].load(QUrl.fromLocalFile(str(self.plot_paths[i])))
