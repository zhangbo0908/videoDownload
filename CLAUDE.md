# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Python 命令行工具，用于从 1000+ 视频网站（YouTube, Bilibili, TikTok 等）下载视频并支持格式转换。

## 核心命令

### 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 安装 FFmpeg（必需，用于格式转换）
brew install ffmpeg
```

### 运行应用
```bash
# 直接运行 Python 源代码
python3 video_extractor.py

# 构建独立可执行文件
pyinstaller video-extractor.spec

# 运行打包后的应用（需先授权）
chmod +x dist/video-extractor
./dist/video-extractor
```

### 使用模式
```bash
# 交互模式
./video-extractor

# 命令行模式 - 默认 1080P + MP4
./video-extractor "视频链接"

# 指定分辨率 (max/1080/720/480)
./video-extractor "视频链接" --res 720

# 跳过格式转换
./video-extractor "视频链接" --no-mp4
```

## 代码架构

### 核心类: VideoExtractor

位置: [video_extractor.py](video_extractor.py)

**关键设计模式**:
- **延迟导入**: `yt_dlp` 在 `extract()` 方法内导入，显著提升启动速度
- **下载目录管理**: 构造函数自动创建 `downloads/` 目录

**关键方法**:
- `progress_hook(d)` - 实时显示下载进度、速度、剩余时间
- `convert_to_mp4_ffmpeg(input_path, output_path)` - 使用 FFmpeg 转换为 H.264/AAC MP4
- `extract(url, convert_to_mp4=True, resolution='1080')` - 核心提取方法

### 分辨率处理逻辑

格式选择字符串（yt-dlp format）:
- `max` → `bestvideo+bestaudio/best` (最高可用画质)
- `1080` → `bestvideo[height<=1080]+bestaudio/best[height<=1080]`
- 其他数值 → 动态构建格式字符串

### 格式转换流程

1. 检查文件是否已是 MP4（如果是则跳过转换）
2. 使用 FFmpeg 转换为 H.264/AAC MP4
3. 转换成功后删除原文件
4. 转换失败时保留原文件并显示错误

## 依赖说明

| 依赖 | 用途 |
|------|------|
| yt-dlp | 视频下载引擎（支持 1000+ 网站） |
| FFmpeg | 格式转换引擎（需手动安装） |
| PyInstaller | 打包成独立可执行文件 |

## 输出位置

所有下载的视频保存在 `downloads/` 目录下。

## 打包配置

PyInstaller 配置文件: [video-extractor.spec](video-extractor.spec)
