# Agent 协作约定

## 目标

协助完成 ISIP 2027 / SPIE Proceedings 论文：3D Gaussian Splatting 相关方法、实验与投稿材料。

## 硬性规则

1. **不要修改** `spie.cls`、`spiebib.bst`。
2. 论文结构优先改 `main.tex` + `sections/*.tex`，避免把长文全塞进一个文件。
3. 参考文献只写进 `references.bib`，样式用 `spiebib`。
4. 不提交编译产物（`.aux` `.log` `.out` `.synctex.gz` `.bbl` `.blg` 等）。
5. 改动前先读 `notes/` 与 `docs/`，避免和已定大纲、投稿要求冲突。

## 建议工作流

1. 在 `notes/paper_outline.md` 定大纲与章节目标。
2. 在 `notes/contributions.md` 锁定贡献点表述。
3. 正文写入 `sections/`，实验数字写入 `data/`。
4. 投稿前用 `docs/ISIP_checklist.pdf` 自查。

## 文件职责

| 路径 | 职责 |
|------|------|
| `main.tex` | 标题、作者、导言区、章节 `\input`、参考文献入口 |
| `sections/` | 分章正文 |
| `figures/` `tables/` | 图表资产 |
| `data/` | 原始指标与实验笔记 |
| `notes/` | 写作计划，不进最终 PDF |
| `docs/` | 官方须知与样例，只读参考 |

