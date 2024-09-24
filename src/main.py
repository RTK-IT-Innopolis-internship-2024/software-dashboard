from pathlib import Path

import pandas as pd

from src.backend.controllers.dashboard_controller import parse_data
# from src import app
from src.utils.config import AppConfig


def test():
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
        "код класса"
    ]

    file_path: Path = Path(AppConfig.get_some_path("example_inputs/Системы_Задача2_.xlsx"))

    df: pd.DataFrame = parse_data(file_path=file_path, columns_list=head_list, sheet_name="Sheet0")


if __name__ == "__main__":
    test()

    # your code
    # app.run()
