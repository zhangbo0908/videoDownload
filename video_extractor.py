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
        self.last_error = None # 记录最后一次错误信息
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        # 检查 FFmpeg 是否可用 (增强路径检测)
        import shutil
        
        # 常见路径列表 (macOS/Linux)
        possible_paths = [
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "/opt/local/bin",
            "/usr/bin",
            "/bin",
            os.path.join(os.path.expanduser("~"), "bin")
        ]
        
        # 尝试将这些路径添加到 PATH
        current_path = os.environ.get("PATH", "")
        for p in possible_paths:
            if os.path.exists(p) and p not in current_path:
                os.environ["PATH"] += os.pathsep + p
                
        if not shutil.which("ffmpeg"):
            self._log("警告: 系统中未检测到 FFmpeg，部分平台(如B站)可能无法下载高清或视频合并。")
        else:
            # self._log(f"FFmpeg 已就绪: {shutil.which('ffmpeg')}")
            pass

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
                self.progress_callback(1.0, "下载完成，准备处理...", "0s")

    def convert_to_mp4_ffmpeg(self, input_path, output_path):
        import subprocess
        cmd = [
            'ffmpeg', '-y', '-i', input_path, 
            '-c:v', 'libx264', '-c:a', 'aac', 
            '-crf', '23', '-preset', 'fast', 
            '-loglevel', 'error', '-stats',
            output_path
        ]
        self._log("状态: 正在转码 (FFmpeg)...")
        subprocess.run(cmd, check=True)

    def extract(self, url, convert_to_mp4=True, resolution='1080'):
        import yt_dlp
        
        self.last_error = None
        
        # 自动补全协议头
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        self._log(f"状态: 正在解析链接...")
        
        if resolution.lower() == 'max':
            format_str = 'bestvideo+bestaudio/best'
            # self._log("选择画质: 最高可用画质")
        else:
            try:
                res_val = int(resolution.replace('p', '').replace('P', ''))
                # YouTube 特定优化：排除 HLS 协议，优先使用 progressive mp4
                if 'youtube.com' in url or 'youtu.be' in url:
                    format_str = f'best[height<={res_val}][ext=mp4][protocol!=m3u8]/bestvideo[height<={res_val}][protocol!=m3u8]+bestaudio[protocol!=m3u8]/best[height<={res_val}]'
                    # self._log(f"选择画质: 不超过 {res_val}P (排除 HLS 流)")
                else:
                    format_str = f'bestvideo[height<={res_val}]+bestaudio/best[height<={res_val}]'
                    # self._log(f"选择画质: 不超过 {res_val}P")
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
            downloaded_path = None
            output_path = None # 最终文件路径
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._log("状态: 开始提取下载...")
                info = ydl.extract_info(url, download=True)
                if not info:
                    self.last_error = "无法获取视频信息"
                    self._log(f"错误: {self.last_error}")
                    return False
                
                title = info.get('title', 'Unknown')
                # self._log(f"下载已完成: {title}")
                
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
                    # 策略1: 尝试寻找 mp4 后缀的文件（自动修正扩展名）
                    if downloaded_path:
                        base_chk, _ = os.path.splitext(downloaded_path)
                        mp4_path = base_chk + ".mp4"
                        if os.path.exists(mp4_path):
                            downloaded_path = mp4_path
                            # self._log(f"自适应修正路径: {os.path.basename(downloaded_path)}")
                        else:
                            # 策略2: 模糊搜索 (应对 FFmpeg 未安装导致无法合并，文件名带有格式后缀的情况)
                            # 例如: "Title.f10086.mp4" 而不是 "Title.mp4"
                            dir_path = os.path.dirname(downloaded_path)
                            base_name = os.path.basename(base_chk) # 去除后缀的文件名部分
                            
                            found_candidate = None
                            if os.path.exists(dir_path):
                                for f in os.listdir(dir_path):
                                    # 检查文件名是否包含预期的标题，且是视频/音频格式
                                    if base_name in f and f.lower().endswith(('.mp4', '.m4a', '.webm', '.mkv')):
                                        found_candidate = os.path.join(dir_path, f)
                                        # 如果找到视频文件，优先使用；如果是音频，继续找看看有没有视频
                                        if f.lower().endswith('.mp4'):
                                            break
                            
                            if found_candidate:
                                downloaded_path = found_candidate
                                # 尝试手动合并分轨文件
                                try:
                                    video_part = None
                                    audio_part = None
                                    # 简单判断：found_candidate 是视频，那还得找音频
                                    # 假设命名规则: Title.fxxx.mp4 (video) 和 Title.fxxx.m4a (audio)
                                    # 或者 yt-dlp 风格: Title.mp4, Title.m4a
                                    
                                    # 扫描目录下所有同名不同后缀文件
                                    candidates = []
                                    for f in os.listdir(dir_path):
                                        if base_name in f:
                                            candidates.append(os.path.join(dir_path, f))
                                    
                                    for c in candidates:
                                        if c.lower().endswith(('.mp4', '.webm', '.mkv')) and not c.lower().endswith('.temp.mp4'): # 排除正在生成的temp
                                            video_part = c
                                        elif c.lower().endswith(('.m4a', '.mp3', '.aac')):
                                            audio_part = c
                                    
                                    if video_part and audio_part and shutil.which("ffmpeg"):
                                        merged_output = os.path.join(dir_path, base_name + ".mp4")
                                        self._log(f"状态: 检测到分轨资源，尝试手动合并...")
                                        self._log(f"视频: {os.path.basename(video_part)}")
                                        self._log(f"音频: {os.path.basename(audio_part)}")
                                        
                                        cmd = [
                                            'ffmpeg', '-y',
                                            '-i', video_part,
                                            '-i', audio_part,
                                            '-c:v', 'copy',
                                            '-c:a', 'aac', # 音频转码 AAC 以保证兼容性
                                            '-strict', 'experimental',
                                            '-loglevel', 'error',
                                            merged_output
                                        ]
                                        import subprocess
                                        subprocess.run(cmd, check=True)
                                        
                                        self._log("状态: 手动合并成功")
                                        downloaded_path = merged_output
                                        output_path = merged_output
                                        
                                        # 清理分轨文件
                                        try:
                                            os.remove(video_part)
                                            os.remove(audio_part)
                                        except:
                                            pass
                                    else:
                                        self.last_error = "下载成功但未合并 (缺少 FFmpeg 或 音频轨)"
                                        self._log(f"警告: {self.last_error}")
                                except Exception as e:
                                    self._log(f"手动合并失败: {e}")
                                    self.last_error = "下载成功但未合并"

                            else:
                                self.last_error = f"文件未找到: {os.path.basename(downloaded_path)}"
                                self._log(f"错误: {self.last_error}")
                                return False
                    else:
                        self.last_error = "无法确定文件下载路径"
                        self._log(f"错误: {self.last_error}")
                        return False
                
                # 默认最终路径就是下载路径
                output_path = downloaded_path

                if convert_to_mp4 and downloaded_path and os.path.exists(downloaded_path):
                    base, ext = os.path.splitext(downloaded_path)
                    if ext.lower() == '.mp4':
                        self._log("状态: 校验完成 (已是 MP4)")
                        return True
                        
                    target_mp4 = base + ".mp4"
                    self._log(f"状态: 正在转码为 MP4...")
                    try:
                        self.convert_to_mp4_ffmpeg(downloaded_path, target_mp4)
                        self._log(f"状态: 转码成功")
                        output_path = target_mp4 # 更新最终路径
                        os.remove(downloaded_path)
                        # self._log("已清理源文件")
                    except Exception as e:
                        self.last_error = f"转码异常: {str(e)}"
                        self._log(f"警告: {self.last_error}")
                        # 转码失败不应导致任务失败，只要源文件还在
                        output_path = downloaded_path
                
                # 最终校验：只要有一个文件存在，就返回成功
                if output_path and os.path.exists(output_path):
                    self._log("状态: 任务全部完成")
                    return True
                elif downloaded_path and os.path.exists(downloaded_path):
                    self._log("状态: 任务完成 (未转码)")
                    return True
                else:
                    self.last_error = "最终文件校验失败"
                    return False
                
        except Exception as e:
            self.last_error = f"运行异常: {str(e)}"
            self._log(f"错误: {self.last_error}")
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
