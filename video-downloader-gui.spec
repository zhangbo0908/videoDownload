# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[('bin/ffmpeg', 'bin')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'tcl', 'idlelib', 'unittest', 'pydoc', 'email', 'html', 'http', 'sqlite3', 'dist'], # 排除 dist 防止无限循环
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Video Downloader', # 直接使用最终名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=True, # 开启 strip 减小体积
    upx=False,  # 如果没有安装 upx 就关闭
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='Video Downloader.app', # 最终 .app 名称
    icon='assets/app.icns',     # 打包时直接指定图标
    bundle_identifier='com.zhangbo.videodownloader',
)
