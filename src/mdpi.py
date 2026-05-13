"""
MDPI 下载方案
DOI前缀: 10.3390/
策略: 多级备选
  1. 通过doi.org获取article页面，提取citation_pdf_url
  2. mdpi.com PDF直链（多种格式）
  3. doi.org 重定向
  4. Sci-Hub 备选
"""
from curl_cffi import requests as curl_requests
import re
from . import scihub


def download(doi, filepath):
    """下载MDPI论文PDF"""
    # 策略1: 通过doi.org获取article页面，提取citation_pdf_url
    try:
        resp = curl_requests.get('https://doi.org/' + doi, impersonate='chrome131', timeout=30, allow_redirects=True)
        if resp.status_code == 200:
            cit = re.findall(r'citation_pdf_url[^>]*content=["\']([^"\']*)["\']', resp.text)
            if cit:
                pdf_url = cit[0]
                r = curl_requests.get(pdf_url, impersonate='chrome131', timeout=60, allow_redirects=True)
                if r.content[:4] == b'%PDF':
                    with open(filepath, 'wb') as f:
                        f.write(r.content)
                    return True
    except Exception:
        pass

    # 策略2: 尝试PDF直链
    doi_suffix = doi.split('/', 1)[-1] if '/' in doi else doi
    urls = [
        f'https://www.mdpi.com/{doi_suffix}/pdf',
        f'https://www.mdpi.com/{doi_suffix}',
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

    # 策略3: Sci-Hub
    if scihub.download_via_scihub(doi, filepath):
        return True

    return False
