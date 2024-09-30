from pathlib import Path

import pandas as pd


def parse_data(file_path: Path, columns_list: list, sheet_name: str = "Sheet0") -> pd.DataFrame:
    required_columns = [col.strip().lower() for col in columns_list]

    data = pd.read_excel(file_path, sheet_name=sheet_name)

    current_columns = data.columns.str.strip().str.lower()

    missing_columns = [columns_list[index] for index, col in enumerate(required_columns) if col not in current_columns]
    extra_columns = [col for col in current_columns if col not in required_columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    data = data.drop(columns=extra_columns)
    data.columns = [col.strip() for col in data.columns]

    return data.fillna(
        {
            "Класс ИС ИМЗ / Наименование": "(пусто)",
            "Статус принадлежности к целевой архитектуре / Наименование": "(пусто)",
            "Этап ЖЦ / Наименование": "(пусто)",
        }
    )


def parse_data_sheet0(file_path: Path) -> pd.DataFrame:
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

    return parse_data(file_path=file_path, columns_list=head_list, sheet_name="Sheet0")
