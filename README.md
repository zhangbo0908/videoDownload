# Video Downloader (万能视频提取工具)

> 🎯 **v0.2.0 重大更新**：基于 **Python 3.12** 和 **Flet 0.80+** 重构，采用**混合下载架构**，完美解决了 YouTube 高画质下载和 API 格式错误问题。提供科技简约风格的 **GUI 界面**，支持 macOS 原生应用体验。

![Platform](https://img.shields.io/badge/Platform-macOS%20(ARM64)-blue)
![Python](https://img.shields.io/badge/Python-3.12%2B-green)
![License](https://img.shields.io/badge/License-Apache%202.0-orange)

---

## ✨ 核心特性

- 🎨 **双模式运行**：
  - **GUI 模式**：原生 macOS 应用 (`.app`)，毛玻璃特效，深色科技风。
  - **命令行模式**：支持脚本调用和批处理。
- 🌐 **全平台支持**：核心优化 **YouTube** 下载体验，同时也支持 Bilibili、TikTok 等 1000+ 平台。
- 🛠 **混合下载架构 (New)**：
  - **YouTube**: 采用动态格式选择算法 (`bestvideo[height<=REL]+bestaudio`)，智能规避 API 限制。
  - **其他平台**: 使用标准 Python API 高效处理。
- 🎬 **智能转码**：自动将 WebM/MKV 转为 MP4，确保兼容性。
- 📊 **实时进度**：精准的下载百分比、速度和剩余时间显示。
- ⚙️ **画质控制**：严格遵循用户设置的分辨率 (360P ~ 1080P/Max)，自动降级回退。
- � **开箱即用 (New)**：应用包已内置 **FFmpeg** 静态二进制文件，无需额外安装即可直接运行。
- �🔒 **隐私保护**：自动读取浏览器 Cookies（Chrome），无需手动提取。

---

## 📦 安装说明 (macOS)

### 方式 1：直接运行应用 (推荐)

在 `dist` 目录下找到打包好的应用：

```bash
dist/Video Downloader.app
```

**首次运行提示 "无法打开"？**
macOS Gatekeeper 可能会拦截未签名的应用（显示“无法验证开发者”或“由于来自不可信开发者而无法打开”）。你需要手动移除文件的“隔离属性”：

1. **指令含义**：
   - `xattr`: 扩展属性工具。
   - `-c`: 清除属性。
   - `-r`: 递归处理整个应用包。
   结合起来就是移除苹果添加的安全标记，让系统允许其运行。

2. **操作示例**：
   - **如果应用在 `dist` 目录**：
     ```bash
     xattr -cr "dist/Video Downloader.app"
     ```
   - **如果已经拖入“应用程序” (Applications) 文件夹**：
     ```bash
     xattr -cr /Applications/"Video Downloader.app"
     ```

处理完成后，直接双击打开即可正常使用。

### 方式 2：从源码运行 (开发模式)

如果你想修改代码或体验最新功能：

1. **环境要求**:
   - Python 3.12+ (必需)
   - (可选) FFmpeg (打包版已内置)

2. **安装依赖**:
   ```bash
   # 创建并激活虚拟环境
   python3.12 -m venv .venv_py312
   source .venv_py312/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **运行 GUI**:
   ```bash
   python gui_app.py
   ```

---

## 🚀 使用指南

### GUI 图形界面

1. **粘贴链接**: 支持 YouTube, Bilibili, TikTok 等 URL。
2. **设置画质**: 点击右上角 ⚙️ 设置图标，选择期望分辨率 (默认 1080P)。
3. **开始下载**: 点击 "解析并下载"。
4. **查看文件**: 默认下载至 `~/Downloads/VideoDownloads`。

### 命令行工具

```bash
# 交互模式
python video_extractor.py

# 命令行参数模式
python video_extractor.py "https://youtu.be/xxx" --res 1080 --mp4
```

---

## 🛠 技术细节 (v0.2.0 更新)

### 1. 架构升级
- **Python 3.12**: 这一版本强制要求 Python 3.12，以获得更好的 SSL/TLS 支持和性能。
- **yt-dlp 2026.02**: 集成了最新的提取器，解决了 YouTube JS 挑战问题。

### 2. 兼容性修复
- **Flet 0.80.5 适配**: 修复了 `Dropdown` 事件绑定和 `page.show_drawer` 异步调用的 API 变更问题。
- **PyInstaller 打包**: 解决了打包后 `yt-dlp` 命令行工具缺失的问题，重构为 Library API 调用。

### 3. YouTube 专项优化
- 移除了导致 403 错误的 `--cookies-from-browser` 参数。
- 实现了动态格式选择器，优先匹配用户分辨率但保留最佳兼容性回退。

---

## 📅 版本历史

- **v0.2.0 (2026-02-05)**: 重大版本更新。修复 YouTube 下载，升级架构，修复 GUI 崩溃问题。
- **v0.1.0**: 初始版本，支持基础 GUI 和 Bilibili 下载。

---

> **注意**: 如果遇到 YouTube 下载慢，通常是网络连接问题。工具本身已配置为使用系统代理。

```bash
# 默认 1080P + 转 MP4
./dist/video-extractor "https://www.bilibili.com/video/BV1xxxxxx"

# 指定分辨率
./dist/video-extractor "视频链接" --res 720

# 下载最高画质
./dist/video-extractor "视频链接" --res max

# 跳过转码（保留原格式）
./dist/video-extractor "视频链接" --no-mp4

# 使用 Cookies 文件（解决需要登录的视频）
./dist/video-extractor "视频链接" --cookies /path/to/cookies.txt

# 组合参数使用
./dist/video-extractor "视频链接" --cookies cookies.txt --res 1080 --no-mp4
```

**如何导出 Cookies 文件:**
1. 安装浏览器插件 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)(Chrome/Edge)
2. 在需要下载的网站登录账号(如 Bilibili、YouTube)
3. 点击插件图标,选择 "Export" → 保存为 `cookies.txt`
4. 使用 `--cookies` 参数传递该文件路径

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

**原因**:YouTube 2025 年起大幅强化反爬虫策略,且工具为了避免 macOS 频繁弹出钥匙串访问提示,**不再自动读取 Chrome Cookies**。

**解决方案**:
1. **使用 VPN**:切换到美国/欧洲 IP 通常能缓解 403 问题。
2. **降低画质**:尝试下载 720P 或更低分辨率。
3. **手动传递 Cookies**(仅命令行):
   ```bash
   # 先导出浏览器 cookies(参见上方"如何导出 Cookies 文件")
   ./dist/video-extractor "YouTube链接" --cookies cookies.txt
   ```

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

<details>
<summary><b>Q4: 下载成功但文件是分离的（有画面没声音/有声音没画面）</b></summary>

**原因**：系统中未安装或未配置 **FFmpeg**。
- 工具已成功下载了视频流和音频流，但在最后一步合并时失败。
- GUI 会提示 "下载成功但未合并"。

**解决方案**：
请参考 [安装依赖](#-安装依赖) 章节安装 FFmpeg。安装后重启应用即可。

</details>

<details>
<summary><b>Q5: 视频下载到哪里了？</b></summary>

**默认路径**：
- **macOS / Linux**: `~/Downloads/VideoDownloads/` (用户下载目录下的 VideoDownloads 文件夹)
- **Windows**: `C:\Users\用户名\Downloads\VideoDownloads\`

为了解决 macOS 打包应用的权限问题，我们已将默认路径固定为用户下载目录。

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
