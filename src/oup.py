"""
Oxford University Press (OUP) 下载方案
DOI前缀: 10.1093/
策略: 多级备选
  1. Sci-Hub（优先，doi.org有Cloudflare保护）
  2. academic.oup.com PDF直链
  3. academic.oup.com article页面
  4. doi.org 重定向
"""
from curl_cffi import requests as curl_requests
from . import scihub


def download(doi, filepath):
    """下载OUP论文PDF"""
    # 策略1: Sci-Hub（优先，doi.org有Cloudflare保护）
    if scihub.download_via_scihub(doi, filepath):
        return True

    # 策略2: 尝试PDF直链
    doi_suffix = doi.split('/', 1)[-1] if '/' in doi else doi
    urls = [
        f'https://academic.oup.com/{doi_suffix}/pdf',
        f'https://academic.oup.com/{doi_suffix}/article-pdf',
        f'https://academic.oup.com/{doi_suffix}',
        f'https://doi.org/{doi}',
    ]
    for url in urls:
        try:
            r = curl_requests.get(url, impersonate='chrome131', timeout=30, allow_redirects=True)
            if r.content[:4] == b'%PDF':
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
        except Exception:
            continue

    return False
