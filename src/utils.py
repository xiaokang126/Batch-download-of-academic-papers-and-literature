"""
公共工具函数
"""
import os
import re

# ============ DOI前缀 -> 出版社映射 ============
DOI_PUBLISHER_MAP = [
    ('10.1103/', 'aps'),
    ('10.1038/', 'nature'),
    ('10.1126/', 'science'),
    ('10.1021/', 'acs'),
    ('10.1016/', 'elsevier'),
    ('10.1088/', 'iop'),
    ('10.1007/', 'springer'),
    ('10.3390/', 'mdpi'),
    ('10.1063/', 'aip'),
    ('10.1073/', 'pnas'),
    ('10.1093/', 'oup'),
    ('10.1002/', 'wiley'),
    ('10.1039/', 'rsc'),
]


def get_publisher_from_doi(doi):
    """根据DOI前缀判断出版社"""
    doi_lower = doi.lower().strip()
    for prefix, publisher in DOI_PUBLISHER_MAP:
        if doi_lower.startswith(prefix):
            return publisher
    return 'other'


def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    if len(filename) > 180:
        filename = filename[:180]
    return filename.strip('._ ')


def is_valid_pdf(filepath):
    """检查文件是否为有效的PDF（存在且大于10KB）"""
    return os.path.exists(filepath) and os.path.getsize(filepath) > 10000
