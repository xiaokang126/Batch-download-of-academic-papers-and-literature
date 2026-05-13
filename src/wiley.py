"""
Wiley 下载方案
DOI前缀: 10.1002/
策略: 多级备选
  1. onlinelibrary.wiley.com pdfdirect
  2. onlinelibrary.wiley.com pdf
  3. onlinelibrary.wiley.com epdf
  4. doi.org 重定向
  5. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载Wiley论文PDF"""
    urls = [
        f'https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}',
        f'https://onlinelibrary.wiley.com/doi/pdf/{doi}',
        f'https://onlinelibrary.wiley.com/doi/epdf/{doi}',
        f'https://onlinelibrary.wiley.com/doi/abs/{doi}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
