# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个**双模式视频下载工具**，同时提供：
- **GUI 图形界面** - 基于 Flet 框架的现代化桌面应用
- **命令行界面** - 适合自动化和批处理

支持从 1000+ 视频网站（YouTube, Bilibili, TikTok 等）下载视频并自动转换为 MP4 格式。

## 核心命令

### 环境准备
```bash
# 创建虚拟环境（推荐使用 .venv 名称，与 build.sh 一致）
python3.12 -m venv .venv
source .venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 FFmpeg（可选，GUI 版已内置，CLI 模式必需）
brew install ffmpeg
```

### 运行应用
```bash
# GUI 模式 - 图形界面
python3 gui_app.py

# CLI 模式 - 交互式命令行
python3 video_extractor.py

# CLI 模式 - 直接下载
python3 video_extractor.py "视频链接"

# CLI 模式 - 指定分辨率和跳过转换
python3 video_extractor.py "视频链接" --res 720 --no-mp4
```

### 打包构建

**推荐：使用一键打包脚本**
```bash
# 一键打包 GUI + CLI 两个版本
./build.sh
```

[build.sh](build.sh) 脚本会自动完成：
1. 检查虚拟环境（`.venv`）和依赖
2. 使用 [assets/create_icon.sh](assets/create_icon.sh) 生成应用图标
3. 打包两个版本（GUI 和 CLI）
4. 修正 macOS 应用元数据（Info.plist、图标）
5. 重命名为 "Video Downloader.app"
6. 移除隔离属性并重新签名

**关键打包配置差异**：

| 配置项 | GUI 版本 ([video-downloader-gui.spec](video-downloader-gui.spec)) | CLI 版本 ([video-extractor.spec](video-extractor.spec)) |
|--------|------------------------------------------------|--------------------------------------------|
| 内置 FFmpeg | ✅ 是 (`binaries=[('bin/ffmpeg', 'bin')]`) | ❌ 否（依赖系统 FFmpeg） |
| 输出名称 | `Video Downloader.app` | `video-extractor` |
| 控制台 | 无 (`console=False`) | 有 (`console=True`) |
| UPX 压缩 | ❌ 禁用 | ✅ 启用 |
| Strip | ❌ 禁用 | ❌ 禁用 |

**手动打包（不推荐）**
```bash
# 打包 GUI 版本（生成 .app 和可执行文件）
pyinstaller video-downloader-gui.spec

# 打包 CLI 版本（生成命令行工具）
pyinstaller video-extractor.spec

# 打包后移除 macOS 隔离属性（注意应用名称）
xattr -cr dist/Video\ Downloader.app

# 重新签名（解决 macOS 安全问题）
codesign --force --deep --sign - dist/Video\ Downloader.app
```

## 项目结构

```
videoDownload/
├── gui_app.py              # GUI 图形界面入口
├── video_extractor.py      # CLI 入口 + 核心下载引擎
├── build.sh                # 一键打包脚本（推荐使用）
├── assets/
│   ├── icon.png            # 应用图标源文件
│   └── create_icon.sh      # 图标生成脚本
├── bin/
│   └── ffmpeg              # FFmpeg 静态二进制（打包时内置到 GUI 版）
├── video-downloader-gui.spec  # GUI 打包配置
├── video-extractor.spec    # CLI 打包配置
├── requirements.txt        # Python 依赖
├── README.md               # 用户文档
├── PRD.md                  # 产品需求文档
└── CLAUDE.md               # 本文件
```

## 代码架构

### 双入口设计

| 入口文件 | 用途 | 打包配置 |
|---------|------|---------|
| [gui_app.py](gui_app.py) | GUI 图形界面入口 | [video-downloader-gui.spec](video-downloader-gui.spec) |
| [video_extractor.py](video_extractor.py) | CLI + 核心下载引擎 | [video-extractor.spec](video-extractor.spec) |

两个入口共享同一个 `VideoExtractor` 核心类，完全解耦。

### 核心类: VideoExtractor

位置: [video_extractor.py:5-43](video_extractor.py#L5-L43)

**关键设计模式**:
- **延迟导入**: `yt_dlp` 在 `extract()` 方法内导入（第 81 行），显著提升启动速度
- **回调机制**: 通过 `progress_callback` 和 `status_callback` 实现 GUI 与下载引擎解耦
- **智能 FFmpeg 检测**: 构造函数自动搜索常见 FFmpeg 路径并添加到 PATH
- **错误记录**: `last_error` 属性记录最后一次错误，便于 GUI 显示具体错误信息

**关键方法**:
- `progress_hook(d)` - [第 50-66 行](video_extractor.py#L50-L66)，实时回调下载进度
- `convert_to_mp4_ffmpeg()` - [第 68-78 行](video_extractor.py#L68-L78)，使用 FFmpeg 转换为 H.264/AAC
- `extract()` - [第 80-290 行](video_extractor.py#L80-L290)，核心提取方法，包含复杂的文件处理逻辑

### GUI 组件: DownloadTask

位置: [gui_app.py:6-55](gui_app.py#L6-L55)

- 任务卡片式设计，每个下载任务显示为独立卡片
- 通过回调机制与 `VideoExtractor` 通信
- 在独立线程中运行下载，避免阻塞 UI

### 智能文件处理策略

位置: [video_extractor.py:161-243](video_extractor.py#L161-L243)

当 yt-dlp 下载的文件路径不正确或不存在时，代码会执行多级回退策略：

1. **自适应修正** - 尝试将扩展名改为 `.mp4`
2. **模糊搜索** - 在目录中搜索包含视频标题的视频/音频文件
3. **手动合并** - 检测到分轨文件时（如 `.mp4` + `.m4a`），使用 FFmpeg 手动合并

这是处理 FFmpeg 未安装或合并失败场景的关键逻辑。

### 分辨率处理逻辑

位置: [video_extractor.py:91-106](video_extractor.py#L91-L106)

格式选择字符串（yt-dlp format）:
- `max` → `bestvideo+bestaudio/best` (最高可用画质)
- `1080` → `bestvideo[height<=1080]+bestaudio/best[height<=1080]`
- **YouTube 特殊处理**: 排除 HLS 协议，优先使用 progressive MP4

### 平台特殊处理

**抖音 Douyin** - 位置: [video_extractor.py:54-200+](video_extractor.py#L54-L200)
- 使用 `_extract_douyin_video_url()` 方法进行专用解析
- 通过 `curl_cffi` 模拟 Chrome 120 移动端请求（`impersonate="chrome120"`）
- 解析移动端分享链接的 `_ROUTER_DATA` JSON 获取真实视频地址
- 绕过 yt-dlp 无法处理的 WAF 和签名验证

### 回调机制设计

`VideoExtractor` 支持两种回调：

```python
# 进度回调 - 参数: (百分比, 速度, 剩余时间)
progress_callback(0.5, "2.5MiB/s", "00:15")

# 状态回调 - 参数: 消息字符串
status_callback("状态: 正在解析链接...")
```

GUI 通过设置这些回调来实时更新界面。

## 输出位置

所有下载的视频默认保存在 `~/Downloads/VideoDownloads/` 目录。

## 依赖说明

| 依赖 | 用途 |
|------|------|
| yt-dlp | 视频下载引擎（支持 1000+ 网站） |
| curl_cffi | **绕过抖音 TLS 指纹检测**，模拟 Chrome 120 请求 |
| flet[all] | GUI 框架（Flutter for Python） |
| FFmpeg | 格式转换和视频合并（GUI 版已内置，CLI 需手动安装） |
| PyInstaller | 打包成独立可执行文件 |
| pycryptodomex | 处理加密视频流 |

## 常见问题

### macOS 打包应用无法启动
- 推荐使用 `./build.sh` 打包，脚本会自动处理以下步骤
- 手动操作：移除隔离属性 `xattr -cr dist/Video\ Downloader.app`
- 重新签名: `codesign --force --deep --sign - dist/Video\ Downloader.app`
- **注意**: 打包后的应用名称为 "Video Downloader.app"（不是 video-downloader-gui.app）

### 下载后只有视频无声音
- 原因: FFmpeg 未正确安装或不在 PATH 中
- 解决: 确保 `ffmpeg` 命令在终端可执行

### YouTube 下载失败
- 某些视频可能需要 cookies，代码已移除自动读取浏览器 cookies 功能以避免打扰用户

## 开发模式

### 调试技巧

1. **GUI 开发**: 直接运行 `python3 gui_app.py`，修改代码后重启应用即可看到效果
2. **CLI 开发**: 直接运行 `python3 video_extractor.py` 或传递 URL 参数
3. **FFmpeg 检测**: 查看 `VideoExtractor` 构造函数中的日志输出，确认 FFmpeg 是否被检测到

### 添加新平台支持

1. 在 [video_extractor.py:321-344](video_extractor.py#L321-L344) 中修改 `headers` 和 `ydl_opts` 配置
2. 某些平台可能需要特定的 Referer 或 User-Agent
   - Bilibili: 添加 `Referer: https://www.bilibili.com/`
   - Douyin 直链: 添加移动端 UA
3. 如果平台需要专用解析器（如 Douyin），参考 `_extract_douyin_video_url()` 实现
4. 测试时先使用 CLI 模式，确认无误后再测试 GUI

### 修改 UI 样式

GUI 样式在 [gui_app.py:57-201](gui_app.py#L57-L201) 中定义：
- 主色调: `#00D2FF`（极光蓝）
- 背景色: `#121212`（深灰）
- 卡片背景: `#1E1E1E`
- 修改后需重启应用查看效果
