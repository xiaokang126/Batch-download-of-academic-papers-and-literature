"""
Springer 下载方案
DOI前缀: 10.1007/
策略: 多级备选
  1. link.springer.com PDF直链
  2. doi.org 重定向
  3. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载Springer论文PDF"""
    urls = [
        f'https://link.springer.com/content/pdf/{doi}.pdf',
        f'https://link.springer.com/content/pdf/{doi}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
