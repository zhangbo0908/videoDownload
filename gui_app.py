import flet as ft
import os
import threading
from video_extractor import VideoExtractor

class DownloadTask(ft.Container):
    def __init__(self, url, extractor, on_task_complete):
        super().__init__()
        self.url = url
        self.extractor = extractor
        self.on_task_complete = on_task_complete
        self.progress_bar = ft.ProgressBar(value=0, color="#00D2FF", bgcolor="#333333", height=8)
        self.status_text = ft.Text("准备中...", size=12, color="#E0E0E0")
        self.speed_text = ft.Text("", size=11, color="#AAAAAA")
        self.title_text = ft.Text(url, size=14, weight="bold", overflow=ft.TextOverflow.ELLIPSIS)

        # Container 配置
        self.padding = 15
        self.border_radius = 10
        self.bgcolor = "#1E1E1E"
        self.border = ft.border.all(1, "#333333")
        self.margin = ft.margin.only(bottom=10)
        self.content = ft.Column([
            self.title_text,
            self.status_text,
            self.progress_bar,
            self.speed_text,
        ], spacing=5)

    def update_progress(self, percent, speed, eta):
        self.progress_bar.value = percent
        self.speed_text.value = f"速度: {speed} | 剩余: {eta}"
        self.update()

    def update_status(self, message):
        self.status_text.value = message
        self.update()

    def run_download(self, convert_to_mp4=True, resolution='1080'):
        self.extractor.progress_callback = self.update_progress
        self.extractor.status_callback = self.update_status
        success = self.extractor.extract(self.url, convert_to_mp4=convert_to_mp4, resolution=resolution)
        if success:
            self.status_text.value = "任务已完成"
            self.status_text.color = ft.Colors.GREEN_400
            self.progress_bar.value = 1.0
            self.speed_text.value = "下载并处理完成 100%"
        else:
            # 优先显示具体错误信息
            error_msg = getattr(self.extractor, 'last_error', None)
            if error_msg:
                self.status_text.value = f"失败: {error_msg}"
            else:
                self.status_text.value = "任务失败"
            self.status_text.color = ft.Colors.RED_400
        self.on_task_complete()
        self.update()

def main(page: ft.Page):
    page.title = "万能视频提取工具"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 30
    page.window_width = 850
    page.window_height = 700
    page.window_resizable = True

    # 状态变量
    config = {
        # 修复：macOS 打包应用中 os.getcwd() 可能为只读根目录
        # 改为使用用户下载文件夹
        "path": os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloads"),
        "resolution": "1080",
        "convert": True
    }

    if not os.path.exists(config["path"]):
        os.makedirs(config["path"])
    
    # UI 组件
    url_input = ft.TextField(
        hint_text="粘贴视频链接 (Bilibili, YouTube, TikTok...)",
        border_color="#00D2FF",
        expand=True,
        height=50,
        text_size=14,
        content_padding=15,
        border_radius=10,
    )

    task_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    def add_task(url=None):
        target_url = url if url else url_input.value.strip()
        if not target_url: return
        
        # 自动补全协议头
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url
            
        if not url: url_input.value = ""
        
        extractor = VideoExtractor(
            download_dir=config["path"]
        )
        
        task_ui = DownloadTask(target_url, extractor, lambda: page.update())
        task_list.controls.insert(0, task_ui)
        page.update()
        
        def thread_wrapper():
            try:
                task_ui.run_download(convert_to_mp4=config["convert"], resolution=config["resolution"])
            except Exception as ex:
                task_ui.status_text.value = f"错误: {str(ex)}"
                task_ui.status_text.color = ft.Colors.RED_400
                task_ui.update()

        threading.Thread(target=thread_wrapper, daemon=True).start()

    # 设置面板
    def toggle_settings(e):
        page.drawer.open = not page.drawer.open
        page.update()

    page.drawer = ft.NavigationDrawer(
        bgcolor="#1A1A1A",
        controls=[
            ft.Container(height=20),
            ft.Text("   偏好设置", size=20, weight="bold", color="#00D2FF"),
            ft.Divider(color="#333333"),
            ft.Container(
                content=ft.Column([
                    ft.Text("下载分辨率", size=14),
                    ft.Dropdown(
                        value="1080",
                        options=[
                            ft.dropdown.Option("max", "最高画质"),
                            ft.dropdown.Option("1080", "1080P"),
                            ft.dropdown.Option("720", "720P"),
                            ft.dropdown.Option("480", "480P"),
                        ],
                        on_change=lambda e: config.update({"resolution": e.data})
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("格式转换", size=14),
                    ft.Switch(
                        label="下载后自动转为 MP4",
                        value=True,
                        active_color="#00D2FF",
                        on_change=lambda e: config.update({"convert": e.control.value})
                    ),
                ], spacing=10),
                padding=20
            )
        ]
    )

    # 剪贴板监控 (简易版示例)
    def check_clipboard():
        import time
        last_clip = ""
        while True:
            # 注意：GUI 环境下获取剪贴板可能需要特定库或 API
            # 这里仅展示逻辑结构
            time.sleep(2)

    # UI 组装
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("VIDEO DOWNLOAD", size=28, weight="black", color="#00D2FF"),
                        ft.Text("万能视频提取工具 · 科技简约版", size=12, color="#666666"),
                    ]),
                    ft.IconButton(ft.Icons.SETTINGS_ROUNDED, icon_color="#00D2FF", on_click=toggle_settings)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=30, color="transparent"),
                ft.Row([
                    url_input,
                    ft.Container(
                        content=ft.ElevatedButton(
                            "解析并下载",
                            icon=ft.Icons.BOLT_ROUNDED,
                            bgcolor="#00D2FF",
                            color=ft.Colors.BLACK,
                            on_click=lambda _: add_task(),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        ),
                        height=50
                    ),
                ], spacing=10),
                ft.Divider(height=20, color="#333333"),
                ft.Row([
                    ft.Icon(ft.Icons.LIST_ALT_ROUNDED, size=18, color="#666666"),
                    ft.Text(" 任务列表", size=16, weight="bold", color="#888888"),
                ]),
                task_list
            ]),
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
