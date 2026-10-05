# Contributions

> Synced from `sections/01_introduction.tex` (conference Intro).

## Claim list

1. **C1 — Visual Hull Initialization**  
   Multi-view silhouettes → visual hull → stable point cloud prior for Gaussian initialization under sparse views.

2. **C2 — VGGT / Depth-Guided Densification**  
   Cross-view consistent depth → reliable regions → back-projected supplementary points → more complete 3DGS initialization.

3. **C3 — Dynamic Visibility Regularization**  
   Random Gaussian masking redistributes gradients; reduces foreground overfitting; strengthens updates for distant / weakly visible regions.  
   *(Intro does not claim opacity compensation; mechanism detail in Sec.~3.4 / DVR.)*

## Evidence mapping

| Claim | Experiment / figure / table | Status |
|-------|-----------------------------|--------|
| C1 | Table~\ref{tab:ablation} (Visual Hull Init) | draft |
| C2 | Table~\ref{tab:ablation} (Depth Densification; largest PSNR jump) | draft |
| C3 | Table~\ref{tab:ablation} (Visibility Balancing*); Fig.~\ref{fig:gradient} | draft |

## Naming notes

- Full module names in Intro; `(DVR)` first expanded in Sec.~3.1.
- No opacity compensation in Intro.
- Cite keys remain placeholders (`ref2`, `ref3`, …); bib alignment later.
