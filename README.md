# MiMo TTS Web

一个基于 **Python FastAPI + HTML/CSS/JavaScript** 的小米 MiMo V2.5 TTS 网页应用。

项目支持在网页中输入文本，调用小米 MiMo 开放平台接口，将文字转换为语音音频。前端提供现代化玻璃拟态界面，后端作为 API 代理层，避免直接把请求逻辑写死在前端。

> 默认 API 地址：`https://api.xiaomimimo.com/v1`

---

## 项目预览

本项目主要功能：

- 文本转语音 TTS
- 支持网页端填写 MiMo API Key
- 支持 Bearer Token / api-key 两种认证方式
- 支持音色选择
- 支持语速调节
- 支持音量调节
- 支持 MP3 / WAV 输出
- 支持在线播放生成音频
- 支持下载音频文件
- FastAPI 后端代理请求，前端不需要直接写死接口逻辑
- 支持 Windows 本地运行
- 支持手机浏览器访问电脑后端
- 支持安卓 Termux 本机运行

---

## 技术栈

### 前端

- HTML5
- CSS3
- JavaScript ES6+
- TailwindCSS CDN
- Glassmorphism 玻璃拟态 UI

### 后端

- Python 3.10+
- FastAPI
- Uvicorn
- HTTPX
- Pydantic Settings

### 部署

- Docker
- 本地 Python 环境
- 安卓 Termux 可运行

---

## 项目结构

```txt
mimo-tts-web/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       └── tts.py
│   ├── controllers/
│   │   └── tts_controller.py
│   ├── services/
│   │   └── mimo_service.py
│   ├── schemas/
│   │   └── tts.py
│   ├── core/
│   │   └── config.py
│   └── static/
│       └── index.html
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 支持音色

根据 MiMo API 返回，目前可用音色包括：

```txt
mimo_default
冰糖
茉莉
苏打
白桦
Mia
Chloe
Milo
Dean
```

默认音色为：

```txt
茉莉
```

如果接口返回 `Unknown voice`，请检查前端下拉框的 `value` 是否和官方返回的音色名称完全一致。

---

## Windows 本地运行

### 1. 解压项目

例如解压到：

```txt
C:\Users\21642\Desktop\mimo-tts-web
```

### 2. 打开 PowerShell

进入项目目录：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web"
```

如果你解压后出现双层目录，例如：

```txt
C:\Users\21642\Desktop\mimo-tts-web\mimo-tts-web
```

那就进入里面那层：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web\mimo-tts-web"
```

可以用下面命令检查是否进入正确目录：

```powershell
dir
```

当前目录里应该能看到：

```txt
app
requirements.txt
Dockerfile
```

---

### 3. 创建虚拟环境

```powershell
python -m venv .venv
```

如果 `python` 命令不可用，可以尝试：

```powershell
py -m venv .venv
```

---

### 4. 激活虚拟环境

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

---

### 5. 安装依赖

```powershell
python -m pip install --upgrade pip

pip install -r requirements.txt
```

如果安装慢，可以使用国内镜像：

```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

---

### 6. 启动服务

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，电脑浏览器打开：

```txt
http://127.0.0.1:8000
```

---

## 下次启动

如果已经安装过依赖，下次只需要：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web"

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

然后打开：

```txt
http://127.0.0.1:8000
```

---

## 手机访问电脑后端

如果想在手机浏览器上使用，需要电脑和手机连接同一个 WiFi。

### 1. 电脑启动后端

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

注意必须是：

```txt
--host 0.0.0.0
```

不能只监听 `127.0.0.1`。

---

### 2. 查询电脑 IP

在 PowerShell 输入：

```powershell
ipconfig
```

找到类似：

```txt
IPv4 地址 . . . . . . . . . . . . : 192.168.1.8
```

---

### 3. 手机浏览器访问

假设电脑 IP 是：

```txt
192.168.1.8
```

那么手机打开：

```txt
http://192.168.1.8:8000
```

不要在手机上打开：

```txt
http://127.0.0.1:8000
```

因为手机上的 `127.0.0.1` 指的是手机自己，不是电脑。

---

## 安卓 Termux 本机运行

如果想在安卓手机本机运行，可以使用：

- Acode 编辑代码
- Termux 运行 Python 后端
- 手机浏览器打开网页

### 1. 安装 Termux

建议从 F-Droid 下载新版 Termux。

### 2. 给 Termux 存储权限

```bash
termux-setup-storage
```

### 3. 安装 Python

```bash
pkg update
pkg install python
```

### 4. 进入项目目录

假设项目解压到了下载目录：

```bash
cd /storage/emulated/0/Download/mimo-tts-web
```

如果是双层目录：

```bash
cd /storage/emulated/0/Download/mimo-tts-web/mimo-tts-web
```

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

如果安装慢：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 6. 启动后端

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

然后手机浏览器打开：

```txt
http://127.0.0.1:8000
```

---

## Docker 运行

```bash
docker build -t mimo-tts-web .

docker run --rm -p 8000:8000 mimo-tts-web
```

然后打开：

```txt
http://127.0.0.1:8000
```

---

## API Key 使用说明

本项目支持两种方式：

### 方式一：网页中填写 API Key

打开网页后，在右侧 API Key 输入框中填写你的 MiMo API Key。

可以选择：

```txt
Bearer Token
api-key 请求头
```

如果使用 `Bearer Token` 报 401，可以切换到 `api-key 请求头` 再试。

---

### 方式二：使用 .env 文件

复制示例文件：

```bash
cp .env.example .env
```

Windows PowerShell 可以使用：

```powershell
copy .env.example .env
```

然后修改 `.env`：

```env
MIMO_API_KEY=your_mimo_api_key_here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_ENDPOINT_PATH=/chat/completions
MIMO_MODEL=mimo-v2.5-tts
MIMO_AUTH_TYPE=bearer
```

---

## curl 测试后端接口

Windows PowerShell：

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/tts" `
  -H "Content-Type: application/json" `
  -d '{"text":"你好，这是 MiMo 语音合成测试。","voice":"茉莉","speed":1.0,"volume":80,"response_format":"mp3"}' `
  --output output.mp3
```

如果前端 API Key 输入框没有传入密钥，则后端会尝试读取 `.env` 中的 `MIMO_API_KEY`。

---

## 常见问题

### 1. Failed to fetch

一般是前端没有连接到后端。

检查：

- 是否直接双击了 `index.html`
- 是否启动了 FastAPI 后端
- 访问地址是否是 `http://127.0.0.1:8000`
- 手机上是否使用了电脑局域网 IP

正确方式：

```txt
先启动后端，再打开 http://127.0.0.1:8000
```

---

### 2. 无法识别 Activate.ps1

说明当前目录里没有 `.venv`，或者没有进入正确项目目录。

先执行：

```powershell
dir
```

确认当前目录里有：

```txt
app
requirements.txt
```

然后创建虚拟环境：

```powershell
python -m venv .venv
```

再激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 3. Unknown voice

如果出现：

```txt
Unknown voice
```

请使用支持的音色：

```txt
mimo_default
冰糖
茉莉
苏打
白桦
Mia
Chloe
Milo
Dean
```

不要使用：

```txt
xiaomi-mimo-test
moli
bingtang
soda
baihua
```

---

### 4. 401 鉴权失败

可能原因：

- API Key 填错
- 认证方式选错
- 当前 Token 没有模型权限

可以在网页里切换：

```txt
Bearer Token
api-key 请求头
```

---

### 5. 429 限速或额度不足

说明请求太频繁，或者 Token Plan 额度不足。

可以稍后重试，或者检查 MiMo 控制台额度。

---

### 6. 手机访问不到电脑

可能原因：

- 手机和电脑不在同一个 WiFi
- 校园网开启了设备隔离
- Windows 防火墙拦截了 8000 端口
- 启动后端时没有使用 `--host 0.0.0.0`

可以尝试管理员 PowerShell 放行端口：

```powershell
New-NetFirewallRule -DisplayName "MiMo TTS Web 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## 安全提醒

请不要把自己的 API Key 提交到 GitHub。

建议：

- `.env` 加入 `.gitignore`
- GitHub 仓库不要上传真实 Token
- README 中只写 `.env.example`
- 前端“记住 API Key”只适合个人本机使用，不建议在公共电脑使用

---

## .gitignore 建议

```gitignore
.venv/
__pycache__/
*.pyc
.env
.DS_Store
start-log.txt
output.mp3
output.wav
```

---

## License

MIT License

---

## 说明

本项目仅用于学习和个人开发测试。MiMo API 的具体模型名称、接口路径、鉴权方式和可用音色可能会随官方更新而变化，请以小米 MiMo 开放平台实际文档和接口返回为准。
