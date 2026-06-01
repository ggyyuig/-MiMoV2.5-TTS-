# MiMo V2.5 TTS Web 修复版

这个版本已修复 `Unknown voice: xiaomi-mimo-test` 问题。

## 已修复内容

- 默认请求地址：`https://api.xiaomimimo.com/v1`
- 默认模型：`mimo-v2.5-tts`
- 默认音色：`茉莉`
- 下拉框只保留接口返回支持的音色：
  - `mimo_default`
  - `冰糖`
  - `茉莉`
  - `苏打`
  - `白桦`
  - `Mia`
  - `Chloe`
  - `Milo`
  - `Dean`
- 前端可直接输入 MiMo API Token，不需要必须改 `.env`

## Windows PowerShell 启动命令

进入项目目录后执行：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web"

python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器打开：

```txt
http://127.0.0.1:8000
```

## 第二次启动

以后不用重复安装依赖，只需要：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web"

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 注意

不要双击 `index.html`。这个项目必须通过 FastAPI 后端打开，也就是访问：

```txt
http://127.0.0.1:8000
```
