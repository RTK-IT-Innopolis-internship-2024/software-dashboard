import typing
from pathlib import Path

if typing.TYPE_CHECKING:
    import pandas as pd
import plotly
import plotly.graph_objects as go
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QHBoxLayout, QHeaderView, QTableView, QVBoxLayout, QWidget

from backend.controllers.dashboard_controller import parse_data
from ui.widgets.pandas_table import PandasTableModel
from utils.config import AppConfig


class RegistryTab(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Main Table and plot
        self.table = self.create_table()
        self.plot = self.create_plot()

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.table)
        content_layout.addWidget(self.plot, stretch=1)

        layout.addLayout(content_layout)

    def initialize(self) -> None:
        self.load_data()
        self.update_data()

    def create_table(self) -> QTableView:
        table = QTableView(self)
        table.setMinimumWidth(490)
        font = table.font()
        font.setPointSize(AppConfig.FONT_SIZE)  # Increase font size
        table.setFont(font)
        return table

    # plot using plotly
    def create_plot(self) -> QWebEngineView:
        return QWebEngineView(self)

    def update_plot(self) -> None:
        if self.data is None:
            return

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data["Нет в реестре"],
                name="Нет в реестре",
                marker_color="rgb(220, 20, 60)",
                text=self.data["Нет в реестре"].apply(lambda x: f"{x:.0%}"),
                hovertemplate="%{x}<br>Нет в реестре: %{text}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data["Есть в реестре"],
                name="Есть в реестре",
                marker_color="rgb(34, 139, 34)",
                text=self.data["Есть в реестре"].apply(lambda x: f"{x:.0%}"),
                hovertemplate="%{x}<br>Есть в реестре: %{text}<extra></extra>",
            )
        )

        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data["(пусто)"],
                name="(пусто)",
                marker_color="rgb(200, 200, 200)",
                text=self.data["(пусто)"].apply(lambda x: f"{x:.0%}"),
                hovertemplate="%{x}<br>(пусто): %{text}<extra></extra>",
            )
        )

        # Update the layout
        fig.update_layout(
            title="Выполнение КПЭ по классам",
            xaxis={
                "title": "Классы",
                "tickangle": -45,
            },
            yaxis={
                "title": "Процент",
                "range": [0, 1.1],
                "showticklabels": False,  # Hide the tick labels
                "showgrid": False,  # Hide the grid
                "zeroline": False,  # Hide the zero line
            },
            barmode="stack",
            showlegend=True,
            legend={"title": "Наличие в реестре"},
            margin={"l": 40, "r": 40, "t": 40, "b": 120},
            plot_bgcolor="rgba(0,0,0,0)",
        )

        # Display the plot
        html = "<html><body>"
        html += plotly.offline.plot(fig, output_type="div", include_plotlyjs="cdn")
        html += "</body></html>"
        self.plot.setHtml(html)

    def set_table_model(self) -> None:
        if self.data is None:
            return
        self.table.setModel(None)
        model = PandasTableModel(self.data.map("{:.0%}".format), "Класс ИС ИМЗ")
        self.table.setModel(model)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for i in range(1, len(self.data.columns) + 1):
                self.table.setColumnWidth(i, 70)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
            header.setMinimumHeight(int(30 * 2))
            header.setMaximumSectionSize(250)
            header.setStyleSheet(
                "::section { background-color: #f0f0f0; border-width: 1px; border-style: solid; border-color: #b0b0b0 #b0b0b0 #b0b0b0 #f0f0f0; }"
                "::section::first { background-color: #f0f0f0; border-width: 1px; border-style: solid; border-color: #b0b0b0 #b0b0b0 #b0b0b0 #b0b0b0; }"
            )

        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def update_data(self) -> None:
        self.set_table_model()
        self.update_plot()

    def load_data(self) -> None:
        head_list = [
            "дата ввода в эксплуатацию",
            "ит-ландшафт / наименование",
            "инвентарный номер",
            "класс ис имз / наименование",
            "кпэ по классу в 2024",
            "краткое наименование",
            "наименование",
            "план импортозамещения",
            "Бюджет",
            "наличие в реестре мин связи российского по",
            "описание",
            "наличие имз ос",
            "наличие имз субд",
            "наличие имз виртуализации",
            "ответственный за развитие / фио",
            "приказ о вводе в эксплуатацию",
            "статус принадлежности к целевой архитектуре / наименование",
            "технический владелец / фио",
            "этап жц / наименование",
            "код класса",
        ]

        file_path: Path = Path(AppConfig.get_some_path("example_inputs/Системы_Задача2_.xlsx"))

        df: pd.DataFrame = parse_data(file_path=file_path, columns_list=head_list, sheet_name="Sheet0")
        data = (
            df[["Класс ИС ИМЗ / Наименование", "Наличие в реестре Мин связи российского ПО"]]
            .melt(id_vars="Класс ИС ИМЗ / Наименование")
            .fillna({"value": -1})
            .groupby(["Класс ИС ИМЗ / Наименование", "value"])
        )
        data = data.size()
        data = data.groupby(level=0).transform(lambda x: x / x.sum())
        data = data.unstack()  # noqa: PD010
        data = data.rename_axis(index=None, columns=None)
        data = data[[0.0, 1.0, -1.0]]
        data = data.rename(columns={-1.0: "(пусто)", 0.0: "Нет в реестре", 1.0: "Есть в реестре"})
        data = data.fillna(0)

        self.data = data

    def on_refresh_clicked(self) -> None:
        self.load_data()
        self.update_data()
