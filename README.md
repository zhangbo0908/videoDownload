# 万能视频提取工具

一个轻量级的命令行视频提取工具，支持全球 1000+ 视频网站（如 YouTube, Bilibili, TikTok 等）的最高画质下载，并支持自动转换为 MP4 格式。

## 核心功能
- ✅ **全能支持**：覆盖 YouTube, Bilibili, TikTok, X (Twitter), Instagram 等主流平台
- ✅ **自动转码**：下载后自动将 WebM/MKV 转换为兼容性最好的 MP4 (H.264)
- ✅ **画质控制**：默认下载 **1080P**（平衡体积与画质），支持手动选择 720P/480P 或 Max (原始最高画质)
- ✅ **简单易用**：提供 macOS 独立应用，即开即用

## 🌐 支持的网站
核心引擎基于 `yt-dlp`，支持全球 1000+ 视频网站，以下为常用的主流网站：

### 🇨🇳 国内主流
- **Bilibili (B站)**：支持 1080P/4K/8K、番剧、电影
- **抖音 (Douyin)**：支持个人主页、收藏夹批量下载
- **快手 (Kuaishou)**：支持短视频、直播回放
- **微博 (Weibo)**：支持秒拍、长视频
- **小红书 (Xiaohongshu)**：支持笔记视频、图集
- **腾讯视频/优酷/爱奇艺**：支持部分无加密长视频
- **直播平台**：斗鱼、虎牙（支持录制直播流）

### 🌎 国际主流
- **YouTube**：支持所有画质、字幕、列表下载
- **TikTok**：支持无水印下载
- **Instagram**：支持 Reels、IGTV、图片/视频帖子
- **X (Twitter)**：支持推文视频
- **Facebook**：支持公开视频、极速下载
- **Twitch**：支持直播切片及录像
- **Other**：Reddit, Pinterest, TED, Vimeo, Pornhub 等

## 准备工作
为了能进行视频合并及格式转换，您需要在电脑上安装 **FFmpeg**。
*如果已经安装过，可跳过此步*。

打开终端运行：
```bash
brew install ffmpeg
```

## 使用说明 (macOS)

### 1. 获取应用
在 `dist/` 目录下找到 `video-extractor` 文件。

### 2. 授权与运行
首次使用时，需要先在终端赋予文件执行权限：

```bash
chmod +x video-extractor
```

授权后即可运行：

#### 交互模式 (推荐)
```bash
./video-extractor
```
1. 粘贴视频链接。
2. **选择分辨率**：默认为 1080P (直接回车)，输入 `max` 为最高画质，或输入 `720`、`480` 等数值限制画质。
3. 确认是否转码为 MP4。

#### 命令行模式
```bash
# 默认 1080P & 转为 MP4
./video-extractor "https://www.bilibili.com/video/BV1xxxxxx"

# 指定分辨率 (如 720P)
./video-extractor "视频链接" --res 720

# 下载最高画质 (4K/8K)
./video-extractor "视频链接" --res max

# 仅下载原格式 (不转码)
./video-extractor "视频链接" --no-mp4
```

### 3. 下载位置
所有下载的视频将保存在当前目录下的 `downloads/` 文件夹中。
