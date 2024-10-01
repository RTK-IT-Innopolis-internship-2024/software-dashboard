from collections.abc import Callable

import pandas as pd
from PyQt6.QtCore import Qt, pyqtBoundSignal
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QSplitter, QVBoxLayout, QWidget

from src.ui.widgets.pandas_table import CheckableTableView
from src.ui.widgets.plot_widget import PlotWidget
from src.utils import utils
from src.utils.config import AppConfig


class RegistryTab(QWidget):
    def __init__(self, parent=None, on_filter_changed: pyqtBoundSignal | None = None, data_getter: Callable[[], pd.DataFrame] | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.data_getter = data_getter

        # Main Table and plot
        self.table = self.create_table()
        self.table.checked_updated.connect(self.update_plot)
        self.plot = self.create_plot()

        self.scroll_plot_area = QScrollArea(self)
        self.scroll_plot_area.setWidgetResizable(True)
        self.scroll_plot_area.setWidget(self.plot)
        self.scroll_plot_area.setMinimumWidth(AppConfig.SCROLL_AREA_MIN_WIDTH)
        self.scroll_plot_area.setMinimumHeight(AppConfig.SCROLL_AREA_MIN_HEIGHT)

        content_layout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setOpaqueResize(False)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.scroll_plot_area)
        self.splitter.splitterMoved.connect(self.splitter_changed)
        self.table_min = True

        content_layout.addWidget(self.splitter, stretch=1)
        layout.addLayout(content_layout, stretch=1)

        if on_filter_changed is not None:
            on_filter_changed.connect(self.refresh)

        self.on_resize()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.on_resize()

    def splitter_changed(self) -> None:
        self.table_min = self.splitter.sizes()[0] == AppConfig.TABLE_MINIMUM_WIDTH

    def on_resize(self) -> None:
        if self.table_min:
            self.splitter.setSizes([AppConfig.TABLE_MINIMUM_WIDTH, self.width() - AppConfig.TABLE_MINIMUM_WIDTH])

    def initialize(self) -> None:
        self.load_data()
        self.update_data()

    def create_table(self) -> CheckableTableView:
        return CheckableTableView(self, minimum_width=AppConfig.TABLE_MINIMUM_WIDTH)

    # plot using plotly
    def create_plot(self) -> PlotWidget:
        return PlotWidget.from_config(
            name="registry",
            title_template="Выполнение КПЭ по классам",
            x_axis_title="Классы",
            y_axis_title="Процент",
            column_names=["Нет в реестре", "Есть в реестре", "(пусто)"],
            singular_title_template='Выполнение КПЭ по классу "{x}"',
            legend_title="Наличие в реестре",
            parent=self,
        )

    def update_plot(self) -> None:
        if self.data is None:
            return
        self.plot.update_plot(self.data, self.table.get_checked_mask())

    def set_table_model(self) -> None:
        if self.data is None:
            return
        formatted_data = utils.format_percent(self.data, exclude=["Класс ИС ИМЗ / Наименование", "Кол-во систем"])
        self.table.set_table_model(formatted_data, "Класс ИС ИМЗ")

    def update_data(self) -> None:
        self.set_table_model()
        self.update_plot()

    def load_data(
        self, status: list[str] | None = None, stage: list[str] | None = None, landscape: list[str] | None = None, import_type: list[str] | None = None
    ) -> None:
        if self.data_getter is None:
            return
        data_df: pd.DataFrame = self.data_getter()
        if data_df.empty:
            self.data = None
            return
        if status is not None:
            data_df = data_df[data_df["Статус принадлежности к целевой архитектуре / Наименование"].isin(status)]
        if stage is not None:
            data_df = data_df[data_df["Этап ЖЦ / Наименование"].isin(stage)]
        if landscape is not None:
            data_df = data_df[data_df["ИТ-ландшафт / Наименование"].isin(landscape)]
        if import_type is not None:
            data_df = data_df[data_df["Целевая ИС для задач импортозамещения"].isin(import_type)]

        if data_df.empty:
            self.data = pd.DataFrame(columns=["Нет в реестре", "Есть в реестре", "(пусто)"])
            return

        data = (
            data_df[["Класс ИС ИМЗ / Наименование", "Наличие в реестре Мин связи российского ПО"]]
            .melt(id_vars="Класс ИС ИМЗ / Наименование")
            .fillna({"value": -1})
            .groupby(["Класс ИС ИМЗ / Наименование", "value"])
        )
        data = data.size()
        data = data.groupby(level=0).transform(lambda x: x / x.sum())
        data = data.unstack()  # noqa: PD010
        data = data.rename_axis(index=None, columns=None)
        if 0.0 not in data.columns:
            data[0.0] = 0
        if 1.0 not in data.columns:
            data[1.0] = 0
        if -1.0 not in data.columns:
            data[-1.0] = 0
        data = data[[0.0, 1.0, -1.0]]
        data = data.rename(columns={-1.0: "(пусто)", 0.0: "Нет в реестре", 1.0: "Есть в реестре"})
        data = data.fillna(0)

        system_count = data_df.groupby("Класс ИС ИМЗ / Наименование").size()
        data["Кол-во систем"] = system_count
        idx = data.index.to_list()
        if "(пусто)" in idx:
            idx.remove("(пусто)")
            idx.insert(0, "(пусто)")
        data = data.reindex(idx)

        self.data = data

    def refresh(
        self, status: list[str] | None = None, stage: list[str] | None = None, landscape: list[str] | None = None, import_type: list[str] | None = None
    ) -> None:
        self.load_data(status, stage, landscape, import_type)
        self.update_data()

    def export_plot(self, file_path: str) -> None:
        if self.data is None:
            return
        self.plot.export_plot(self.data, self.table.get_checked_mask(), file_path)
