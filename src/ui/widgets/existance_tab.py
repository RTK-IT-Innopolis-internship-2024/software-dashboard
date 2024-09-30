from collections.abc import Callable

import pandas as pd
from PyQt6.QtCore import Qt, pyqtBoundSignal
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QSplitter, QVBoxLayout, QWidget

from src.ui.widgets.pandas_table import CheckableTableView
from src.ui.widgets.plot_widget import PlotWidget
from src.utils import utils
from src.utils.config import AppConfig


class ExistanceTab(QWidget):
    def __init__(
        self,
        existance_column_name: str,
        plot_name: str,
        parent=None,
        on_filter_changed: pyqtBoundSignal | None = None,
        data_getter: Callable[[], pd.DataFrame] | None = None,
    ) -> None:
        super().__init__(parent)
        self.existance_column_name = existance_column_name
        self.plot_name = plot_name
        self.data_getter = data_getter
        layout = QVBoxLayout(self)

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
        plot = PlotWidget.from_config(
            name=self.plot_name,
            title_template=f"{self.existance_column_name} по классам",
            x_axis_title="Классы",
            y_axis_title="Процент",
            column_names=["Нет", "Да", "В разработке", "Не используется", "(пусто)"],
            singular_title_template=f'{self.existance_column_name} по классу "{{x}}"',
            legend_title="Наличие имз",
            parent=self,
        )
        plot.colors = [
            AppConfig.PLOT_RED_COLOR,
            AppConfig.PLOT_GREEN_COLOR,
            AppConfig.PLOT_ORANGE_COLOR,
            AppConfig.PLOT_DARK_GRAY_COLOR,
            AppConfig.PLOT_GRAY_COLOR,
        ]

        return plot

    def update_plot(self) -> None:
        if self.data is None:
            return
        self.plot.update_plot(self.data, self.table.get_checked_mask())

    def set_table_model(self) -> None:
        if self.data is None:
            return
        formatted_data = utils.format_percent(self.data, exclude=["Класс ИС ИМЗ / Наименование", "Кол-во систем"])
        self.table.set_table_model(formatted_data, "Класс ИС ИМЗ", [50, 50, 90, 100, 70])

    def update_data(self) -> None:
        self.set_table_model()
        self.update_plot()

    def load_data(self, status: str | None = None, stage: str | None = None) -> None:
        if self.data_getter is None:
            return
        data_df: pd.DataFrame = self.data_getter()
        if data_df.empty:
            self.data = None
            return
        if status is not None and status != "(все)":
            data_df = data_df[data_df["Статус принадлежности к целевой архитектуре / Наименование"] == status]
        if stage is not None and stage != "(все)":
            data_df = data_df[data_df["Этап ЖЦ / Наименование"] == stage]
        data = (
            data_df[["Класс ИС ИМЗ / Наименование", self.existance_column_name]].melt(id_vars="Класс ИС ИМЗ / Наименование").fillna({"value": "(пусто)"})
        )
        data["value"] = data["value"].replace({"разработка": "в разработке", "минус": "нет", "?": "(пусто)"})

        data = data.groupby(["Класс ИС ИМЗ / Наименование", "value"])
        data = data.size()
        data = data.groupby(level=0).transform(lambda x: x / x.sum())
        data = data.unstack()  # noqa: PD010
        data = data.rename_axis(index=None, columns=None)
        cols = ["нет", "да", "в разработке", "не используют", "(пусто)"]
        for col in cols:
            if col not in data.columns:
                data[col] = 0
        data = data[cols]
        data = data.rename(
            columns={
                "да": "Да",
                "нет": "Нет",
                "в разработке": "В разработке",
                "не используют": "Не используется",
            }
        )
        data = data.fillna(0)

        system_count = data_df.groupby("Класс ИС ИМЗ / Наименование").size()
        data["Кол-во систем"] = system_count
        idx = data.index.to_list()
        if "(пусто)" in idx:
            idx.remove("(пусто)")
            idx.insert(0, "(пусто)")
        data = data.reindex(idx)

        self.data = data

    def refresh(self, status: str | None = None, stage: str | None = None) -> None:
        self.load_data(status, stage)
        self.update_data()

    def export_plot(self, file_path: str) -> None:
        if self.data is None:
            return
        self.plot.export_plot(self.data, self.table.get_checked_mask(), file_path)
