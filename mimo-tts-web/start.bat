@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo MiMo TTS Web 一键启动
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [错误] 没有找到 Python。
  echo 请先安装 Python 3.10 或更高版本，并勾选 Add Python to PATH。
  echo 下载地址：https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] 正在创建虚拟环境 .venv ...
  python -m venv .venv
  if errorlevel 1 (
    echo [错误] 创建虚拟环境失败。
    pause
    exit /b 1
  )
) else (
  echo [1/4] 已检测到虚拟环境 .venv
)

echo [2/4] 正在启用虚拟环境 ...
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [错误] 启用虚拟环境失败。
  pause
  exit /b 1
)

echo [3/4] 正在安装 / 检查依赖 ...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo [错误] 依赖安装失败，请检查网络或 pip 源。
  pause
  exit /b 1
)

echo [4/4] 正在启动后端服务 ...
echo.
echo 浏览器会自动打开：http://127.0.0.1:8000
echo 请不要关闭这个黑色窗口，关闭后网页就不能用了。
echo.
start http://127.0.0.1:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 服务已停止。
pause
