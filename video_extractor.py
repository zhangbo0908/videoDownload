import sys
import os
# import yt_dlp # 移除顶层导入，优化启动速度

class VideoExtractor:
    def __init__(self, download_dir=None, progress_callback=None, status_callback=None):
        if download_dir is None:
            # 默认为用户下载目录下的 VideoDownloads 文件夹
            download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloads")
            
        self.download_dir = download_dir
        self.progress_callback = progress_callback # 用于同步进度的回调 (percent, speed, eta)
        self.status_callback = status_callback     # 用于同步状态文字的回调
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        # 检查 FFmpeg 是否可用
        import shutil
        if not shutil.which("ffmpeg"):
            self._log("警告: 系统中未检测到 FFmpeg，部分平台(如B站)可能无法下载高清或视频合并。")

    def _log(self, message):
        if self.status_callback:
            self.status_callback(message)
        else:
            print(message)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('%','').strip()
            s_str = d.get('_speed_str', 'N/A')
            e_str = d.get('_eta_str', 'N/A')
            
            if self.progress_callback:
                try:
                    p_val = float(p_str) / 100.0
                    self.progress_callback(p_val, s_str, e_str)
                except:
                    pass
            else:
                print(f"\r正在下载: {p_str}% | 速度: {s_str} | 剩余时间: {e_str}", end='')
        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(1.0, "完成", "0s")

    def convert_to_mp4_ffmpeg(self, input_path, output_path):
        import subprocess
        cmd = [
            'ffmpeg', '-y', '-i', input_path, 
            '-c:v', 'libx264', '-c:a', 'aac', 
            '-crf', '23', '-preset', 'fast', 
            '-loglevel', 'error', '-stats',
            output_path
        ]
        self._log("启动 FFmpeg 转码引擎...")
        subprocess.run(cmd, check=True)

    def extract(self, url, convert_to_mp4=True, resolution='1080'):
        import yt_dlp
        
        # 自动补全协议头
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        self._log(f"正在解析链接: {url}")
        
        if resolution.lower() == 'max':
            format_str = 'bestvideo+bestaudio/best'
            self._log("选择画质: 最高可用画质")
        else:
            try:
                res_val = int(resolution.replace('p', '').replace('P', ''))
                # YouTube 特定优化：排除 HLS 协议，优先使用 progressive mp4
                if 'youtube.com' in url or 'youtu.be' in url:
                    format_str = f'best[height<={res_val}][ext=mp4][protocol!=m3u8]/bestvideo[height<={res_val}][protocol!=m3u8]+bestaudio[protocol!=m3u8]/best[height<={res_val}]'
                    self._log(f"选择画质: 不超过 {res_val}P (排除 HLS 流)")
                else:
                    format_str = f'bestvideo[height<={res_val}]+bestaudio/best[height<={res_val}]'
                    self._log(f"选择画质: 不超过 {res_val}P")
            except ValueError:
                format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                self._log("分辨率参数错误，使用默认 1080P")

        # 动态构建 Headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        # 仅针对 Bilibili 添加 Referer（保持最简配置）
        if 'bilibili.com' in url or 'b23.tv' in url:
            headers['Referer'] = 'https://www.bilibili.com/'

        ydl_opts = {
            'format': format_str, 
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'), 
            'progress_hooks': [self.progress_hook],
            'noplaylist': True, 
            'ignoreerrors': True,
            'no_warnings': True,
            'http_headers': headers,
        }
        
        # YouTube 特定优化：使用浏览器 cookies 解决 403 问题
        # 注意：macOS 下读取 Chrome cookies 需要访问钥匙串，会弹出授权提示。
        # 应用户要求移除此功能，避免打扰。如果需要 cookies，建议用户通过 --cookies 参数手动传递。
        # if 'youtube.com' in url or 'youtu.be' in url:
        #     try:
        #         ydl_opts['cookiesfrombrowser'] = ('chrome',)
        #     except:
        #         pass
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    self._log("提取失败: 无法获取视频信息")
                    return False
                
                title = info.get('title', 'Unknown')
                self._log(f"下载完成: {title}")
                
                downloaded_path = None
                # 修复：下载失败时 requested_downloads 可能为空或不包含 filepath
                if 'requested_downloads' in info and info['requested_downloads']:
                    try:
                        downloaded_path = info['requested_downloads'][0].get('filepath')
                    except (KeyError, IndexError):
                        pass
                
                if not downloaded_path:
                    downloaded_path = ydl.prepare_filename(info)
                
                # 检查文件是否真实存在（下载失败时可能只有路径但无文件）
                if not downloaded_path or not os.path.exists(downloaded_path):
                    # 尝试寻找 mp4 后缀的文件（yt-dlp 可能自动合并了）
                    if downloaded_path:
                        base_chk, _ = os.path.splitext(downloaded_path)
                        mp4_path = base_chk + ".mp4"
                        if os.path.exists(mp4_path):
                            downloaded_path = mp4_path
                            self._log(f"自适应修正文件路径: {os.path.basename(downloaded_path)}")
                        else:
                            self._log(f"下载失败: 文件未找到 {downloaded_path}")
                            return False
                    else:
                        self._log("下载失败: 无法确定文件路径")
                        return False
                
                if convert_to_mp4 and downloaded_path and os.path.exists(downloaded_path):
                    base, ext = os.path.splitext(downloaded_path)
                    if ext.lower() == '.mp4':
                        self._log("目标文件已是 MP4 格式，无需转换。")
                        return True
                        
                    output_path = base + ".mp4"
                    self._log(f"正在将视频转换为 MP4 格式 (H.264)...")
                    try:
                        self.convert_to_mp4_ffmpeg(downloaded_path, output_path)
                        self._log(f"转换成功: {os.path.basename(output_path)}")
                        os.remove(downloaded_path)
                        self._log("已清理临时源文件。")
                    except Exception as e:
                        self._log(f"格式转换失败: {e}")
                
                return True
                
        except Exception as e:
            self._log(f"发生错误: {str(e)}")
            return False

def main():
    if len(sys.argv) > 1:
        # 命令行模式
        # Usage: ./video-extractor URL [--no-mp4] [--res 720]
        url = None
        convert_to_mp4 = True
        resolution = '1080'
        
        args = sys.argv[1:]
        skip_next = False
        
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue
                
            if arg == "--no-mp4":
                convert_to_mp4 = False
            elif arg == "--res" or arg == "--resolution":
                if i + 1 < len(args):
                    resolution = args[i+1]
                    skip_next = True
            elif not arg.startswith("--"):
                url = arg
        
        if url:
            extractor = VideoExtractor()
            extractor.extract(url, convert_to_mp4=convert_to_mp4, resolution=resolution)
        else:
            print("错误: 未提供视频链接")
    else:
        # 交互模式
        print("=== 万能视频提取工具 ===")
        print("输入 q 退出")
        
        extractor = VideoExtractor()
        
        while True:
            try:
                url = input("\n请输入视频链接: ").strip()
                if url.lower() == 'q':
                    break
                
                if not url:
                    continue

                # 询问分辨率
                res_input = input("选择分辨率? (默认 1080, 输入 max 为最高): ").strip().lower()
                if not res_input:
                    res_input = '1080'
                
                # 询问是否转码
                convert_input = input("是否转换为 MP4 格式? (y/n) [默认为 y]: ").strip().lower()
                convert_to_mp4 = True
                if convert_input == 'n':
                    convert_to_mp4 = False
                    
                extractor.extract(url, convert_to_mp4=convert_to_mp4, resolution=res_input)
                
            except KeyboardInterrupt:
                print("\n退出程序")
                break
            except Exception as e:
                print(f"未知错误: {e}")

if __name__ == "__main__":
    main()
