"""
其他出版社通用下载方案
（无法通过DOI前缀识别的出版社）
策略: 多级备选
  1. Sci-Hub（优先，doi.org常有Cloudflare保护）
  2. doi.org 重定向
"""
from curl_cffi import requests as curl_requests
from . import scihub


def download(doi, filepath):
    """通用下载：多级备选"""
    # 策略1: Sci-Hub（优先，doi.org常有Cloudflare保护）
    if scihub.download_via_scihub(doi, filepath):
        return True

    # 策略2: 通过doi.org重定向
    try:
        resp = curl_requests.get('https://doi.org/' + doi, impersonate='chrome131', timeout=30, allow_redirects=True)
        if resp.content[:4] == b'%PDF':
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception:
        pass

    return False
