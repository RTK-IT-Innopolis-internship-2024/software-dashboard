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

    return data
