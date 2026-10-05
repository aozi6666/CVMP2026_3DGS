# Paper Outline

> 论文大纲（不进入最终 PDF）。随写作进度更新。

## Working title

TBD — 3D Gaussian Splatting / ISIP 2027

## Sections

### 1. Introduction
- Problem / motivation: sparse-view underconstraint — drafted
- 3DGS background + SfM init limits — drafted
- SynGS + three named modules — drafted
- Contributions: itemize C1–C3 — drafted (`notes/contributions.md` synced)

### 2. Related Work
- Classical / NeRF-style:
- 3DGS and variants:
- Sparse-view / geometry priors (if relevant):

### 3. Method
- 3.1 Overall Framework — drafted; first expand **DVR** here
- 3.2 Visual Hull Initialization — drafted
- 3.3 VGGT / Depth-Guided Densification — drafted (trained adaptation + cross-attention)
- 3.4 Dynamic Visibility Regularization — drafted (`eq:dropout_ratio`, `eq:dvr_loss`; Fig.3 omitted by default)
- Figure: `figures/framework.pdf` (pending; `fig:framework`)
- Figure: `figures/vggt_depth.pdf` (pending; `fig:vggt_depth`)
- Fig.3 / `fig:dvr` — conference default: **omit**
- Eqs: `eq:pipeline`, `eq:delta_d`, `eq:dropout_ratio`, `eq:dvr_loss`

### 4. Experiments
- 4.1 Experimental Setup and Datasets — drafted (baselines → Tables 1–2; LLFF 360; VGGT + GT depth)
- 4.2 Quantitative and Qualitative Results — drafted (merged; compact Gradient; honest LPIPS / 9-view)
- 4.3 Ablation Study — drafted (Visibility Balancing* = DVR; PSNR chain in text)
- Tables: `mip360_results` / `llff_results` / `ablation` shells — **paste numbers from manuscript**
- Figs: `fig:gradient`, `fig:qualitative` (one-row, Mip-NeRF 360 4-view) — pending files


### 5. Conclusion
- Summary:
- Limitations:
- Future work:

## Target length / venue notes

- Venue: ISIP 2027 → SPIE Proceedings format
- Check: `docs/ISIP_checklist.pdf`, `docs/submission_notice.pdf`
