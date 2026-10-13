# SynGS 审稿修改说明 / Revision Change Log

**对照文件 / Reference:** `output/SynGS_revised_highlighted.pdf`（黄底 = 本次修改）  
**审稿日期 / Review date:** 2026-10-12  
**修改类型 / Revision type:** 文案小修（不改方法、表格数字、实验设置）

---

## 审稿意见与回应总览 / Response Overview

| 审稿意见 Reviewer comment | 我们的修改 How we addressed it |
|---------------------------|--------------------------------|
| 新颖性相对已有方法不够清晰；与现有方法的区别需进一步阐明 | Introduction 增加定位段；三条贡献改为对比式表述；Related Work 末尾补一句边界说明 |
| 未在全部指标上全面最优；性能优势表述应更谨慎 | Abstract 末句条件化；§4.2 保留原骨架并承认 LPIPS/9-view trade-off、收束更谨慎；Conclusion 同步弱化笼统 claim |

**未改动 / Unchanged:** Method 技术正文、Tables 1–3 数值、图、参考文献列表。

---

## 1. Abstract（摘要，少改）

**位置：** Abstract 末句  
**目的：** 避免读成“全面最优”；增益绑定到 4-view vs D²GS，并说明并非所有指标/视角均第一。

**原文是：**  
On the Mip-NeRF 360 dataset, SynGS achieves gains of up to 3.56 dB in PSNR and 0.025 in SSIM under sparse-view settings.

**中文：**  
在 Mip-NeRF 360 数据集上，SynGS 在稀疏视角设置下最高可取得约 3.56 dB 的 PSNR 提升以及 0.025 的 SSIM 提升。

**修改后：**  
On Mip-NeRF 360, SynGS demonstrates consistent improvements in PSNR and SSIM across the evaluated sparse-view settings, with gains of 3.56 dB in PSNR and 0.025 in SSIM over a leading baseline using only four input views. On LLFF, the improvements are more pronounced in the four- and six-view settings, while the nine-view results remain comparable to those of leading existing methods.

**中文：**  
在 Mip-NeRF 360 上，SynGS 在所评估的稀疏视角设置中均在 PSNR 与 SSIM 上取得一致提升，其中在仅 4 视角输入时相对某一领先基线的增益为 PSNR +3.56 dB、SSIM +0.025。在 LLFF 上，提升在 4 与 6 视角设置更为明显，而 9 视角结果与现有领先方法保持可比。

---

## 2. Introduction — 新颖性定位（短定位段）

**位置：** 贡献列表之前（整段替换原文过渡句 + 旧长定位段）  
**目的：** 短写边界与 gap；三项技术细节留给 Contributions。

**原文是：**  
Existing sparse-view methods explore depth regularization and densification, or co-regularization and Gaussian dropout, but still struggle with fine structures and geometric consistency. We present SynGS, which strengthens Gaussian initialization with explicit geometric constraints and depth-guided densification, and applies Dynamic Visibility Regularization to reduce overfitting.

**中文：**  
现有稀疏视角方法主要探索深度正则与稠密化，或共正则与高斯 dropout，但在细结构与几何一致性上仍有不足。我们提出 SynGS，通过显式几何约束与深度引导稠密化加强高斯初始化，并采用动态可见性正则以减轻过拟合。

**修改后：**  
Existing sparse-view methods have explored depth regularization, Gaussian densification, co-regularization, and Gaussian dropout to improve reconstruction. Nevertheless, incomplete initial geometry and overfitting during optimization remain challenges when only a few observations are available. To address these issues, we propose SynGS, a sparse-view 3DGS framework that combines geometry-guided Gaussian initialization with training-time regularization. By strengthening initial geometric support and mitigating overfitting during optimization, SynGS improves reconstruction robustness under severely limited view coverage.

**中文：**  
现有稀疏视角方法已探索深度正则、高斯稠密化、共正则与高斯 dropout 以改善重建。然而，在观测极少时，初始几何不完整与优化阶段过拟合仍是挑战。为此，我们提出 SynGS：一种将几何引导的高斯初始化与训练期正则相结合的稀疏视角 3DGS 框架。通过加强初始几何支撑并在优化中缓解过拟合，SynGS 提升在视角覆盖严重受限时的重建鲁棒性。

---

## 3. Introduction — 三条贡献（差异化重写）

**位置：** Contributions bullet list  
**目的：** 每条用 Unlike / Complementary to 写清相对谁不同。

**说明：** 贡献三条**标题仍用旧名**（Visual Hull / VGGT-Guided Densification / DVR）；仅替换解释句。引导句保持 `The main contributions are:`。定位段已改为短版，细节由本三条承担。

### 3.1 Visual Hull Initialization

**原文是：**  
We construct a visual hull from multi-view silhouettes as a stable geometric prior for Gaussian initialization.

**中文：**  
我们从多视角轮廓构建视觉外壳（visual hull），作为高斯初始化的稳定几何先验。

**修改后：**  
We incorporate a visual hull derived from multi-view silhouettes to provide an explicit geometric constraint for Gaussian initialization. This constraint complements incomplete SfM observations and helps establish a more reliable initial spatial distribution of Gaussian primitives.

**中文：**  
我们引入由多视角轮廓得到的视觉外壳，为高斯初始化提供显式几何约束。该约束互补不完整的 SfM 观测，并有助于建立更可靠的高斯基元初始空间分布。

### 3.2 VGGT-Guided Densification

**原文是：**  
We back-project cross-view consistent depth predictions to supplement missing geometry for Gaussian initialization.

**中文：**  
我们将跨视角一致的深度预测反投影，以补充缺失几何，用于高斯初始化。

**修改后：**  
We develop a pre-optimization densification strategy that back-projects cross-view-consistent depth estimates from VGGT to supplement the sparse initial point set. By introducing additional geometric samples before training, this strategy improves geometric coverage in under-observed regions.

**中文：**  
我们提出训练前（pre-optimization）稠密化策略：将 VGGT 得到的跨视角一致深度估计反投影，以补充稀疏初始点集。通过在训练前引入额外几何采样，该策略改善欠观测区域的几何覆盖。

### 3.3 Dynamic Visibility Regularization

**原文是：**  
We randomly mask Gaussian primitives during training to rebalance gradients and alleviate sparse-view overfitting.

**中文：**  
我们在训练中随机掩蔽高斯基元，以重新平衡梯度并缓解稀疏视角过拟合。

**修改后：**  
We incorporate Dynamic Visibility Regularization during training to stochastically mask Gaussian primitives, redistribute optimization gradients, and mitigate overfitting under limited-view supervision. This regularization complements the geometry-enhanced initialization to improve the robustness of sparse-view reconstruction.

**中文：**  
我们在训练中引入动态可见性正则，随机掩蔽高斯基元、重分配优化梯度，并缓解有限视角监督下的过拟合。该正则与几何增强后的初始化相互补充，以提升稀疏视角重建的鲁棒性。

---

## 4. Related Work — 第 2 段小润色 + 第 3 段收束（新颖性）

**位置：** Related Work 第 2 段局部；第 3 段收束（替换原 SynGS 句）  
**目的：** 前两段少动；第 3 段用 gap + SynGS 定位阐明新颖性；不新增文献。

### 4.1 第 2 段（两处小润色）

**原文是：**  
Depth-based approaches add geometric supervision. densification-based methods improve Gaussian coverage, including progressive geometric propagation, gradient-aware density control, and epipolar depth priors.

**中文：**  
基于深度的方法加入几何监督；基于稠密化的方法改善高斯覆盖，其中包括渐进几何传播、梯度感知密度控制以及极线深度先验。

**修改后：**  
Depth-based approaches introduce additional geometric supervision, while densification-based methods improve Gaussian coverage. Other strategies include progressive geometric propagation, gradient-aware density control, and epipolar depth priors.

**中文：**  
基于深度的方法引入额外几何监督，而基于稠密化的方法改善高斯覆盖。其他策略还包括渐进几何传播、梯度感知密度控制以及极线深度先验。

### 4.2 第 3 段收束（替换）

**原文是：**  
SynGS instead adapts a VGGT-based multi-view depth prior together with explicit visual-hull initialization and dynamic visibility regularization for more stable sparse-view 3DGS reconstruction.

**中文：**  
SynGS 则采用基于 VGGT 的多视角深度先验，并结合显式视觉外壳初始化与动态可见性正则，以实现更稳定的稀疏视角 3DGS 重建。

**修改后：**  
Although depth supervision, Gaussian densification, and training-time regularization have improved sparse-view reconstruction, limited-view observations can still result in incomplete initial geometry and overfitting during optimization. To address these challenges, SynGS combines explicit visual-hull constraints with a VGGT-based multi-view depth prior to augment the initial Gaussian geometry before optimization, and incorporates Dynamic Visibility Regularization during training to alleviate sparse-view overfitting.

**中文：**  
尽管深度监督、高斯稠密化与训练期正则已改善稀疏视角重建，有限视角观测仍可能导致初始几何不完整以及优化阶段过拟合。为应对这些挑战，SynGS 将显式视觉外壳约束与基于 VGGT 的多视角深度先验相结合，在优化前增强初始高斯几何，并在训练中引入 Dynamic Visibility Regularization 以缓解稀疏视角过拟合。

**说明：** 第 1 段未改；引用键未增删；模块名与 Intro/Method 统一为 Dynamic Visibility Regularization。

---

## 5. Experiments §4.2 — 定量讨论（重点）

**位置：** “Mip-NeRF 360 and LLFF” 段  
**目的：** 保留原叙述骨架；承认 LPIPS / 9-view trade-off；收束语气谨慎；删除两句 meta 辩护句。

**原文是：**  
Table 1 reports the results on Mip-NeRF 360 under the 4-, 6-, and 9-view settings. SynGS achieves the highest PSNR and SSIM in all three settings, with the largest PSNR advantage in the 4-view case: 25.91 dB, 3.56 dB above D²GS. For LPIPS, D²GS obtains lower values across the three settings. Table 2 shows a similar trend. With four views, SynGS achieves the best PSNR, SSIM, and LPIPS; under six views it obtains the highest PSNR and SSIM with LPIPS close to the best result. At nine views, D²GS gives slightly higher PSNR and lower LPIPS, while CoR-GS achieves slightly higher SSIM. The clearest advantage appears in the 4- and 6-view settings.

**中文：**  
表 1 报告了 Mip-NeRF 360 在 4/6/9 视角设置下的结果。SynGS 在三个设置下均取得最高的 PSNR 与 SSIM，其中 4 视角时 PSNR 优势最大：25.91 dB，比 D²GS 高 3.56 dB。就 LPIPS 而言，D²GS 在三个设置下均为更低（更好）。表 2 呈现类似趋势：4 视角时 SynGS 在 PSNR、SSIM、LPIPS 上均最优；6 视角时 PSNR 与 SSIM 最高，LPIPS 接近最优；9 视角时 D²GS 的 PSNR 略高、LPIPS 更低，CoR-GS 的 SSIM 略高。最明显的优势出现在 4 与 6 视角设置。

**修改后：**  
Table 1 reports the results on Mip-NeRF 360 under the 4-, 6-, and 9-view settings. SynGS achieves the highest PSNR and SSIM in all three settings, with the largest PSNR gain in the 4-view case: 25.91 dB, 3.56 dB above D²GS. However, D²GS obtains lower LPIPS values across the three settings, indicating an advantage in perceptual similarity. Table 2 shows a similar trend. With four views, SynGS leads in PSNR, SSIM, and LPIPS; under six views it obtains the highest PSNR and SSIM with LPIPS close to the best result. As the number of input views increases to nine, the differences among the leading methods become smaller: D²GS gives slightly higher PSNR and lower LPIPS, while CoR-GS achieves slightly higher SSIM. Overall, SynGS shows more pronounced improvements in the four- and six-view settings, suggesting that the proposed framework is particularly beneficial when the geometric information available from the input views is severely limited.

**中文：**  
表 1 报告 Mip-NeRF 360 在 4/6/9 视角下的结果。SynGS 在三个设置下均取得最高 PSNR 与 SSIM，其中 4 视角时 PSNR 增益最大：25.91 dB，比 D²GS 高 3.56 dB。然而，D²GS 在三个设置下 LPIPS 更低，在感知相似性上占优。表 2 趋势类似。4 视角时 SynGS 在 PSNR、SSIM、LPIPS 上领先；6 视角时取得最高 PSNR 与 SSIM，LPIPS 接近最优。当输入增至 9 视角时，领先方法之间差距变小：D²GS 的 PSNR 略高、LPIPS 更低，CoR-GS 的 SSIM 略高。总体而言，SynGS 在 4 与 6 视角设置下提升更为明显，表明当输入视角提供的几何信息严重受限时，所提框架尤为有益。

**相对原文的取舍：**  
- 删除：sparsity-dependent / claims stated … 两句 meta  
- 保留：Table 1/2 报告骨架、PSNR/SSIM 数字、LPIPS 与 9-view 分项事实  
- 调整：advantage→gain；LLFF 4-view best→leads；However+感知相似性；9-view “差距变小”；收束改为 more pronounced improvements …

---

## 6. Conclusion（结论）

**位置：** Conclusion 中原 “improves novel-view quality…” 一句  
**目的：** 与 §4.2 一致：sparsity-aware、主看 PSNR/SSIM、感知指标与更多视角更混合。

**结构：** 保留首句方法总结（不标黄）；其后整段为黄底修改。

**原文是：**  
On Mip-NeRF 360 and LLFF, SynGS improves novel-view quality under sparse inputs; densification adds memory and compute cost, and more efficient densification without losing quality is left for future work.

**中文：**  
在 Mip-NeRF 360 与 LLFF 上，SynGS 提升了稀疏输入下的新视角合成质量；稠密化会增加显存与计算开销，如何在不损失质量的前提下更高效地稠密化留待未来工作。

**修改后：**  
SynGS demonstrates more pronounced improvements under highly sparse-view conditions, particularly in PSNR and SSIM with four or six input views. With nine input views, SynGS maintains improvements in PSNR and SSIM on Mip-NeRF 360, while achieving performance comparable to leading methods on LLFF. However, the additional geometry introduced during initialization incurs memory and computational overhead. Future work will focus on developing more efficient geometry augmentation strategies to reduce these costs while preserving reconstruction quality.

**中文：**  
SynGS 在高度稀疏视角条件下提升更为明显，尤其在 4 或 6 输入视角下的 PSNR 与 SSIM。在 9 输入视角时，SynGS 在 Mip-NeRF 360 上仍保持 PSNR 与 SSIM 的提升，而在 LLFF 上与领先方法性能相当。然而，初始化阶段引入的额外几何会带来显存与计算开销。未来工作将聚焦更高效的几何增强策略，以在保持重建质量的同时降低这些成本。

---

## 修改清单速查 / Checklist

| # | 章节 | 类型 | 回应哪条意见 |
|---|------|------|--------------|
| 1 | Abstract | 改写末句 | 性能表述谨慎 |
| 2 | Introduction | **新增**定位段 | 新颖性/区别 |
| 3 | Introduction | 改写 3 条贡献 | 新颖性/区别 |
| 4 | Related Work | **新增** 1 句 | 新颖性/区别 |
| 5 | §4.2 Results | 改写+新增开场/收束 | 性能表述谨慎 |
| 6 | Conclusion | 改写 1 句 | 性能表述谨慎 |

---

## 给编辑的一句话（可选粘贴）

**中文：**  
本次修改针对审稿意见做了文案澄清：在引言中明确相对 depth supervision、online densification 与 co-regularization/dropout 的方法边界与贡献差异；在摘要、实验讨论与结论中将性能主张改为按视角数量与指标限定的表述，并明确报告 trade-off，未改实验与数据。

**English:**  
We clarified novelty by positioning SynGS against depth supervision, online densification, and co-regularization/dropout, and by rewriting the contribution statements comparatively. We also moderated performance claims in the abstract, experimental discussion, and conclusion to be sparsity- and metric-specific, explicitly acknowledging trade-offs, without changing methods or numerical results.

---

*供作者审查。若某句中译或英文仍偏满/偏弱，可直接在本文件标注后回改正文。*
