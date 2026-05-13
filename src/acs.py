"""
American Chemical Society (ACS) 下载方案
DOI前缀: 10.1021/
策略: 多级备选
  1. pubs.acs.org PDF直链
  2. pubs.acs.org article页面提取PDF
  3. doi.org 重定向
  4. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载ACS论文PDF"""
    urls = [
        f'https://pubs.acs.org/doi/pdf/{doi}',
        f'https://pubs.acs.org/doi/epdf/{doi}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
