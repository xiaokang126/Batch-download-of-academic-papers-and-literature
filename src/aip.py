"""
American Institute of Physics (AIP) 下载方案
DOI前缀: 10.1063/
策略: 多级备选（优先使用Sci-Hub，更快更稳定）
  1. Sci-Hub 备选（优先，速度快）
  2. 通过doi.org获取article页面，提取citation_pdf_url
  3. pubs.aip.org PDF直链
  4. doi.org 重定向
"""
from curl_cffi import requests as curl_requests
import re
from . import scihub


def download(doi, filepath):
    """下载AIP论文PDF"""
    # 策略1: Sci-Hub（优先，AIP官方有Cloudflare保护）
    if scihub.download_via_scihub(doi, filepath):
        return True

    # 策略2: 通过doi.org重定向到article页面，提取citation_pdf_url
    try:
        resp = curl_requests.get('https://doi.org/' + doi, impersonate='chrome131', timeout=30, allow_redirects=True)
        if resp.status_code == 200:
            cit = re.findall(r'citation_pdf_url[^>]*content=["\']([^"\']*)["\']', resp.text)
            if cit:
                pdf_url = cit[0]
                # 添加referer
                r = curl_requests.get(pdf_url, impersonate='chrome131', timeout=60, 
                                      allow_redirects=True,
                                      headers={'Referer': resp.url})
                if r.content[:4] == b'%PDF':
                    with open(filepath, 'wb') as f:
                        f.write(r.content)
                    return True
    except Exception:
        pass

    # 策略3: 尝试PDF直链
    try:
        urls = [
            f'https://pubs.aip.org/aip/article-pdf/doi/{doi}',
            f'https://aip.scitation.org/doi/pdf/{doi}',
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
    except Exception:
        pass

    return False
