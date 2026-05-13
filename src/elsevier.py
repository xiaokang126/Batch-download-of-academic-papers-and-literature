"""
Elsevier 下载方案
DOI前缀: 10.1016/
策略: 多级备选
  1. 通过article页面获取md5/pid，尝试pdfft
  2. doi.org 重定向
  3. Sci-Hub 备选
"""
from curl_cffi import requests as curl_requests
import re, json
from . import scihub


def download(doi, filepath):
    """下载Elsevier论文PDF"""
    pii = ''
    pii_match = re.search(r'10\.1016/([a-z0-9]+)', doi, re.IGNORECASE)
    if pii_match:
        pii = pii_match.group(1)

    # 策略1: 通过article页面获取md5/pid，尝试pdfft
    if pii:
        try:
            resp = curl_requests.get(
                'https://www.sciencedirect.com/science/article/pii/' + pii,
                impersonate='chrome131', timeout=30, allow_redirects=True
            )
            if resp.status_code == 200:
                match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*({.*?});', resp.text, re.DOTALL)
                if match:
                    state = json.loads(match.group(1))
                    pdf_info = state.get('article', {}).get('pdfDownload', {})
                    url_meta = pdf_info.get('urlMetadata', {})
                    md5 = url_meta.get('queryParams', {}).get('md5', '')
                    pid = url_meta.get('queryParams', {}).get('pid', '')
                    pdf_ext = url_meta.get('pdfExtension', '/pdfft')

                    if md5 and pid:
                        pdf_url = f'https://www.sciencedirect.com/science/article/pii/{pii}{pdf_ext}?md5={md5}&pid={pid}'
                        r = curl_requests.get(pdf_url, impersonate='chrome131', timeout=30, allow_redirects=True)
                        if r.content[:4] == b'%PDF':
                            with open(filepath, 'wb') as f:
                                f.write(r.content)
                            return True
        except Exception:
            pass

    # 策略2: 尝试doi.org
    try:
        r = curl_requests.get('https://doi.org/' + doi, impersonate='chrome131', timeout=30, allow_redirects=True)
        if r.content[:4] == b'%PDF':
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return True
    except Exception:
        pass

    # 策略3: Sci-Hub 备选
    return scihub.download_via_scihub(doi, filepath)
