"""
American Physical Society (APS) 下载方案
DOI前缀: 10.1103/
策略: 多级备选
  1. journals.aps.org PDF直链
  2. link.aps.org PDF直链
  3. doi.org 重定向
  4. Sci-Hub 备选
"""
from curl_cffi import requests as curl_requests
from . import scihub


def download(doi, filepath):
    """下载APS论文PDF"""
    # 策略1: 尝试官方PDF直链
    try:
        urls = [
            f'https://journals.aps.org/prb/pdf/{doi}',
            f'https://journals.aps.org/pra/pdf/{doi}',
            f'https://journals.aps.org/prl/pdf/{doi}',
            f'https://journals.aps.org/rmp/pdf/{doi}',
            f'https://link.aps.org/pdf/{doi}',
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

    # 策略2: Sci-Hub 备选
    return scihub.download_via_scihub(doi, filepath)
