# Market VIX Dashboard

## Installation & Setup

First clone the repository:

```bash
git clone https://github.com/Huang-Yongzhi/market_vix.git
cd market_vix
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

## Windows 环境快速入门

### 方案 A – CMD / PowerShell
```bat
:: 1. 进入项目目录
cd C:\path\to\market_vix

:: 2. 创建虚拟环境
python -m venv venv

:: 3. 激活
venv\Scripts\activate.bat   :: CMD
venv\Scripts\Activate.ps1   :: PowerShell

:: 4. 安装依赖
pip install -r requirements.txt

:: 5. 运行 / 测试
pytest -q
python app.py
```

### 方案 B – VS Code
```powershell
# 终端创建并激活
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖 & 运行
pip install -r requirements.txt
pytest -q
python app.py
```

- Ctrl+Shift+P → Python: Select Interpreter 选择 .venv

## Running

```bash
python app.py
```

## Screenshot

![dashboard screenshot](docs/screenshot.png)

## Indicator Explanation

The app computes the VIX term structure slope using the first and third futures
contracts: `(v1 - v3) / v3`. Positive values indicate a steeper front end and
can signal increased market stress.

