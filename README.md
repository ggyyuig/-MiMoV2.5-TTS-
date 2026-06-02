# MiMo TTS Web

一个基于 **小米 MiMo V2.5 TTS** 的本地网页语音合成工具。

项目使用：

* 前端：HTML / CSS / JavaScript
* 后端：Python + FastAPI
* 接口：小米 MiMo V2.5 TTS API

后端作为代理层负责调用 MiMo API，前端不会直接暴露 API Key。

---

## 功能介绍

本项目支持：

* 文本转语音
* MiMo 官方预置音色
* 文本描述生成音色
* 上传音频进行声音复刻
* WAV / MP3 格式选择
* 本地网页界面操作
* 后端代理保护 API Key

推荐首次测试使用：

* 模式：预置音色
* 音色：茉莉
* 格式：WAV

---

## 项目结构

```txt
mimo-tts-web/
├─ app/
│  ├─ main.py              # FastAPI 主入口
│  ├─ api/                 # 后端接口路由
│  ├─ services/            # MiMo API 调用逻辑
│  ├─ schemas/             # 请求数据结构
│  └─ static/              # 前端页面文件
├─ requirements.txt        # Python 依赖
├─ README.md               # 项目说明
└─ .env                    # API Key 配置文件，需要自己创建
```

---

## 运行前准备

你需要先安装：

* Python 3.10 或更高版本
* 可以访问 MiMo API 的网络环境
* 小米 MiMo API Key

检查 Python 是否安装成功：

```powershell
python --version
```

如果能看到类似下面的内容，说明 Python 正常：

```txt
Python 3.10.x
```

---

## 配置 API Key

在项目根目录新建一个文件，名字必须是：

```txt
.env
```

然后写入：

```env
MIMO_API_KEY=你的MiMo_API_Key
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
```

示例：

```env
MIMO_API_KEY=sk-xxxxxxxxxxxxxxxx
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
```

注意：

* `.env` 文件不要上传到 GitHub
* API Key 不要发给别人
* `MIMO_API_KEY=` 后面不要加中文引号
* 不要多加空格

---

## 第一次运行

进入项目文件夹，也就是能看到 `app` 和 `requirements.txt` 的那个目录。

在文件夹空白处右键，选择：

```txt
在终端中打开
```

然后复制下面这一整段命令运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
if (!(Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，浏览器打开：

```txt
http://127.0.0.1:8000
```

终端窗口不要关闭，关闭后网页服务也会停止。

---

## 第二次以及以后运行

以后已经安装过依赖了，就不用再重新安装。

还是在项目文件夹里右键打开终端，然后运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

然后浏览器打开：

```txt
http://127.0.0.1:8000
```

---

## 如果你不在项目文件夹里

如果终端不是在项目目录打开的，需要先 `cd` 到项目目录。

例如你的项目放在：

```txt
D:\mimo-tts-web-fixed
```

那就运行：

```powershell
cd "D:\mimo-tts-web-fixed"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

重点：
必须进入到包含下面这些内容的目录：

```txt
app
requirements.txt
README.md
```

否则会启动失败。

---

## 使用方法

打开网页后：

1. 输入要合成的文字
2. 选择语音模式
3. 选择音色
4. 选择输出格式
5. 点击生成语音
6. 等待生成完成
7. 播放或下载生成的音频

---

## 语音模式说明

### 1. 预置音色

使用 MiMo 官方提供的固定音色。

常见音色包括：

```txt
冰糖
茉莉
苏打
白桦
Mia
Chloe
Milo
Dean
```

推荐先用：

```txt
茉莉
```

测试接口是否正常。

---

### 2. 文本音色设计

通过文字描述生成指定风格的声音。

例如：

```txt
年轻男性，声音干净，语速适中，情绪自然，适合旁白。
```

或者：

```txt
温柔女声，语气亲切，声音清晰，适合有声书朗读。
```

---

### 3. 声音复刻

上传一段音频样本，让模型根据样本生成相似音色。

建议音频满足：

* WAV 或 MP3 格式
* 声音清晰
* 背景噪音少
* 只有一个人说话
* 不要太长
* 不要带音乐背景

如果复刻失败，可以换一段更短、更清晰的音频重新测试。

---

## 推荐测试流程

第一次运行建议这样测试：

1. 模式选择：预置音色
2. 音色选择：茉莉
3. 格式选择：WAV
4. 文本输入：

```txt
你好，这是一次小米 MiMo 语音合成测试。
```

如果这个能正常生成，说明：

* API Key 没问题
* 后端启动没问题
* MiMo 接口调用没问题

然后再测试文本音色设计和声音复刻。

---

## 常见问题

### 1. 运行后提示找不到 Python

说明 Python 没装好，或者没有加入环境变量。

解决方法：

1. 重新安装 Python
2. 安装时勾选 `Add Python to PATH`
3. 重新打开终端
4. 再运行启动命令

---

### 2. PowerShell 提示禁止运行脚本

先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

这个设置只对当前终端窗口生效，不会永久修改系统设置。

---

### 3. 提示找不到 requirements.txt

说明你没有进入项目根目录。

请确认当前目录里有：

```txt
requirements.txt
app
```

如果没有，就先 `cd` 到项目目录。

---

### 4. 提示 No module named uvicorn

说明依赖没有安装成功。

重新运行：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

然后再启动：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 5. 网页打不开

先检查终端里有没有启动成功。

正常启动后，一般会看到类似：

```txt
Uvicorn running on http://0.0.0.0:8000
```

然后浏览器打开：

```txt
http://127.0.0.1:8000
```

注意不是打开 `0.0.0.0:8000`，本机浏览器建议打开 `127.0.0.1:8000`。

---

### 6. 端口 8000 被占用

如果提示端口被占用，可以换成 8010：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

然后浏览器打开：

```txt
http://127.0.0.1:8010
```

---

### 7. 生成语音失败

优先检查：

* `.env` 文件是否存在
* `MIMO_API_KEY` 是否正确
* 网络是否能访问 MiMo API
* 音色名称是否正确
* 格式是否选择 WAV
* 文本是否过长

建议先用：

```txt
预置音色 + 茉莉 + WAV
```

测试。

---

### 8. 声音复刻失败

可能原因：

* 音频太大
* 音频格式不规范
* 音频里面有多人声音
* 背景噪音太大
* 音频不是纯人声
* 音频时长太短或太乱

建议换一段安静环境下录制的单人语音。

---

## 重要提醒

不要把 API Key 写进前端代码里。

正确做法是写在 `.env` 里：

```env
MIMO_API_KEY=你的MiMo_API_Key
```

前端只请求本地后端，后端再去请求 MiMo API。

这样可以避免 API Key 暴露。

---

## 开发说明

本项目的基本调用流程是：

```txt
浏览器前端
    ↓
本地 FastAPI 后端
    ↓
MiMo API
    ↓
返回音频
    ↓
网页播放或下载
```

这样设计的好处：

* API Key 不暴露给浏览器
* 调用逻辑更安全
* 后续可以增加登录、限流、错误日志
* 方便部署到服务器

---

## 一句话启动总结

第一次运行用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
if (!(Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

以后运行用：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

浏览器打开：

```txt
http://127.0.0.1:8000
```

---

## 许可证

本项目仅供学习、测试和个人使用。
使用 MiMo API 时，请遵守小米 MiMo 平台的相关服务条款。
