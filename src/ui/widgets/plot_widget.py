import pandas as pd
import plotly.graph_objects as go
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget

from src.utils import utils
from src.utils.config import AppConfig


class PlotWidget(QWebEngineView):
    plot_updated = pyqtSignal(str, bool)

    def __init__(
        self,
        parent: QWidget | None = None,
        name: str = "registry",
        colors: list[str] | None = None,
        tick_font_size: int = 15,
        legend_font_size: int = 12,
        title_font_size: int = 18,
        hover_font_size: int = 16,
        text_info_font_size: int = 12,
        title_template: str = "Выполнение КПЭ по классам",
        x_axis_title: str = "Классы",
        y_axis_title: str = "Процент",
        column_names: list[str] | None = None,
        truncate_len: int = 30,
        singular_title_template: str = 'Выполнение КПЭ по классу "{class_name}"',
        legend_title: str = "Наличие в реестре",
        margins: dict[str, int] | None = None,
        background_color: str = "rgba(0,0,0,0)",
        min_width: int = 1000,
        min_height: int = 600,
    ) -> None:
        super().__init__(parent=parent)

        # Customizable properties
        self.name: str = name
        self.colors: list[str] = colors or ["rgb(220, 20, 60)", "rgb(34, 139, 34)", "rgb(200, 200, 200)"]
        self.tick_font_size: int = tick_font_size
        self.legend_font_size: int = legend_font_size
        self.title_font_size: int = title_font_size
        self.hover_font_size: int = hover_font_size
        self.text_info_font_size: int = text_info_font_size
        self.title_template: str = title_template
        self.singular_title_template: str = singular_title_template
        self.x_axis_title: str = x_axis_title
        self.y_axis_title: str = y_axis_title
        self.truncate_len: int = truncate_len
        self.legend_title: str = legend_title
        self.margins: dict[str, int] = margins or {"l": 40, "r": 40, "t": 40, "b": 120}
        self.background_color: str = background_color
        self.min_width: int = min_width
        self.min_height: int = min_height

        # Data column names (default)
        self.column_names: list[str] = column_names or ["Нет в реестре", "Есть в реестре", "(пусто)"]

        # Set minimum size of widget
        self.setMinimumWidth(self.min_width)
        self.setMinimumHeight(self.min_height)

    @classmethod
    def from_config(
        cls,
        name: str,
        title_template: str,
        x_axis_title: str,
        y_axis_title: str,
        column_names: list[str],
        singular_title_template: str,
        legend_title: str,
        parent: QWidget | None = None,
    ) -> "PlotWidget":
        """Alternative constructor that pulls default values from a config"""
        return cls(
            parent=parent,
            name=name,
            colors=[AppConfig.get_param("plot_red_color"), AppConfig.get_param("plot_green_color"), AppConfig.get_param("plot_gray_color")],
            tick_font_size=AppConfig.get_param("plot_tick_font_size"),
            legend_font_size=AppConfig.get_param("plot_legend_font_size"),
            title_font_size=AppConfig.get_param("plot_title_font_size"),
            hover_font_size=AppConfig.get_param("plot_hover_font_size"),
            text_info_font_size=AppConfig.get_param("plot_text_info_font_size"),
            title_template=title_template,
            x_axis_title=x_axis_title,
            y_axis_title=y_axis_title,
            column_names=column_names,
            truncate_len=AppConfig.get_param("plot_truncate_len"),
            singular_title_template=singular_title_template,
            legend_title=legend_title,
            margins=AppConfig.PLOT_MARGINS,
            background_color=AppConfig.get_param("plot_background_color"),
            min_width=AppConfig.get_param("plot_min_width"),
            min_height=AppConfig.get_param("plot_min_height"),
        )

    def reset_config(self) -> None:
        self.colors = [AppConfig.get_param("plot_red_color"), AppConfig.get_param("plot_green_color"), AppConfig.get_param("plot_gray_color")]
        self.tick_font_size = AppConfig.get_param("plot_tick_font_size")
        self.legend_font_size = AppConfig.get_param("plot_legend_font_size")
        self.title_font_size = AppConfig.get_param("plot_title_font_size")
        self.hover_font_size = AppConfig.get_param("plot_hover_font_size")
        self.text_info_font_size = AppConfig.get_param("plot_text_info_font_size")
        self.truncate_len = AppConfig.get_param("plot_truncate_len")
        self.margins = AppConfig.PLOT_MARGINS
        self.background_color = AppConfig.get_param("plot_background_color")
        self.min_width = AppConfig.get_param("plot_min_width")
        self.min_height = AppConfig.get_param("plot_min_height")

    def make_plot(self, data: pd.DataFrame, mask: pd.Series, width: int | None = None, height: int | None = None) -> tuple[go.Figure, bool]:
        """Updates the plot based on the data and the provided mask."""
        if data is None:
            return None, False

        filtered_data: pd.DataFrame = data[mask]
        truncated_index: pd.Series = filtered_data.index.to_series().apply(lambda x: x[: self.truncate_len] + "..." if len(x) > self.truncate_len else x)

        fig: go.Figure = go.Figure()
        is_pie = False

        # Handle case where there's no data
        if len(filtered_data) == 0:
            is_pie = True
            fig.add_annotation(text="Нет данных", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font={"size": 20}, align="center")
            fig.update_layout(
                showlegend=False,
                xaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
                yaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
                margin=self.margins,
                plot_bgcolor=self.background_color,
            )
        # Handle case where there's only one row
        elif len(filtered_data) == 1:
            is_pie = True
            class_name: str = filtered_data.index[0]
            pie_labels: list[str] = []
            pie_values: list[float] = []
            pie_colors: list[str] = []

            for idx, name in enumerate(self.column_names):
                filtered_data_value = filtered_data[name].to_list()[0]
                if filtered_data_value != 0:
                    pie_labels.append(name)
                    pie_values.append(filtered_data_value)
                    pie_colors.append(self.colors[idx])

            # Add pie chart trace
            fig.add_trace(
                go.Pie(
                    labels=pie_labels,
                    values=pie_values,
                    text=[f"{x:.1%}" for x in pie_values],
                    textinfo="label+text",
                    hoverinfo="label+text",
                    textfont={"size": self.tick_font_size},
                    hoverlabel={"font": {"size": self.hover_font_size}},
                    marker={"colors": pie_colors},
                )
            )

            # Update layout for pie chart
            fig.update_layout(
                title=self.singular_title_template.format(x=class_name),
                title_font_size=self.title_font_size,
                showlegend=True,
                legend={"title": self.legend_title, "font": {"size": self.legend_font_size}},
                margin=self.margins,
                plot_bgcolor=self.background_color,
            )
        else:
            for idx, name in enumerate(self.column_names):
                fig.add_trace(
                    go.Bar(
                        x=filtered_data.index,
                        y=filtered_data[name],
                        name=name,
                        marker_color=self.colors[idx],
                        text=filtered_data[name].apply(lambda x: f"{x:.0%}"),
                        hovertemplate="%{customdata}<br>" + name + ": %{text}<extra></extra>",
                        hoverlabel={"font": {"size": self.hover_font_size}},
                        textfont={"size": self.text_info_font_size},
                        customdata=filtered_data.index,
                    )
                )

            # Update layout for bar chart
            fig.update_layout(
                title=self.title_template,
                title_font_size=self.title_font_size,
                xaxis={
                    "title": self.x_axis_title,
                    "tickangle": -45,
                    "tickmode": "array",
                    "ticktext": truncated_index,
                    "tickvals": filtered_data.index,
                    "tickfont": {"size": self.tick_font_size},
                },
                yaxis={
                    "title": self.y_axis_title,
                    "range": [0, 1.1],
                    "showticklabels": False,  # Hide the tick labels
                    "showgrid": False,  # Hide the grid
                    "zeroline": False,  # Hide the zero line
                },
                barmode="stack",
                showlegend=True,
                legend={"title": self.legend_title, "font": {"size": self.legend_font_size}},
                margin=self.margins,
                plot_bgcolor=self.background_color,
                width=width,
                height=height,
            )

        return fig, is_pie

    def update_plot(self, data: pd.DataFrame, mask: pd.Series) -> None:
        """Updates the plot based on the data and the provided mask."""
        if data is None:
            return

        fig, is_pie = self.make_plot(data, mask)

        # Save plot and load it in the widget
        file: str = utils.create_plotly_plot(fig, self.name)
        self.plot_updated.emit(file, is_pie)
        self.load(QUrl.fromLocalFile(file))

    def export_plot(self, data: pd.DataFrame, mask: pd.Series, file_path: str) -> None:
        if data is None:
            return

        fig, _ = self.make_plot(data, mask, width=AppConfig.get_param("export_plot_width"), height=AppConfig.get_param("export_plot_height"))

        # Save plot and load it in the widget
        utils.export_plotly_plot(fig, file_path)
