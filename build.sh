#!/bin/bash
# 视频下载工具 - 自动打包脚本
# 用途：一键打包 GUI 和命令行两个版本

set -e  # 遇到错误立即退出

echo "🚀 开始打包万能视频提取工具..."
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误：未找到虚拟环境 .venv"
    echo "   请先运行: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装打包工具
echo "📦 检查 PyInstaller..."
pip install pyinstaller --quiet

# 准备图标
if [ -f "assets/create_icon.sh" ]; then
    echo "🎨 生成应用图标..."
    chmod +x assets/create_icon.sh
    cd assets && ./create_icon.sh && cd ..
fi

ICON_PARAM=""
if [ -f "assets/app.icns" ]; then
    echo "✅ 图标准备就绪: assets/app.icns"
    ICON_PARAM="--icon=assets/app.icns"
else
    echo "⚠️ 未找到图标文件，将使用默认图标"
fi

echo ""
echo "1️⃣  打包命令行版本..."
pyinstaller --onefile \
    --name video-extractor \
    --clean \
    $ICON_PARAM \
    video_extractor.py

echo ""
echo "2️⃣  打包 GUI 版本..."
pyinstaller --onefile \
    --name video-downloader-gui \
    --windowed \
    --clean \
    $ICON_PARAM \
    gui_app.py

# 后期处理：强制修正 Info.plist 和图标 (解决 macOS 显示 Flet 的问题)
APP_PATH="dist/video-downloader-gui.app"
if [ -d "$APP_PATH" ]; then
    echo "🔨 修正应用元数据..."
    
    # 强制覆盖图标
    if [ -f "assets/app.icns" ]; then
        cp "assets/app.icns" "$APP_PATH/Contents/Resources/app.icns"
    fi
    
    # 修改 Info.plist
    PLIST="$APP_PATH/Contents/Info.plist"
    if [ -f "$PLIST" ]; then
        # 修改显示名称
        plutil -replace CFBundleDisplayName -string "Video Downloader" "$PLIST"
        plutil -replace CFBundleName -string "Video Downloader" "$PLIST"
        # 确保使用正确的图标文件名
        plutil -replace CFBundleIconFile -string "app.icns" "$PLIST"
        # 修改 Bundle ID (避免冲突)
        plutil -replace CFBundleIdentifier -string "com.zhangbo.videodownloader" "$PLIST"
    fi
    
    # 尝试清除图标缓存
    touch "$APP_PATH"
fi

echo ""
echo "✅ 打包完成！"
echo ""
echo "📂 输出目录: dist/"
echo "   - video-extractor          (命令行版本)"
echo "   - video-downloader-gui     (GUI 版本)"
echo ""
echo "💡 使用提示:"
echo "   chmod +x dist/video-extractor"
echo "   chmod +x dist/video-downloader-gui"
echo ""
echo "🎉 大功告成！"
