"""
IOP Publishing 下载方案
DOI前缀: 10.1088/
策略: 多级备选
  1. iopscience.iop.org PDF直链
  2. iopscience.iop.org article页面提取PDF
  3. doi.org 重定向
  4. Sci-Hub 备选（由curl_downloader自动处理）
"""
from . import curl_downloader


def download(doi, filepath):
    """下载IOP论文PDF"""
    urls = [
        f'https://iopscience.iop.org/article/{doi}/pdf',
        f'https://iopscience.iop.org/article/{doi}/pdfdownload',
        f'https://iopscience.iop.org/article/{doi}',
        f'https://doi.org/{doi}',
    ]
    return curl_downloader.try_urls(urls, filepath)
