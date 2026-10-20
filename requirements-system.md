# System & CLI requirements (not pip)

本仓库主体是 **SPIE LaTeX 论文**；Python 只服务 Word 导出与表格脚本。  
`pip install -r requirements.txt` 装不了下面这些，需本机单独安装。

## 1. 必装：编译 PDF

| 工具 | 用途 | 安装示例 |
|------|------|----------|
| **TeX Live / MacTeX** | 完整 LaTeX 发行版 | macOS: [MacTeX](https://tug.org/mactex/) 或 `brew install --cask mactex` |
| `pdflatex` | 编译 `main.tex` | 随 TeX 发行版 |
| `bibtex` | 处理 `references.bib` | 随 TeX 发行版 |

一键编译：

```bash
./build_output.sh
# 或
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

### LaTeX 宏包（`main.tex` / `spie.cls` 实际用到）

仓库已自带：`spie.cls`、`spiebib.bst`、`authblk.sty`。

其余一般在完整 TeX Live / MacTeX 中已有；若缺包可用 `tlmgr install <name>`：

| 包名 | 说明 |
|------|------|
| `times` / `mathptmx`（psnfss） | Times 正文字体与数学 |
| `amsmath` `amsfonts` `amssymb` | 公式 |
| `graphicx` | 插图 |
| `booktabs` `multirow` `adjustbox` | 表格 |
| `float` | 浮动体 |
| `xcolor` `colortbl` | 表格着色（`[table]`） |
| `soul` | 修订高亮 `\hl` / `\rev` |
| `hyperref` | 超链接（`hidelinks`） |
| `cite` | `spie.cls` 引用压缩 |

可选：`latexmk`（自动多遍编译）。

## 2. 导出 Word 时需要

| 工具 | 用途 | 安装示例 |
|------|------|----------|
| **Python 3.10+**（本机曾用 3.12） | 跑脚本 | `brew install python` |
| **pandoc** | `build_spie_word.py` 调 Markdown→docx | `brew install pandoc` |
| `python-docx` 等 | 见 `requirements.txt` | `pip install -r requirements.txt` |

```bash
python3 -m venv .venv_word
source .venv_word/bin/activate
pip install -r requirements.txt
python build_spie_word.py
```

前提：已用 `pdflatex`+`bibtex` 生成过 `main.bbl`；Word 插图在 `figures/word_export/*.png`。

## 3. 文献核验：`curl` + arXiv API

本仓库**没有**独立文献检索 CLI；写 `references.bib` 时用系统自带的 `curl` 核对 arXiv / OpenAccess 元数据（题名、作者、DOI），避免编造字段。清单见 `notes/refs_search_todo.md`。

| 工具 | 用途 | 安装 |
|------|------|------|
| `curl` | 拉 arXiv atom / abs 页做题名与 id 核验 | macOS / Linux 通常自带 |
| arXiv API | `http://export.arxiv.org/api/query?id_list=<id>` | 无需安装，需网络 |

示例：

```bash
# 按 arXiv id 查题名与作者（把 2402.14650 换成目标 id）
curl -sL "http://export.arxiv.org/api/query?id_list=2402.14650" | head -n 40

# 快速打开摘要页（浏览器或下载 HTML）
curl -sI "https://arxiv.org/abs/2402.14650"
```

规则（与 `notes/` 约定一致）：只写入能核到的字段；核不到不编造；`bibtex` 只负责编译，不负责检索。

## 4. 可选 / 本机常用但不进脚本硬依赖

| 工具 | 用途 |
|------|------|
| `pdftoppm` / Poppler | PDF 页转 PNG（准备 `word_export` 图时可能用到） |
| ImageMagick (`convert`/`magick`) | 图格式转换 |
| macOS `textutil` | 抽 Word 纯文本（调试用） |

## 5. 最小复现清单

**只编 PDF：** TeX Live + 仓库内 `spie.cls` / `spiebib.bst` / `authblk.sty`。

**PDF + SPIE Word：** 上面 + Python 3 + `pip install -r requirements.txt` + pandoc。

**文献核验：** `curl` + 网络访问 arXiv API（无额外 pip 包）。
