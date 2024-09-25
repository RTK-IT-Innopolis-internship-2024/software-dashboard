![multiplatform build](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/multiplatform-build.yml/badge.svg?branch=main)

![windows](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/windows-build.yml/badge.svg?branch=main)
![ubuntu](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/ubuntu-build.yml/badge.svg?branch=main)
![macos](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/macos-build.yml/badge.svg?branch=main)

# 1. Инструкция для пользователя:

## Релиз приложения состоит из архива со следующим содержимым:

├── 📁 Apps-Purchases-<your_platform_name>-latest/  
│   └── 🖥️ Apps-Purchases-<your_platform_name>-latest.exe  

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

### Install venv by [sync command](https://docs.astral.sh/uv/reference/cli/#uv-sync)

```shell
uv sync
```

### Use created venv for next commands

### Set up the git hook scripts by [pre-commit](https://pre-commit.com/#3-install-the-git-hook-scripts)

```shell
pre-commit install
```

### Open `./src` or `main.py` and just code it

### Open your app

```shell
uv run main.py
```
