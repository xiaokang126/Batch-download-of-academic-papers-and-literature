"""
curl_cffi 通用下载引擎
所有使用 curl_cffi 的出版社都通过此模块下载
自动添加 Sci-Hub 作为最终备选
"""
import os
from . import scihub


def try_urls(urls, filepath, use_scihub_fallback=True):
    """
    尝试多个URL下载PDF
    如果所有URL都失败，自动使用Sci-Hub作为备选
    返回: True=成功, False=失败
    """
    try:
        from curl_cffi import requests as curl_requests
    except ImportError:
        print('  [错误] 未安装 curl_cffi，请执行: pip install curl_cffi')
        return False

    for url in urls:
        try:
            resp = curl_requests.get(
                url,
                impersonate="chrome131",
                timeout=30,
                allow_redirects=True
            )
            if (resp.status_code == 200
                    and len(resp.content) > 10000
                    and resp.content[:4] == b'%PDF'):
                with open(filepath, 'wb') as f:
                    f.write(resp.content)
                return True
        except Exception:
            continue

    # 所有URL都失败，使用Sci-Hub备选
    if use_scihub_fallback:
        # 从urls中提取doi（最后一个通常是doi.org的）
        for url in reversed(urls):
            if '/doi.org/' in url or '/doi/' in url:
                doi = url.split('/doi/')[-1].split('?')[0].split('#')[0]
                if scihub.download_via_scihub(doi, filepath):
                    return True
                break

    return False
