
from curl_cffi import requests
import re
import json

# 原始 PC 链接 ID
video_id = "7598633843184143662"
# 移动端分享链接接口 (通常重定向到真实页面，或者直接返回数据)
mobile_url = f"https://www.iesdouyin.com/share/video/{video_id}/"

print(f"Testing URL: {mobile_url}")

try:
    # 模拟 Android 手机访问
    response = requests.get(
        mobile_url,
        impersonate="chrome120", # 使用 chrome 指纹，但 User-Agent 伪装成安卓
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        },
        allow_redirects=True,
        timeout=10
    )
    
    print(f"Final URL: {response.url}")
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    
    with open("douyin_mobile_test.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    # 检查是否依然是 WAF 页面
    if "byted_acrawler" in response.text:
        print("Blocked by WAF (Acrawler)")
    else:
        print("Success! Page content retrieved.")
        # 尝试提取 mp4
        mp4_matches = re.findall(r'https?://[^\s"\']*?\.mp4', response.text)
        if mp4_matches:
            print(f"Found {len(mp4_matches)} raw mp4 links.")
        
        # 尝试查找 the_json_data
        # 移动端页面通常把数据放在 <script id="RENDER_DATA">
        if "RENDER_DATA" in response.text:
             print("Found RENDER_DATA")

except Exception as e:
    print(f"Error: {e}")
