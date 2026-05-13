# Paper PDF Downloader

批量下载学术论文PDF的工具。支持从 Web of Science 导出的 `.xls` 文件中读取论文信息，自动识别出版社并下载PDF全文。

## 功能特点

- 🚀 **批量下载**：支持从 Excel 文件批量读取论文信息并下载
- 🎯 **智能识别**：自动识别 DOI 所属出版社，使用对应的下载策略
- 🔄 **多级备选**：每个出版社都有多级下载策略，失败自动切换备选方案
- ⚡ **交错排列**：相同出版社的论文间隔下载，避免触发反爬机制
- 📊 **进度统计**：实时显示下载进度、成功/失败统计
- 📁 **文件管理**：自动归档已处理的文件，支持断点续传

## 支持的出版社

| 出版社 | 覆盖率 | 下载策略 |
|--------|:------:|---------|
| **Nature** | ✅ 高 | 官方站点 + Sci-Hub |
| **Science** | ✅ 高 | 官方站点 + Sci-Hub |
| **ACS** | ✅ 高 | 官方站点 + Sci-Hub |
| **RSC** | ✅ 高 | 官方站点 + Sci-Hub |
| **IOP** | ✅ 高 | 官方站点 + Sci-Hub |
| **Wiley** | ✅ 高 | 官方站点 + Sci-Hub |
| **Springer** | ✅ 高 | 官方站点 + Sci-Hub |
| **MDPI** | ✅ 高 | 官方站点 + Sci-Hub |
| **PNAS** | ✅ 高 | 官方站点 + Sci-Hub |
| **APS** | ⚠️ 中 | 官方站点 + Sci-Hub |
| **Elsevier** | ⚠️ 中 | 官方站点 + Sci-Hub |
| **AIP** | ⚠️ 中 | 官方站点 + Sci-Hub |
| **OUP** | ⚠️ 低 | 官方站点 + Sci-Hub |
| **其他** | ⚠️ 中 | 通用策略 + Sci-Hub |

> 整体成功率约 **80%**（基于1317篇论文测试）。失败原因主要是论文需要付费订阅且Sci-Hub未收录。

## 安装

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install xlrd requests curl_cffi
```

## 使用方法

### 1. 准备数据

从 Web of Science 导出论文信息为 `.xls` 格式（推荐导出时选择"全记录与引用的参考文献"）。

### 2. 放入待处理目录

将 `.xls` 文件放入 `unprocessed/` 目录：

```
unprocessed/
└── my_papers.xls
```

### 3. 运行下载

```bash
python main.py
```

### 4. 查看结果

- 下载的PDF保存在 `articles/` 目录
- 处理完成的 `.xls` 文件自动移至 `processed/` 目录

## 项目结构

```
paper-pdf-downloader/
├── main.py                 # 主入口
├── src/
│   ├── __init__.py
│   ├── utils.py           # 工具函数（出版社识别等）
│   ├── curl_downloader.py # 下载引擎
│   ├── scihub.py          # Sci-Hub 下载
│   ├── nature.py          # Nature 下载
│   ├── science.py         # Science 下载
│   ├── acs.py             # ACS 下载
│   ├── rsc.py             # RSC 下载
│   ├── iop.py             # IOP 下载
│   ├── wiley.py           # Wiley 下载
│   ├── springer.py        # Springer 下载
│   ├── elsevier.py        # Elsevier 下载
│   ├── aps.py             # APS 下载
│   ├── aip.py             # AIP 下载
│   ├── mdpi.py            # MDPI 下载
│   ├── pnas.py            # PNAS 下载
│   ├── oup.py             # OUP 下载
│   └── other.py           # 其他出版社通用下载
├── articles/              # 下载的PDF（已加入 .gitignore）
├── processed/             # 已处理的xls文件
└── unprocessed/           # 待处理的xls文件
```

## 注意事项

- ⚠️ 下载的PDF论文受版权保护，请仅用于个人学习和研究
- ⚠️ 请遵守各出版社的使用条款，不要高频请求
- ⚠️ Sci-Hub 在某些国家/地区可能被限制访问

## License

MIT
