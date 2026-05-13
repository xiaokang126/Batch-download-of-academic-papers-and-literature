"""
论文PDF批量下载器 - 主入口

工作流程：
1. 扫描 unprocessed/ 文件夹中的 .xls 文件
2. 逐个处理每个文件中的论文
3. 根据DOI判断出版社，调用 src/ 中对应的下载方案
4. 处理完一个文件后，将其移动到 processed/ 文件夹

配置说明（修改下方 CONFIG 字典即可）：
- SKIP_PUBLISHERS: 要跳过的出版社（放弃下载）
- PRIORITY: 下载优先级，靠前的出版社先下载
- DELAY: 下载间隔（秒）
- REVERSE: 是否从后向前下载
"""
import os
import sys
import re
import time
import random
import shutil
import importlib
from collections import Counter
from datetime import datetime

import xlrd

from src.utils import get_publisher_from_doi, sanitize_filename, is_valid_pdf

# ============================================================
#  配置区 - 按需修改
# ============================================================
CONFIG = {
    # 待处理的xls文件夹
    'UNPROCESSED_DIR': r'd:\MyCodes\article_download\unprocessed',
    # 处理完的xls移到这里
    'PROCESSED_DIR': r'd:\MyCodes\article_download\processed',
    # PDF输出目录
    'OUTPUT_DIR': r'd:\MyCodes\article_download\articles',
    # 失败记录文件
    'FAILED_LOG': r'd:\MyCodes\article_download\failed_papers.txt',
    # 进度文件（断点续传）
    'PROGRESS_FILE': r'd:\MyCodes\article_download\download_progress.txt',

    # ===== 要跳过的出版社（直接放弃） =====
    # 在这里添加出版社名即可跳过，例如 {'aps', 'aip', 'wiley'}
    'SKIP_PUBLISHERS': set(),

    # ===== 下载优先级（靠前的先下载） =====
    'PRIORITY': ['nature', 'science', 'acs', 'rsc', 'iop',
                 'wiley', 'elsevier', 'springer', 'mdpi',
                 'pnas', 'oup', 'other'],

    # ===== 下载参数 =====
    'DELAY': 0.2,               # 下载间隔（秒），交错排列后只需短间隔
    'REVERSE': True,            # True=从后向前下载, False=从前向后
    'PDF_MIN_SIZE': 10000,      # 有效PDF最小字节数
    # ===== 交错排列 =====
    # 将相同出版社的论文间隔拉开，避免对同一服务器连续请求
    'INTERLEAVE': True,         # True=交错排列, False=按优先级顺序
    'INTERLEAVE_GAP': 3,        # 相同出版社论文之间的最小间隔数
}

# ============================================================
#  主程序
# ============================================================

def read_excel_papers(filepath):
    """读取xls文件中的论文列表"""
    papers = []
    wb = xlrd.open_workbook(filepath)
    sheet = wb.sheet_by_index(0)

    for row_idx in range(1, sheet.nrows):
        doi = str(sheet.cell_value(row_idx, 56)).strip()
        title = str(sheet.cell_value(row_idx, 8)).strip()
        source = str(sheet.cell_value(row_idx, 9)).strip()
        if doi and doi != '0.0' and doi != '':
            papers.append({
                'doi': doi,
                'title': title,
                'source': source,
            })
    return papers


def interleave_papers(papers, gap=3):
    """
    交错排列论文列表，使相同出版社的论文间隔拉开
    gap: 相同出版社论文之间的最小间隔数
    例如: [A,A,A,B,B,C] -> [A,B,A,C,A,B] (gap=2)
    """
    # 按出版社分组
    groups = {}
    for p in papers:
        pub = get_publisher_from_doi(p['doi'])
        if pub not in groups:
            groups[pub] = []
        groups[pub].append(p)

    # 按组大小降序排列（大的先排）
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    result = []
    # 记录每个出版社上次出现的位置
    last_pos = {}

    # 循环直到所有论文都被分配
    total = len(papers)
    remaining = {pub: len(items) for pub, items in groups.items()}

    while len(result) < total:
        best_pub = None
        best_pos = -1

        for pub, _ in sorted_groups:
            if remaining.get(pub, 0) == 0:
                continue

            # 检查是否满足间隔要求
            pos = len(result)
            last = last_pos.get(pub, -gap - 1)
            if pos - last > gap:
                best_pub = pub
                break

        if best_pub is None:
            # 所有出版社都不满足间隔，选剩余最多的
            best_pub = max(remaining, key=remaining.get)

        # 从该组取一篇
        result.append(groups[best_pub][len(groups[best_pub]) - remaining[best_pub]])
        remaining[best_pub] -= 1
        last_pos[best_pub] = len(result) - 1

    return result


def get_downloader(publisher):
    """动态导入出版社对应的下载模块"""
    try:
        module = importlib.import_module(f'src.{publisher}')
        return module.download
    except (ImportError, AttributeError):
        # 如果没有对应的模块，使用通用下载
        try:
            module = importlib.import_module('src.other')
            return module.download
        except (ImportError, AttributeError):
            return None


def download_paper(paper, output_dir, config):
    """下载单篇论文"""
    doi = paper['doi']
    title = paper['title']
    safe_title = sanitize_filename(title) if title else doi.replace('/', '_')
    filepath = os.path.join(output_dir, f'{safe_title}.pdf')

    # 检查是否已存在
    if is_valid_pdf(filepath):
        return True, 'already_exists'

    # 判断出版社
    publisher = get_publisher_from_doi(doi)

    # 检查是否在跳过列表中
    if publisher in config['SKIP_PUBLISHERS']:
        return False, f'skipped({publisher})'

    # 获取下载器并下载
    downloader = get_downloader(publisher)
    if downloader is None:
        return False, 'no_downloader'

    success = downloader(doi, filepath)
    if success:
        return True, f'{publisher}_ok'
    else:
        return False, f'{publisher}_failed'


def process_excel_file(filepath, config):
    """处理单个xls文件"""
    filename = os.path.basename(filepath)
    print(f'\n{"=" * 60}')
    print(f'[处理文件] {filename}')
    print(f'{"=" * 60}')

    # 读取论文
    papers = read_excel_papers(filepath)
    print(f'  共 {len(papers)} 篇论文')

    if not papers:
        print('  [跳过] 文件为空')
        return

    # 统计出版社分布
    publishers = Counter()
    for p in papers:
        publishers[get_publisher_from_doi(p['doi'])] += 1

    print('\n  出版社分布:')
    for pub, count in publishers.most_common():
        skip_mark = ' [跳过]' if pub in config['SKIP_PUBLISHERS'] else ''
        print(f'    {pub}: {count}篇{skip_mark}')

    # 按优先级排序
    priority = config['PRIORITY']
    def sort_key(p):
        pub = get_publisher_from_doi(p['doi'])
        try:
            return priority.index(pub)
        except ValueError:
            return len(priority)  # 不在优先级列表中的排最后

    papers.sort(key=sort_key)

    # 是否反转（从后向前）
    if config.get('REVERSE', False):
        papers.reverse()

    # 交错排列：将相同出版社的论文间隔拉开
    if config.get('INTERLEAVE', True):
        gap = config.get('INTERLEAVE_GAP', 3)
        papers = interleave_papers(papers, gap=gap)
        print(f'\n  交错排列: 已启用 (间隔={gap})')

    # 统计可下载数量
    downloadable = sum(1 for p in papers
                       if get_publisher_from_doi(p['doi']) not in config['SKIP_PUBLISHERS'])
    skipped_count = len(papers) - downloadable
    print(f'\n  可下载: {downloadable} 篇 | 跳过: {skipped_count} 篇')
    print(f'  下载顺序: {"从后向前" if config["REVERSE"] else "从前向后"}')

    # 开始下载
    success_count = 0
    fail_count = 0
    skip_count = 0
    failed_papers = []

    for i, paper in enumerate(papers, 1):
        # 检查是否在跳过列表中（快速跳过，不打印）
        publisher = get_publisher_from_doi(paper['doi'])
        if publisher in config['SKIP_PUBLISHERS']:
            skip_count += 1
            continue

        # 检查是否已存在（静默跳过）
        safe_title = sanitize_filename(paper['title']) if paper['title'] else paper['doi'].replace('/', '_')
        filepath = os.path.join(config['OUTPUT_DIR'], f'{safe_title}.pdf')
        if is_valid_pdf(filepath):
            success_count += 1
            continue

        # 打印进度
        print(f'\n[{i}/{len(papers)}] {paper["title"][:60]}...')
        print(f'  DOI: {paper["doi"]}')
        print(f'  期刊: {paper["source"]}')

        # 下载
        success, method = download_paper(paper, config['OUTPUT_DIR'], config)

        if success:
            success_count += 1
            size = os.path.getsize(filepath) // 1024
            print(f'  ✅ 成功! ({size}KB) 方法: {method}')
        else:
            if method.startswith('skipped'):
                skip_count += 1
                print(f'  ⏭️ 跳过: {method}')
            else:
                fail_count += 1
                failed_papers.append(paper)
                print(f'  ❌ 失败! ({method})')

        # 固定延时（交错排列后只需短间隔）
        if i < len(papers):
            time.sleep(config['DELAY'])

    # 输出文件级统计
    print(f'\n{"=" * 60}')
    print(f'[完成] {filename}')
    print(f'  成功: {success_count} | 失败: {fail_count} | 跳过: {skip_count} | 总计: {len(papers)}')

    # 保存失败记录
    if failed_papers:
        with open(config['FAILED_LOG'], 'a', encoding='utf-8') as f:
            f.write(f'\n\n文件: {filename}\n')
            f.write(f'处理时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'共 {len(failed_papers)} 篇失败\n')
            f.write('=' * 80 + '\n\n')
            for j, paper in enumerate(failed_papers, 1):
                pub = get_publisher_from_doi(paper['doi'])
                f.write(f'[{j}]\n')
                f.write(f'  标题: {paper["title"]}\n')
                f.write(f'  DOI: {paper["doi"]}\n')
                f.write(f'  期刊: {paper["source"]}\n')
                f.write(f'  出版社: {pub}\n')
                f.write(f'  URL: https://doi.org/{paper["doi"]}\n')
                f.write('\n')

    # 移动文件到 processed
    processed_path = os.path.join(config['PROCESSED_DIR'], filename)
    shutil.move(filepath, processed_path)
    print(f'  [归档] {filename} -> processed/')


def main():
    config = CONFIG
    os.makedirs(config['OUTPUT_DIR'], exist_ok=True)
    os.makedirs(config['PROCESSED_DIR'], exist_ok=True)

    print('=' * 60)
    print('  论文PDF批量下载器')
    print('=' * 60)
    print(f'\n配置:')
    print(f'  跳过出版社: {", ".join(config["SKIP_PUBLISHERS"])}')
    print(f'  下载优先级: {", ".join(config["PRIORITY"])}')
    print(f'  下载间隔: {config["DELAY"]}秒')
    print(f'  下载顺序: {"从后向前" if config["REVERSE"] else "从前向后"}')
    print(f'  PDF目录: {config["OUTPUT_DIR"]}')
    print(f'  待处理: {config["UNPROCESSED_DIR"]}')
    print(f'  已处理: {config["PROCESSED_DIR"]}')

    # 扫描 unprocessed 文件夹
    xls_files = [f for f in os.listdir(config['UNPROCESSED_DIR'])
                 if f.endswith('.xls') and os.path.isfile(os.path.join(config['UNPROCESSED_DIR'], f))]

    if not xls_files:
        print(f'\n[提示] unprocessed/ 文件夹中没有 .xls 文件')
        print(f'  请将 savedrecs 文件放入: {config["UNPROCESSED_DIR"]}')
        return

    # 按文件名排序
    xls_files.sort()
    print(f'\n发现 {len(xls_files)} 个待处理文件:')
    for f in xls_files:
        print(f'  - {f}')

    # 逐个处理
    total_success = 0
    total_fail = 0
    total_skip = 0

    for xls_file in xls_files:
        filepath = os.path.join(config['UNPROCESSED_DIR'], xls_file)
        process_excel_file(filepath, config)

    print(f'\n{"=" * 60}')
    print(f'  全部处理完成!')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()
