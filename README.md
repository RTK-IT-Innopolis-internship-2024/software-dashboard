![multiplatform build](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/multiplatform-build.yml/badge.svg?branch=main)

![windows](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/windows-build.yml/badge.svg?branch=main)
![ubuntu](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/ubuntu-build.yml/badge.svg?branch=main)
![macos](https://github.com/RTK-IT-Innopolis-internship-2024/software-dashboard/actions/workflows/macos-build.yml/badge.svg?branch=main)

### Инструкция для пользователя:

#### Релиз приложения состоит из архива со следующим содержимым:

├── 📁 Apps-Purchases-<your_platform_name>-latest/  
│   └── 🖥️ Apps-Purchases-<your_platform_name>-latest.exe  

### Instruction for developers:

#### Install uv
```shell
irm https://astral.sh/uv/install.ps1 | iex
```

#### Install venv
```shell
uv sync
```

#### Install pre-commit hooks
```shell
pre-commit install
```

#### Open ./src and just code it

#### Open your app
```shell
uv run main.py
```