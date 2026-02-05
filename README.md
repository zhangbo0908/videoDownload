# 万能视频提取工具

> 🎯 **双模式设计**：提供科技简约风格的 **GUI 界面**和强大的**命令行工具**，支持 Bilibili、YouTube 等 1000+ 视频平台的高画质下载。

![Platform](https://img.shields.io/badge/Platform-macOS-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-green)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

---

## ✨ 核心特性

- 🎨 **双模式运行**：GUI 可视化界面 + 命令行批处理
- 🌐 **全平台支持**：Bilibili、YouTube、抖音、TikTok 等 1000+ 网站
- 🎬 **智能转码**：自动将 WebM/MKV 转为 MP4 (H.264)
- 📊 **实时进度**：GUI 任务列表 + 动态进度条
- ⚙️ **画质控制**：支持 360P ~ 8K 自由选择
- 🔒 **隐私保护**：自动读取浏览器登录态（无需手动输入密码）

---

## 📦 安装依赖

### 必需依赖

#### 1. FFmpeg（视频处理核心）

```bash
brew install ffmpeg
```

#### 2. Python 依赖（仅开发/源码运行）

```bash
pip install -r requirements.txt
```

**核心依赖说明**：
- `yt-dlp`：视频下载引擎（支持 1000+ 网站）
- `flet[all]`：跨平台 GUI 框架
- `pycryptodomex`：浏览器 cookies 解密（读取登录态）

---

## 🚀 使用指南

### 方式 1：GUI 图形界面（推荐新手）

#### 启动应用

```bash
# 使用虚拟环境运行（开发模式）
.venv/bin/python gui_app.py

# 或使用打包后的应用（待打包）
./dist/video-downloader-gui
```

#### 界面功能

<details>
<summary><b>📸 界面预览</b></summary>

- **深色科技风格**：毛玻璃效果 + 极光蓝强调色
- **任务卡片**：实时显示下载进度、速度、剩余时间
- **设置面板**：可调整分辨率（360P ~ 1080P）、转码开关

</details>

#### 使用步骤

1. **粘贴视频链接**：在输入框中粘贴 Bilibili/YouTube 等链接
2. **点击下载**：自动解析并开始下载
3. **实时监控**：在任务列表中查看进度
4. **自定义设置**：点击右上角齿轮图标调整参数

---

### 方式 2：命令行工具（批量/自动化）

#### 交互模式（推荐）

```bash
# 开发模式
.venv/bin/python video_extractor.py

# 打包版本
./dist/video-extractor
```

**交互流程**：
1. 输入视频链接
2. 选择分辨率（默认 1080P，输入 `max` 为最高画质）
3. 确认是否转为 MP4（默认是）

#### 命令行模式（脚本化）

```bash
# 默认 1080P + 转 MP4
./dist/video-extractor "https://www.bilibili.com/video/BV1xxxxxx"

# 指定分辨率
./dist/video-extractor "视频链接" --res 720

# 下载最高画质
./dist/video-extractor "视频链接" --res max

# 跳过转码（保留原格式）
./dist/video-extractor "视频链接" --no-mp4
```

---

## 🌐 支持的平台

### 🇨🇳 国内主流

| 平台 | 支持级别 | 备注 |
|------|----------|------|
| **Bilibili** | ✅ 完全支持 | 1080P/4K，需登录大会员下载高清 |
| **抖音** | ✅ 支持 | 无水印下载 |
| **快手** | ✅ 支持 | 短视频、直播回放 |
| **小红书** | ⚠️ 部分支持 | 部分笔记需登录 |
| **腾讯视频/优酷** | ⚠️ 部分支持 | 仅支持无 DRM 保护的视频 |

### 🌎 国际主流

| 平台 | 支持级别 | 备注 |
|------|----------|------|
| **YouTube** | ⚠️ 受限支持 | 需要 Chrome 登录态 + VPN，成功率因地区而异 |
| **TikTok** | ✅ 支持 | 无水印下载 |
| **Instagram** | ✅ 支持 | Reels、IGTV |
| **Twitter (X)** | ✅ 支持 | 推文视频 |

> **注意**：由于 YouTube 在 2025 年起大幅强化反爬虫策略，建议使用 VPN 并在 Chrome 中登录账号。详见故障排查。

---

## 🛠 开发与打包

### 打包独立应用

#### 命令行版本

```bash
pyinstaller --onefile --name video-extractor video_extractor.py
```

#### GUI 版本

```bash
pyinstaller --onefile --name video-downloader-gui --windowed gui_app.py
```

**输出目录**：`dist/`

详细打包说明见 [implementation_plan.md](file:///.gemini/antigravity/brain/2f737ed5-2509-4871-8511-f7ae1ec526b9/implementation_plan.md)

---

## ❓ 常见问题

<details>
<summary><b>Q1: Bilibili 下载提示 403 错误</b></summary>

**原因**：
- 视频需要登录或大会员权限
- IP 被临时限流

**解决方案**：
1. 在 Chrome 中登录 Bilibili 账号
2. 使用 GUI 版本（会自动读取登录态）
3. 尝试下载公开视频测试

</details>

<details>
<summary><b>Q2: YouTube 下载失败</b></summary>

**原因**：YouTube 2025 年起大幅强化反爬虫策略。

**解决方案**：
1. **必须**在 Chrome 中登录 YouTube 账号
2. 使用 VPN 切换到美国/欧洲 IP
3. 降低分辨率至 480P 或 360P
4. 如仍失败，这是 YouTube 平台限制，无法通过代码解决

</details>

<details>
<summary><b>Q3: macOS 提示"无法打开，因为来自身份不明的开发者"</b></summary>

**解决方案**：
```bash
# 方法 1：终端授权
chmod +x dist/video-downloader-gui
xattr -d com.apple.quarantine dist/video-downloader-gui

# 方法 2：手动授权
# 右键点击应用 → 打开 → 确认打开
```

</details>

---

## 📄 开源协议

本项目采用 Apache 2.0 许可证。详见 [LICENSE](LICENSE)。

---

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)：强大的视频下载引擎
- [Flet](https://flet.dev/)：跨平台 GUI 框架
- [FFmpeg](https://ffmpeg.org/)：视频处理核心

---

## ⚠️ 免责声明

本工具仅供**个人学习与研究**使用。请遵守视频平台的服务条款，尊重版权所有者的权益。严禁将下载内容用于商业用途或二次分发。
