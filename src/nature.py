"""
Nature 出版社下载方案
DOI前缀: 10.1038/
策略: 多级备选
  1. nature.com PDF直链
  2. nature.com article页面
  3. doi.org 重定向
  4. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载Nature论文PDF"""
    doi_suffix = doi.split('/', 1)[-1] if '/' in doi else doi
    urls = [
        f'https://www.nature.com/articles/{doi_suffix}.pdf',
        f'https://www.nature.com/articles/{doi_suffix}/pdf',
        f'https://www.nature.com/articles/{doi_suffix}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
