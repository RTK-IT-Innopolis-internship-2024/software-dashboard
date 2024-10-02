![windows](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/windows-build.yml/badge.svg?branch=main)
![ubuntu](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/ubuntu-build.yml/badge.svg?branch=main)
![macos](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/macos-build.yml/badge.svg?branch=main)

![GitHub Last Commit](https://img.shields.io/github/last-commit/RTK-IT-Innopolis-internship-2024/software-dashboard)
![GitHub Releases](https://img.shields.io/github/v/release/RTK-IT-Innopolis-internship-2024/software-dashboard)
![Release Date](https://img.shields.io/github/release-date/RTK-IT-Innopolis-internship-2024/software-dashboard?style=flat&label=Release%20Date&format=%25d.%25m.%25Y)

# 1. Инструкция для пользователя:

## Инструкция по установке

1. Перейдите в раздел [Releases](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/releases/latest) и выбирите самый новый релиз.
2. Скачайте архив с приложением для вашей платформы. Например, для Windows [Apps-dashboard-windows-latest.zip](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/releases/latest/download/Apps-dashboard-windows-latest.zip).
3. Распакуйте папку `Apps-dashboard-<your_platform_name>-latest` из архива в любое место.

    **Важно:** Файлы внутри папки должны оставаться в отдельной папке для корректной работы.

4. Перейдите в папку `Apps-dashboard-<your_platform_name>-latest` и запустите приложение.
5. Выбирите `.xlsx` файл с данными.

## Инструкция по использованию

https://github.com/user-attachments/assets/299889e6-c6b9-4802-971a-bd1c02997e4b

# 2. Instructions for developers:

In this project, Python 3.11 was used.

## 2.1. Main instruction with uv tool (recommended)

In this project UV Project Manager was used, check its [documentation](https://docs.astral.sh/uv) and [source code](https://github.com/astral-sh/uv).

### Install uv

```
# On macOS and Linux.
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
$ powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip.
$ pip install uv
```

See the [installation documentation](https://docs.astral.sh/uv/getting-started/installation/) for details and alternative installation methods.

### Install and activate venv by [sync command](https://docs.astral.sh/uv/reference/cli/#uv-sync)

Install venv and sync dependencies

```shell
uv sync
```

Activate venv

```
# На Windows:
$ .venv\Scripts\activate

# На macOS и Linux:
$ source .venv/bin/activate
```

### Set up the git hook scripts by [pre-commit](https://pre-commit.com/#3-install-the-git-hook-scripts)

```shell
pre-commit install
```

### Open `./src` or `main.py` and just code it

### Open your app

```shell
uv run main.py
```

## 2.2. Alternative instruction with pip tool (not recommended)

### [Install python 3.11](https://docs.python.org/3.11/using/index.html)

### Install pip by this [documentation](https://pip.pypa.io/en/stable/installation/)

### Install venv

Create venv

```shell
python -m venv .venv
```

Activate venv

```
# На Windows:
$ .venv\Scripts\activate

# На macOS и Linux:
$ source .venv/bin/activate
```

After that install dependencies

```shell
pip install .
```

### Set up the git hook scripts by [pre-commit](https://pre-commit.com/#3-install-the-git-hook-scripts)

```shell
pre-commit install
```

### Open `./src` or `main.py` and just code it

### Open your app

```shell
python main.py
```
