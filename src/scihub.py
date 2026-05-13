"""
Sci-Hub 下载方案
作为其他出版社的备选下载方案
"""
from curl_cffi import requests as curl_requests
import re
import os

# Sci-Hub 域名列表
SCI_HUB_DOMAINS = [
    'https://sci-hub.ru',
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ee',
]


def download_via_scihub(doi, filepath, timeout=120):
    """通过Sci-Hub下载论文PDF"""
    for domain in SCI_HUB_DOMAINS:
        try:
            # 访问sci-hub页面
            url = domain + '/' + doi
            resp = curl_requests.get(url, impersonate='chrome131', timeout=60, allow_redirects=True)
            
            if resp.status_code != 200:
                continue
            
            # 提取citation_pdf_url
            cit = re.findall(r'citation_pdf_url[^>]*content=["\']([^"\']*)["\']', resp.text)
            if not cit:
                continue
            
            pdf_url = cit[0]
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif pdf_url.startswith('/'):
                pdf_url = domain + pdf_url
            
            # 下载PDF
            r = curl_requests.get(pdf_url, impersonate='chrome131', timeout=timeout, allow_redirects=True)
            
            if r.content[:4] == b'%PDF':
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                return True
                
        except Exception:
            continue
    
    return False
