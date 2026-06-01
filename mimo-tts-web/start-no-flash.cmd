@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: 不要让窗口闪退；所有错误都会写入 start-log.txt，并在结尾 pause。
chcp 936 >nul 2>nul
title MiMo TTS Web - No Flash Start
cd /d "%~dp0"

set "LOG=%CD%\start-log.txt"
echo ======================================== > "%LOG%"
echo MiMo TTS Web 启动日志 >> "%LOG%"
echo Time: %date% %time% >> "%LOG%"
echo Path: %CD% >> "%LOG%"
echo ======================================== >> "%LOG%"
echo. >> "%LOG%"

echo ========================================
echo MiMo TTS Web 启动器 - 不闪退版
echo ========================================
echo 当前目录：%CD%
echo 日志文件：%LOG%
echo.

call :MAIN
set "CODE=%ERRORLEVEL%"

echo.
echo ========================================
if "%CODE%"=="0" (
    echo 服务已停止。
) else (
    echo 启动失败，错误码：%CODE%
    echo 请把下面这个日志文件里的内容发给我：
    echo %LOG%
)
echo ========================================
echo.
echo 按任意键关闭窗口...
pause >nul
exit /b %CODE%

:MAIN
if not exist "requirements.txt" (
    echo [错误] 当前目录不是项目根目录，找不到 requirements.txt。
    echo [错误] 当前目录不是项目根目录，找不到 requirements.txt。 >> "%LOG%"
    exit /b 10
)

set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo [错误] 没有找到 Python。
    echo 请先安装 Python 3.10 或更高版本，并勾选 Add Python to PATH。
    echo 下载地址：https://www.python.org/downloads/
    echo [错误] 没有找到 Python。 >> "%LOG%"
    exit /b 11
)

echo [1/5] 检测 Python...
echo PY_CMD=%PY_CMD% >> "%LOG%"
%PY_CMD% --version
%PY_CMD% --version >> "%LOG%" 2>&1
if errorlevel 1 (
    echo [错误] Python 可执行但版本检测失败。
    echo [错误] Python 可执行但版本检测失败。 >> "%LOG%"
    exit /b 12
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [2/5] 正在创建虚拟环境 .venv ...
    echo [2/5] 正在创建虚拟环境 .venv ... >> "%LOG%"
    %PY_CMD% -m venv .venv >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败。
        echo 可能原因：Python 安装不完整，或没有 venv 模块。
        exit /b 13
    )
) else (
    echo.
    echo [2/5] 已检测到虚拟环境 .venv
    echo [2/5] 已检测到虚拟环境 .venv >> "%LOG%"
)

set "VPY=%CD%\.venv\Scripts\python.exe"
if not exist "%VPY%" (
    echo [错误] 找不到虚拟环境 Python：%VPY%
    echo [错误] 找不到虚拟环境 Python：%VPY% >> "%LOG%"
    exit /b 14
)

echo.
echo [3/5] 正在升级 pip...
echo [3/5] 正在升级 pip... >> "%LOG%"
"%VPY%" -m pip install --upgrade pip >> "%LOG%" 2>&1
if errorlevel 1 (
    echo [警告] pip 升级失败，继续尝试安装依赖。
    echo [警告] pip 升级失败，继续尝试安装依赖。 >> "%LOG%"
)

echo.
echo [4/5] 正在安装依赖...
echo 如果这里很慢，可以等一会儿；失败原因会写进 start-log.txt。
echo [4/5] 正在安装依赖... >> "%LOG%"
"%VPY%" -m pip install -r requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (
    echo [错误] 依赖安装失败，正在尝试使用清华源重试...
    echo [错误] 依赖安装失败，正在尝试使用清华源重试... >> "%LOG%"
    "%VPY%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [错误] 依赖安装仍然失败。
        echo 你可以打开 start-log.txt 查看具体报错。
        exit /b 15
    )
)

echo.
echo [5/5] 正在启动后端服务...
echo.
echo 浏览器会打开：http://127.0.0.1:8000
echo 请不要关闭这个窗口，关闭后网页就不能用了。
echo.
echo [5/5] 正在启动后端服务... >> "%LOG%"
start "" "http://127.0.0.1:8000"
"%VPY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "%LOG%" 2>&1
exit /b %ERRORLEVEL%
