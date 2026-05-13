"""
Royal Society of Chemistry (RSC) 下载方案
DOI前缀: 10.1039/

注意：RSC 对 curl_cffi 的 impersonate 特征不友好（超时），
改用普通 requests 库反而能成功下载。

策略: 多级备选（优先使用Sci-Hub，更快更稳定）
  1. Sci-Hub 备选（优先，速度快）
  2. pubs.rsc.org articlepdf（通过doi.org重定向获取）
  3. pubs.rsc.org articlepdf 直链
  4. doi.org 重定向
"""
import re
import requests as std_requests
from . import scihub


def download(doi, filepath):
    """下载RSC论文PDF"""
    # 策略1: Sci-Hub（优先，RSC官方下载较慢）
    if scihub.download_via_scihub(doi, filepath):
        return True

    # 策略2: 通过 doi.org 获取 landing 页面 URL，构造 articlepdf URL
    doi_short = doi.replace('10.1039/', '')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://pubs.rsc.org/',
    }

    try:
        resp = std_requests.get(
            f'https://doi.org/{doi}',
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        final_url = resp.url
        pdf_url = final_url.replace('articlelanding', 'articlepdf')
        if pdf_url != final_url:
            pdf_resp = std_requests.get(
                pdf_url,
                headers=headers,
                timeout=60,
                allow_redirects=True
            )
            if (pdf_resp.status_code == 200
                    and len(pdf_resp.content) > 10000
                    and pdf_resp.content[:4] == b'%PDF'):
                with open(filepath, 'wb') as f:
                    f.write(pdf_resp.content)
                return True
    except Exception:
        pass

    # 策略3: 直接尝试常见格式
    urls = [
        f'https://pubs.rsc.org/en/content/articlepdf/{doi}',
        f'https://pubs.rsc.org/en/content/articlepdf/{doi_short}',
        f'https://doi.org/{doi}',
    ]

    for url in urls:
        try:
            resp = std_requests.get(
                url,
                headers=headers,
                timeout=60,
                allow_redirects=True
            )
            if (resp.status_code == 200
                    and len(resp.content) > 10000
                    and resp.content[:4] == b'%PDF'):
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception:
            continue

    return False
