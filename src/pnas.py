"""
Proceedings of the National Academy of Sciences (PNAS) 下载方案
DOI前缀: 10.1073/
策略: 多级备选
  1. pnas.org PDF直链
  2. pnas.org article页面
  3. doi.org 重定向
  4. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载PNAS论文PDF"""
    urls = [
        f'https://www.pnas.org/doi/pdf/{doi}',
        f'https://www.pnas.org/doi/epdf/{doi}',
        f'https://www.pnas.org/doi/{doi}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
