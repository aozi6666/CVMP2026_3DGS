# ISIP2027_3DGS

面向 **ISIP 2027 / SPIE Proceedings** 的 3D Gaussian Splatting 论文仓库。  
正文用 SPIE 官方 LaTeX 模板（`spie.cls` + `spiebib.bst`），材料和实验笔记分区存放。

---

## 快速开始

```bash
# 编译（需本机 TeX Live / MacTeX）
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

当前 `main.tex` 仍是官方样例稿；改成自己的论文后，把 `\bibliography{report}` 改为 `\bibliography{references}`。

---

## 目录结构

```text
ISIP2027_3DGS/
├── main.tex                 # 总入口（结构 / 导言区）
├── spie.cls                 # SPIE 官方 class（勿改）
├── spiebib.bst              # SPIE 参考文献样式（勿改）
├── references.bib           # 正式参考文献（由 report.bib 迁入）
│
├── sections/                # 分章正文
│   ├── 01_introduction.tex
│   ├── 02_related_work.tex
│   ├── 03_method.tex
│   ├── 04_experiments.tex
│   └── 05_conclusion.tex
│
├── figures/                 # 插图
├── tables/                  # 表格片段
├── data/                    # 实验记录与指标
├── docs/                    # 投稿须知 / checklist / 样例 PDF
├── notes/                   # 大纲、贡献点、待办
│
├── AGENTS.md                # Agent 协作约定
└── README.md
```

---

## 官方模板：哪些可复用

来源：`SPIE-模板-LATEX-3.0` + 会议投稿材料包。

| 文件 | 处理 | 说明 |
|------|------|------|
| `spie.cls` | ✅ 已用 | 官方样式，**不要改** |
| `spiebib.bst` | ✅ 已用 | BibTeX 样式，**不要改** |
| `main.tex` | ✅ 已用 | 样例入口，后续改成论文骨架 |
| `report.bib` | ✅ → `references.bib` | 保留条目格式作参考，再换成自己的文献 |
| `mcr3b.eps` | ✅ → `figures/` | 样例图，确认 `\includegraphics` 路径后可删 |
| `MultimediaFigure.jpg` | ✅ → `figures/` | 多媒体插图样例 |
| `main.pdf` | ✅ → `docs/SPIE_template_sample.pdf` | 排版对照 |
| Checklist / 投稿须知 / Word 模板 | ✅ → `docs/` | 投稿自查用 |
| `main.aux` / `.log` / `.out` / `.synctex.gz` | ❌ 不入库 | 本地编译产物，已进 `.gitignore` |

---

## 写作约定

- **正文**：写在 `sections/*.tex`，由 `main.tex` `\input` 引入。
- **图**：放 `figures/`，优先 PDF / PNG；EPS 仅在必要时保留。
- **表**：复杂表拆到 `tables/`，实验结果先记在 `data/`。
- **投稿前**：对照 `docs/ISIP_checklist.pdf` 与 `docs/submission_notice.pdf`。

---

## 状态

| 模块 | 状态 |
|------|------|
| SPIE 模板骨架 | 已就绪 |
| 分章 / 笔记 / data 占位 | 已建空壳 |
| 论文内容改写 | 待开始 |
| 正式实验与图表 | 待填入 |
