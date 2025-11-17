import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def download_main(fin_pic, download_dir):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }
    
    # 创建带重试机制的session
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # 总共重试3次
        backoff_factor=1,  # 重试间隔：1秒、2秒、4秒
        status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码会触发重试
        allowed_methods=["GET"]  # 只对GET请求重试
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    for index, url in enumerate(fin_pic):
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                response = session.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()

                file_name = f'image_{index+1}.jpg'
                full_path = os.path.join(download_dir, file_name)

                with open(full_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"✅ 图片下载成功: {full_path}")
                success = True

            except requests.exceptions.SSLError as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # 指数退避：2秒、4秒、8秒
                    print(f"   SSL错误，第 {retry_count} 次重试（等待 {wait_time} 秒）...")
                    time.sleep(wait_time)
                else:
                    print(f"!! 下载第 {index + 1} 张图片失败 (SSL错误，已重试 {max_retries} 次): {e}")
                    
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"   网络错误，第 {retry_count} 次重试（等待 {wait_time} 秒）...")
                    time.sleep(wait_time)
                else:
                    print(f"!! 下载第 {index + 1} 张图片失败 (网络错误，已重试 {max_retries} 次): {e}")
        
        if not success:
            continue

