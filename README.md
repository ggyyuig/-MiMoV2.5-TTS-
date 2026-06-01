# MiMo V2.5 TTS Studio

一个基于 **FastAPI + 原生 HTML/CSS/JavaScript** 的小米 MiMo V2.5 TTS 网页应用。

项目支持：

- 输入文本生成语音
- 选择 MiMo 内置音色
- 在网页中填写 API Token，不需要写死到代码里
- 上传音频或直接录音，作为临时复刻音色使用
- 生成后在线播放与下载音频
- Windows、Docker、安卓 Termux 运行

> 注意：本项目是本地代理工具。请不要把真实 API Token 提交到 GitHub。

---

## 界面说明

新版界面分成 4 个清晰区域：

1. **连接 MiMo API**：填写 Token，选择认证方式。
2. **生成语音**：输入文本，选择音色、语速、音量、输出格式。
3. **复刻声音 / 自定义音色**：上传音频或录音，保存为本地复刻音色。
4. **播放与下载**：生成成功后播放或下载音频。

复刻音色不会再调用不存在的 `/voices/add` 接口。项目会在生成语音时直接使用 VoiceClone 模型，把音频样本作为 `audio.voice` 发送给 MiMo。

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
│   │   ├── tts_controller.py
│   │   └── voice_controller.py
│   ├── services/
│   │   └── mimo_service.py
│   ├── schemas/
│   │   └── tts.py
│   ├── core/
│   │   └── config.py
│   └── static/
│       └── index.html
├── requirements.txt
├── .env.example
├── Dockerfile
├── .gitignore
└── README.md
```

---

## 运行前准备

需要安装：

- Python 3.10+
- pip
- 浏览器，例如 Edge、Chrome

推荐 Python 3.11 或 3.12。

---

## Windows 第一次启动

打开 PowerShell，进入项目目录。

如果项目解压在桌面：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web"
```

如果你解压后是双层目录，比如：

```txt
C:\Users\21642\Desktop\mimo-tts-web\mimo-tts-web
```

那就进入里面那一层：

```powershell
cd "C:\Users\21642\Desktop\mimo-tts-web\mimo-tts-web"
```

然后运行：

```powershell
python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，浏览器打开：

```txt
http://127.0.0.1:8000
```

不要直接双击 `app/static/index.html`。

---

## Windows 第二次以后启动

以后不用重复安装依赖，只需要：

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

## 网页里怎么填 Token

打开网页后，在顶部 **连接 MiMo API** 区域填写你的 MiMo API Token。

认证方式建议先选：

```txt
Bearer Token
```

如果返回 401，再切换成：

```txt
api-key 请求头
```

如果你勾选“记住到本机浏览器”，Token 会保存在当前浏览器的 `localStorage` 中。请不要在公共电脑上勾选。

---

## 内置音色

当前内置音色使用 MiMo 接口实际返回过的可用名称：

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

如果遇到：

```txt
Unknown voice
```

说明音色名称不被当前接口支持，请选择上面这些音色。

---

## 声音复刻使用方法

网页中进入 **复刻声音 / 自定义音色** 区域：

1. 填写音色名称，例如：`我的声音`。
2. 上传一段音频，或点击“开始录音”。
3. 建议样本 10–30 秒。
4. 勾选授权确认。
5. 点击“保存为复刻音色”。
6. 保存成功后，该音色会自动加入“发音人”下拉框。
7. 输入文本，点击“生成语音”。

注意事项：

- 只上传自己的声音，或已获得声音本人授权的音频。
- 不要用于冒充、诈骗或误导他人。
- 音频尽量清晰、安静、单人声。
- 样本太大会导致 Base64 超过限制。
- 上传 mp3 / wav 最稳。

---

## 手机访问电脑上的项目

如果你想在手机上打开网页，但后端运行在电脑上：

1. 电脑和手机连接同一个 WiFi。
2. 电脑启动后端时必须使用：

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. 在电脑 PowerShell 查看局域网 IP：

```powershell
ipconfig
```

找到类似：

```txt
IPv4 地址 . . . . . . . . . . . . : 192.168.1.8
```

4. 手机浏览器打开：

```txt
http://电脑IPv4地址:8000
```

例如：

```txt
http://192.168.1.8:8000
```

不要在手机上打开：

```txt
http://127.0.0.1:8000
```

因为手机上的 `127.0.0.1` 指的是手机自己，不是电脑。

如果手机打不开，可能是 Windows 防火墙拦截。可以用管理员 PowerShell 执行：

```powershell
New-NetFirewallRule -DisplayName "MiMo TTS Web 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

---

## 安卓手机 Termux 运行

安卓可以使用 **Acode + Termux**。

Acode 负责编辑代码，Termux 负责运行 FastAPI 后端。

Termux 命令：

```bash
termux-setup-storage

pkg update

pkg install python

cd /storage/emulated/0/Download/mimo-tts-web

pip install -r requirements.txt

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

浏览器打开：

```txt
http://127.0.0.1:8000
```

---

## 可选：使用 .env 配置 Token

默认情况下，你可以直接在网页里填写 Token。

如果你不想每次在网页填，也可以复制配置文件：

```bash
cp .env.example .env
```

然后编辑 `.env`：

```env
MIMO_API_KEY=your_mimo_token_here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_ENDPOINT_PATH=/chat/completions
MIMO_MODEL=mimo-v2.5-tts
MIMO_VOICE_CLONE_MODEL=mimo-v2.5-tts-voiceclone
MIMO_AUTH_TYPE=bearer
```

前端传入 Token 时，会优先使用前端 Token。前端不填时，才使用 `.env` 里的 `MIMO_API_KEY`。

---

## curl 测试后端

```bash
curl -X POST "http://127.0.0.1:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "你的 MiMo Token",
    "auth_type": "bearer",
    "text": "你好，这是 MiMo V2.5 TTS 测试。",
    "voice": "茉莉",
    "speed": 1.0,
    "volume": 80,
    "response_format": "mp3"
  }' \
  --output output.mp3
```

Windows CMD 可以使用：

```cmd
curl -X POST "http://127.0.0.1:8000/api/tts" ^
  -H "Content-Type: application/json" ^
  -d "{\"api_key\":\"你的 MiMo Token\",\"auth_type\":\"bearer\",\"text\":\"你好，这是 MiMo V2.5 TTS 测试。\",\"voice\":\"茉莉\",\"speed\":1.0,\"volume\":80,\"response_format\":\"mp3\"}" ^
  --output output.mp3
```

---

## 常见问题

### 1. 为什么直接双击 index.html 不行？

因为项目需要 FastAPI 后端代理 MiMo API。

正确打开地址是：

```txt
http://127.0.0.1:8000
```

不是：

```txt
file:///C:/Users/.../index.html
```

---

### 2. `Failed to fetch` 怎么办？

通常是后端没有启动，或者你直接打开了 HTML 文件。

先确认这个地址能打开：

```txt
http://127.0.0.1:8000/api/health
```

如果打不开，说明后端没启动成功。

---

### 3. `.\.venv\Scripts\Activate.ps1` 找不到怎么办？

说明还没创建虚拟环境，先运行：

```powershell
python -m venv .venv
```

如果 `python` 不行，试：

```powershell
py -m venv .venv
```

---

### 4. `Unknown voice` 怎么办？

选择项目内置支持的音色，例如：

```txt
茉莉
苏打
mimo_default
```

不要使用旧的：

```txt
xiaomi-mimo-test
moli
bingtang
```

---

### 5. 复刻音色时报 404 怎么办？

新版已经不再调用 `/voices/add`。如果还出现类似问题，请确认你启动的是新版项目，并且浏览器地址是：

```txt
http://127.0.0.1:8000
```

不是直接打开旧的 `index.html`。

可以按 `Ctrl + F5` 强制刷新缓存。

---

### 6. 401 鉴权失败怎么办？

检查：

- Token 是否填错
- 认证方式是否应该切换为 `api-key`
- 账户是否有 MiMo V2.5 TTS 或 VoiceClone 权限
- Token 是否过期或额度不足

---

## GitHub 发布注意事项

请确保 `.gitignore` 包含：

```gitignore
.env
.venv/
__pycache__/
*.pyc
start-log.txt
```

不要上传：

- 真实 API Token
- `.env`
- 个人声音样本
- 生成的私人音频

---

## 免责声明

本项目仅用于学习和个人合法用途。声音复刻功能请只用于本人声音或已获得授权的声音。禁止用于冒充他人、诈骗、误导公众、侵犯隐私或其他违法用途。
