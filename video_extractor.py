import sys
import os
# import yt_dlp # 移除顶层导入，优化启动速度

class VideoExtractor:
    def __init__(self, download_dir="downloads"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                print(f"\r正在下载: {d.get('_percent_str', '0%')} | 速度: {d.get('_speed_str', 'N/A')} | 剩余时间: {d.get('_eta_str', 'N/A')}", end='')
            except Exception:
                pass

    def convert_to_mp4_ffmpeg(self, input_path, output_path):
        import subprocess
        # 使用 subprocess 调用 ffmpeg，显示简单进度或静默
        # -y: 覆盖输出文件
        # -i: 输入文件
        # -c:v libx264: H.264 视频编码
        # -c:a aac: AAC 音频编码
        # -crf 23: 质量控制
        # -preset fast: 编码速度预设
        cmd = [
            'ffmpeg', '-y', '-i', input_path, 
            '-c:v', 'libx264', '-c:a', 'aac', 
            '-crf', '23', '-preset', 'fast', 
            '-loglevel', 'error', '-stats', # 只显示进度信息
            output_path
        ]
        print("启动 FFmpeg 转码引擎...")
        subprocess.run(cmd, check=True)

    def extract(self, url, convert_to_mp4=True, resolution='1080'):
        # 延迟导入 yt_dlp，显著提升程序启动速度
        import yt_dlp
        
        print(f"正在解析链接: {url}")
        
        # 构建格式选择字符串
        # 默认 1080: bestvideo[height<=1080]+bestaudio/best[height<=1080]
        # Max: bestvideo+bestaudio/best
        
        if resolution.lower() == 'max':
            format_str = 'bestvideo+bestaudio/best'
            print("选择画质: 最高可用画质")
        else:
            try:
                res_val = int(resolution.replace('p', '').replace('P', ''))
                format_str = f'bestvideo[height<={res_val}]+bestaudio/best[height<={res_val}]'
                print(f"选择画质: 不超过 {res_val}P (默认最高 1080P 如果可用)")
            except ValueError:
                # 默认回退到 1080
                format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                print("分辨率参数错误，使用默认 1080P")

        ydl_opts = {
            'format': format_str, 
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'), 
            'progress_hooks': [self.progress_hook],
            'noplaylist': True, 
            'ignoreerrors': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        # 移除内置 postprocessors，改为手动处理

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    print("\n提取失败: 无法获取视频信息")
                    return False
                
                title = info.get('title', 'Unknown')
                print(f"\n下载完成: {title}")
                
                # 获取下载后的文件路径
                downloaded_path = None
                if 'requested_downloads' in info:
                    downloaded_path = info['requested_downloads'][0]['filepath']
                else:
                    downloaded_path = ydl.prepare_filename(info)
                
                # 如果需要转码且文件路径存在
                if convert_to_mp4 and downloaded_path and os.path.exists(downloaded_path):
                    # 检查是否已经是 MP4
                    base, ext = os.path.splitext(downloaded_path)
                    if ext.lower() == '.mp4':
                        print("目标文件已是 MP4 格式，无需转换。")
                        return True
                        
                    output_path = base + ".mp4"
                    print(f"\n正在将视频转换为 MP4 格式 (H.264)...")
                    print(f"源文件: {downloaded_path}")
                    try:
                        self.convert_to_mp4_ffmpeg(downloaded_path, output_path)
                        print(f"转换成功: {os.path.basename(output_path)}")
                        
                        # 删除源文件
                        os.remove(downloaded_path)
                        print("已清理临时源文件。")
                    except Exception as e:
                        print(f"格式转换失败: {e}")
                        # 转换失败保留源文件
                
                return True
                
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
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
