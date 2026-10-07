% SynGS: synergizing explicit geometry and transformer depth priors for sparse-view 3D Gaussian Splatting
% Junjie Geng*a, Ao Zhanga, and Lian Duana
% aCommunication University of China, State Key Laboratory of Media Convergence and Communication, Intelligent Network and Media Research Center, No. 1 Dingfuzhuang East Street, Chaoyang District, Beijing 100024, China
% *gjj@cuc.edu.cn

# ABSTRACT

In 360-degree scenes captured with sparse views, 3D Gaussian Splatting (3DGS) reconstruction is susceptible to the loss of edge detail, geometric instability in occluded regions, and overfitting to foreground regions. To mitigate these challenges under sparse-view conditions, we present SynGS, a 3D Gaussian Splatting method guided by geometric and depth priors for sparse-view 3D reconstruction. The proposed method leverages the visual hull to impose explicit geometric constraints and integrates a Transformer-based depth prior to facilitate global cross-view consistency, complemented by a geometry enhancement pipeline. By combining reliable depth filtering with fine-grained structural detail recovery and incorporating a dynamic visibility regularization strategy, our approach enables adaptive reweighting of supervision signals during optimization. Empirical evaluations demonstrate that SynGS achieves competitive performance, particularly in PSNR and SSIM. On the Mip-NeRF 360 dataset, SynGS achieves gains of up to 3.56 dB in PSNR and 0.025 in SSIM under sparse-view settings.

**Keywords:** Novel View Synthesis, 3D Gaussian Splatting, Few-shot reconstruction, Geometry Prior-Guided Reconstruction, Vision Transformer

# 1. INTRODUCTION

Sparse inputs provide limited information about visible regions, causing 3D reconstruction methods to overfit local observations and struggle to maintain global geometric consistency <sup>[1]</sup>. Sparse observations also introduce greater geometric ambiguity, making occluded regions, textureless areas, and view boundaries prone to missing geometry, structural distortions, and degraded appearance <sup>[2]</sup>. Kerbl et al. <sup>[3]</sup> introduced 3D Gaussian Splatting (3DGS); with tiled rasterization it enables rapid training and real-time rendering <sup>[3]</sup>, and subsequent variants improve structured, alias-free rendering <sup>[4,5]</sup>. Under sparse views, Structure-from-Motion (SfM) <sup>[6]</sup> often recovers incomplete point clouds. Since 3DGS relies on SfM cameras and sparse points for initialization, weak coverage harms geometric convergence <sup>[7]</sup>. Limited cross-view constraints further cause floaters and pseudo-geometry <sup>[8]</sup>, while sparse supervision <sup>[9]</sup> and visibility imbalance aggravate overfitting <sup>[10]</sup>.

Existing sparse-view methods explore depth regularization <sup>[11]</sup> and densification <sup>[12]</sup>, or co-regularization and Gaussian dropout <sup>[13,9]</sup>, but still struggle with fine structures and geometric consistency. We present SynGS, which strengthens Gaussian initialization with explicit geometric constraints and depth-guided densification, and applies Dynamic Visibility Regularization to reduce overfitting. The main contributions are:

- **Visual Hull Initialization.** We construct a visual hull from multi-view silhouettes as a stable geometric prior for Gaussian initialization.

- **VGGT-Guided Densification.** We back-project cross-view consistent depth predictions to supplement missing geometry for Gaussian initialization.

- **Dynamic Visibility Regularization.** We randomly mask Gaussian primitives during training to rebalance gradients and alleviate sparse-view overfitting.

# 2. RELATED WORK

Neural Radiance Fields (NeRF) represent scenes as implicit radiance fields and achieve high-quality novel view synthesis through differentiable rendering <sup>[14]</sup>. Under sparse views, however, insufficient observations cause severe geometric ambiguity. Depth-guided approaches further improve structural consistency <sup>[15,16]</sup>, while other methods constrain unobserved regions <sup>[2]</sup>, jointly refine noisy poses <sup>[17]</sup>, or leverage diffusion priors <sup>[18]</sup>. Grid-based anti-aliased variants such as Zip-NeRF further improve efficiency and rendering fidelity <sup>[19]</sup>, and baked neural surfaces enable real-time mesh-based view synthesis <sup>[20]</sup>. 3D Gaussian Splatting (3DGS) introduces an explicit scene representation based on optimizable Gaussian primitives and enables efficient training and real-time rendering through differentiable rasterization <sup>[3]</sup>. Beyond the original formulation, structured and anti-aliased Gaussian representations improve robustness and multi-scale rendering <sup>[4,5]</sup>, while surface-aligned variants target more accurate geometry recovery <sup>[21,22]</sup>. Depth-based approaches add geometric supervision <sup>[11]</sup>, densification-based methods improve Gaussian coverage <sup>[12,23]</sup>, including progressive geometric propagation <sup>[24]</sup>, gradient-aware density control <sup>[25]</sup>, and epipolar depth priors <sup>[26]</sup>. Others explore alternating densification under sparse inputs <sup>[27]</sup>, score distillation <sup>[28]</sup>, co-regularization <sup>[13]</sup>, and Gaussian dropout <sup>[9,29]</sup>. Pose-free and feed-forward sparse Gaussian reconstruction has also been studied <sup>[30,31,32,33]</sup>.

Classical multi-view stereo remains a strong geometric backbone <sup>[34]</sup>. Monocular depth estimators provide useful cues for underconstrained views <sup>[35]</sup>, and recent monocular geometry models further recover metric structure from a single image <sup>[36]</sup>. SynGS instead adapts a VGGT-based multi-view depth prior <sup>[37]</sup> together with explicit visual-hull initialization and dynamic visibility regularization for more stable sparse-view 3DGS reconstruction.

# 3. METHOD

## Overall Framework

We propose SynGS, a sparse-view 3D Gaussian Splatting <sup>[3]</sup> framework that integrates explicit geometry initialization, depth-guided densification, and visibility-aware optimization. As illustrated in Figure 1, the input consists of sparse-view images and corresponding foreground masks. While recent variants organize Gaussians with structured scaffolds or octrees <sup>[4,38]</sup>, SynGS focuses on silhouette-based initialization and depth-guided densification under sparse posed inputs.

First, **Visual Hull Initialization** constructs a coarse geometric prior from multi-view silhouettes and generates an initial point cloud. Then, **VGGT-Guided Densification** exploits cross-view depth priors to supplement missing geometry and produce a depth-enhanced point cloud for Gaussian initialization. Finally, **Dynamic Visibility Regularization (DVR)** is applied during 3DGS optimization to rebalance supervision under sparse visibility and reduce overfitting. The complete process proceeds from the Visual Hull point cloud, through depth densification and Gaussian initialization, to DVR-regularized optimization.

![Figure 1. Overview of the SynGS pipeline. The third stage applies Dynamic Visibility Regularization (DVR).](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/framework.png)

## Visual Hull Initialization

Under sparse views, Structure-from-Motion (SfM) <sup>[6]</sup> often produces sparse and incomplete point clouds. Weak coverage then destabilizes 3DGS optimization. We construct a Visual Hull prior from sparse multi-view images, camera parameters, and foreground masks, with light mask cleanup at boundaries. With known cameras, silhouettes are back-projected into 3D, and multi-view silhouette consistency defines a coarse geometric envelope of the target <sup>[39]</sup>.

Candidate points are retained only when their projections agree with all valid foreground masks, then cleaned by one-time statistical and radius-based outlier filtering. The scaffold is stable but coarse: silhouette-based reconstruction cannot fully recover concave regions and fine structures. Sec. 3.3 supplements the missing geometry before Gaussian initialization.

## VGGT-Guided Densification

Silhouettes alone miss concave regions and fine structures. We densify the Visual Hull point cloud with **VGGT-Depth**: from a pre-trained VGGT backbone <sup>[37]</sup>, a depth prior adaptation branch with cross-attention over multi-view tokens and a lightweight fusion head predicts per-view depth and confidence. Unlike a frozen monocular depth network <sup>[35]</sup>, the adaptation branch is conditioned on multi-view tokens (Figure 2).

![Figure 2. VGGT-Depth prior used for depth-guided point cloud densification.](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/vggt_depth.png)

We use the Visual Hull AABB diagonal $L$ as the scene-scale reference. For each view, masked depth MAE against dataset ground-truth depth is used only to filter views and rays during densification (not at inference or when computing metrics); it is normalized by the 95th percentile over validation views to obtain $q_v$. Views with $q_v<0.4$ are discarded. If fewer than $0.8N$ views remain, densification is skipped and the Visual Hull point cloud is retained. Remaining views keep regions that pass VGGT-Depth confidence and depth consistency. With tolerance

$$
\Delta(d)=\alpha d+\beta,\qquad
\alpha=0.01,\quad \beta=0.002L,
$$

we reject low-confidence or inconsistent observations before back-projection.

Point supplementation runs only along reliable rays. For each point, the top $K=3$ reliable views are selected; candidates are sampled around the predicted depth and back-projected. Related densification strategies propagate geometric cues or control Gaussian density during optimization <sup>[24,25]</sup>; alternating densification schedules have also been studied for sparse inputs <sup>[27]</sup>. Here supplementation is applied offline to the Visual Hull point cloud before training. Complementary work injects epipolar depth priors into sparse-view Gaussian reconstruction <sup>[26]</sup>, or rasterizes depth from Gaussians for geometric supervision <sup>[40]</sup>; we instead use adapted VGGT-Depth predictions for back-projection. Supplementary points are merged via two-stage voxel fusion and deduplication ($0.01L$ then $0.004L$).

Each densified point initializes a Gaussian center; scale comes from the mean distance to its $k=8$ nearest neighbors. Multi-view colors are fused with depth-consistency and VGGT confidence weights. Opacity is set from cross-view consistency and clipped to $[0.2,0.8]$. Uneven supervision remains under sparse views; we address this with DVR (Sec. 3.4).

## Dynamic Visibility Regularization

Sparse-view optimization remains strongly visibility-dependent. Distant, occluded, or poorly observed Gaussians appear in fewer views or pixels and receive weaker reconstruction gradients <sup>[8,9]</sup>. Visibility priors have also been explored to regularize sparse-input radiance fields <sup>[10]</sup>, and distractor-aware training further highlights sensitivity to unreliable observations <sup>[41]</sup>. Beyond fixed densification heuristics, densification can also be cast as stochastic sampling <sup>[42]</sup>, while constraining the Gaussian budget motivates careful control of which primitives participate in rendering <sup>[43]</sup>. We use DVR via progressive Gaussian dropout.

At iteration $t$, DVR randomly masks a subset of Gaussians for dropout rendering. The dropout ratio grows linearly:

$$
r_t=\min\left(r_{\max},\,\gamma\frac{t}{T}\right),
$$

where $t$ and $T$ are the current and total iterations, $r_{\max}$ is the maximum dropout ratio, and $\gamma=0.1$--$0.2$ controls the growth rate. Early training keeps weak dropout for geometric convergence; later training increases it against sparse-view overfitting.

Used alone, random dropout can induce opacity or scale compensation; we keep a full-render branch as an anchor. Unlike compensated rendering that rescales retained primitives <sup>[9]</sup>, the dropout branch is left uncompensated, while the full set is rendered in parallel under the same target. Let $I_{\mathrm{full}}$ and $I_{\mathrm{drop}}$ denote the full and dropout renderings, and $I$ the ground-truth image. We use the standard color loss

$$
\mathcal{L}_{\mathrm{color}}(\hat{I},I)
=
(1-\lambda)\,\mathcal{L}_{1}(\hat{I},I)
+
\lambda\,\mathcal{L}_{\mathrm{D\text{-}SSIM}}(\hat{I},I),
$$

with $\lambda=0.2$ <sup>[3]</sup>. The final objective is

$$
\mathcal{L}
=
\mathcal{L}_{\mathrm{color}}(I_{\mathrm{full}},I)
+
\beta\,\mathcal{L}_{\mathrm{color}}(I_{\mathrm{drop}},I),
$$

where $\beta=0.5$--$1.0$. Related sparse-view designs further modulate masking with depth and density cues <sup>[44]</sup>, or drop anchors and spherical harmonics <sup>[29]</sup>; DVR instead uses a progressive random schedule with an uncompensated dropout branch.

# 4. EXPERIMENTS

## Experimental Setup and Datasets

We evaluate SynGS on Mip-NeRF 360 (unbounded 360° scenes) <sup>[45]</sup> and LLFF (forward-facing real captures) <sup>[46]</sup>. All images are downsampled by a factor of 8. Mip-NeRF 360 scenes are tested with 4, 6, and 9 uniformly sampled input views. Metrics are PSNR, SSIM, and LPIPS. We compare against the baselines in Table 1 and Table 2. Table 1 includes RegNeRF <sup>[2]</sup>, SparseNeRF <sup>[15]</sup>, 3DGS <sup>[3]</sup>, CoR-GS <sup>[13]</sup>, DropGaussian <sup>[9]</sup>, and D²GS <sup>[44]</sup>. Table 2 uses the same 3DGS-based baselines, with FreeNeRF <sup>[1]</sup> in place of SparseNeRF among the NeRF-based methods.

Training follows the standard 3DGS framework. Depth priors come from VGGT-Depth. Consistent with Sec. 3.3, view- and ray-level selection during densification may use dataset ground-truth depth only as a filter; novel-view rendering and all reported metrics do not use ground-truth depth. The model is trained for 30K iterations, with 3DGS initialization optimized for 10K iterations. Floaters are periodically removed during training. Experiments use PyTorch on an NVIDIA RTX 4090 GPU.

## Quantitative and Qualitative Results

Table 1. Performance comparisons of sparse-view synthesis on Mip-NeRF 360 (4/6/9 views). LPIPS* denotes LPIPS × 10².

| Group | Methods | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| | | 4-view | 4-view | 4-view | 6-view | 6-view | 6-view | 9-view | 9-view | 9-view |
| NeRF-based | RegNeRF | 19.88 | 12.59 | 0.841 | 20.72 | 13.41 | 0.847 | 19.7 | 13.68 | 0.852 |
|  | SparseNeRF | 17.76 | 12.83 | 0.845 | 19.74 | 13.42 | 0.861 | 21.56 | 14.36 | 0.873 |
| 3DGS-based | 3DGS | 10.8 | 20.31 | 0.899 | 8.38 | 22.12 | 0.913 | 6.42 | 24.29 | 0.93 |
|  | CoR-GS | 11.76 | 20.45 | 0.856 | 9.28 | 22.57 | 0.901 | 7.04 | 24.73 | 0.926 |
|  | DropGaussian | 11.57 | 21.76 | 0.837 | 8.61 | 22.98 | 0.895 | 8.02 | 24.1 | 0.915 |
|  | D²GS | 2.58 | 22.35 | 0.923 | 2.34 | 24.74 | 0.937 | 2.11 | 27.13 | 0.941 |
|  | SynGS (Ours) | 3.89 | 25.91 | 0.948 | 3.43 | 27.93 | 0.953 | 3.02 | 29.21 | 0.961 |

Table 2. Performance comparisons of sparse-view synthesis on LLFF (4/6/9 views). LPIPS* denotes LPIPS × 10².

| Group | Methods | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| | | 4-view | 4-view | 4-view | 6-view | 6-view | 6-view | 9-view | 9-view | 9-view |
| NeRF-based | RegNeRF | 29.65 | 18.55 | 0.587 | 22.61 | 19.08 | 0.76 | 18.39 | 22.86 | 0.82 |
|  | FreeNeRF | 30.85 | 19.09 | 0.624 | 23.06 | 19.81 | 0.763 | 17.94 | 23.08 | 0.823 |
| 3DGS-based | 3DGS | 22.93 | 19.32 | 0.649 | 13.45 | 23.8 | 0.814 | 9.68 | 25.44 | 0.86 |
|  | CoR-GS | 19.66 | 20.45 | 0.696 | 12.53 | 23.87 | 0.84 | 8.94 | 26.7 | 0.874 |
|  | DropGaussian | 21.93 | 19.8 | 0.621 | 13.79 | 23.41 | 0.803 | 9.4 | 25.87 | 0.868 |
|  | D²GS | 17.98 | 22.35 | 0.746 | 13.85 | 23.91 | 0.846 | 8.91 | 26.8 | 0.871 |
|  | SynGS (Ours) | 16.92 | 23.92 | 0.762 | 12.54 | 25.17 | 0.848 | 8.96 | 26.71 | 0.871 |

## Quantitative and Qualitative Results

**Mip-NeRF 360 and LLFF.** Table 1 reports the results on Mip-NeRF 360 under the 4-, 6-, and 9-view settings. SynGS achieves the highest PSNR and SSIM in all three settings, with the largest PSNR advantage in the 4-view case: 25.91 dB, 3.56 dB above D²GS <sup>[44]</sup>. For LPIPS, D²GS obtains lower values across the three settings. Table 2 shows a similar trend. With four views, SynGS achieves the best PSNR, SSIM, and LPIPS; under six views it obtains the highest PSNR and SSIM with LPIPS close to the best result. At nine views, D²GS <sup>[44]</sup> gives slightly higher PSNR and lower LPIPS, while CoR-GS <sup>[13]</sup> achieves slightly higher SSIM. The clearest advantage appears in the 4- and 6-view settings.

**Qualitative Results.** Figure 3 shows the 4-view comparison on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete object boundaries, and preserves finer structures where baselines show broken contours or missing details.

![Figure 3. Qualitative comparison under the 4-view sparse-input setting on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete structural boundaries than the compared methods.](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/qualitative.png)

## Ablation Study

## Ablation Study

Table 3 isolates the contributions of the three components. Unlike Table 1, which reports dataset-wide averages, the ablation is a separate protocol and is not the 4-view mean in Table 1.

Visual Hull Initialization establishes the geometric baseline at 17.51 dB PSNR. Adding Depth Densification raises PSNR to 24.96 dB, the largest gain in the ablation. Adding DVR further improves the full configuration to 26.18 dB, with gains in SSIM and LPIPS.

Table 3. Ablation study of SynGS components. LPIPS* denotes LPIPS × 10².

| Visual Hull Init | Depth Densification | Visibility Balancing* | SSIM↑ | PSNR↑ | LPIPS*↓ |
|:---:|:---:|:---:|---:|---:|---:|
| √ |  |  | 0.865 | 17.51 | 12.80 |
| √ | √ |  | 0.902 | 24.96 | 5.20 |
| √ | √ | √ | **0.943** | **26.18** | **3.98** |

*Visibility Balancing denotes Dynamic Visibility Regularization (DVR).

# 5. CONCLUSION

We present SynGS for sparse-view 3DGS, combining **Visual Hull Initialization**, **VGGT-Guided Densification**, and **Dynamic Visibility Regularization** for more reliable initialization, geometry completion, and reduced sparse-view overfitting. On Mip-NeRF 360 and LLFF, SynGS improves novel-view quality under sparse inputs; densification adds memory and compute cost, and more efficient densification without losing quality is left for future work.

# REFERENCES

[1] Yang, J., Pavone, M., and Wang, Y., ``FreeNeRF: Improving few-shot neural rendering with free frequency regularization,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 8254--8263 (2023). DOI: https://doi.org/10.1109/cvpr52729.2023.00798.

[2] Niemeyer, M., Barron, J.~T., Mildenhall, B., Sajjadi, M. S.~M., Geiger, A., and Radwan, N., ``RegNeRF: Regularizing neural radiance fields for view synthesis from sparse inputs,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5480--5490 (2022). DOI: https://doi.org/10.1109/cvpr52688.2022.00540.

[3] Kerbl, B., Kopanas, G., Leimk\"uhler, T., and Drettakis, G., ``3D gaussian splatting for real-time radiance field rendering,'' ACM Transactions on Graphics~ 42(4), 139:1--139:14 (2023). DOI: https://doi.org/10.1145/3592433.

[4] Lu, T., Yu, M., Xu, L., Xiangli, Y., Wang, L., Lin, D., and Dai, B., ``Scaffold-GS: Structured 3D gaussians for view-adaptive rendering,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 20654--20664 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01952.

[5] Yu, Z., Chen, A., Huang, B., Sattler, T., and Geiger, A., ``Mip-splatting: Alias-free 3D Gaussian splatting,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 19447--19456 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01839.

[6] Sch\"onberger, J.~L. and Frahm, J.-M., ``Structure-from-motion revisited,'' in [Proc.\ IEEE Conference on Computer Vision and Pattern Recognition (CVPR)], 4104--4113 (2016). DOI: https://doi.org/10.1109/cvpr.2016.445.

[7] Chung, J., Oh, J., and Lee, K.~M., ``Depth-regularized optimization for 3D gaussian splatting in few-shot images,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)], 811--820 (2024). DOI: https://doi.org/10.1109/cvprw63382.2024.00086.

[8] Xu, Y., Wang, L., Chen, M., Ao, S., Li, L., and Guo, Y., ``DropoutGS: Dropping out gaussians for better sparse-view rendering,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 701--710 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.00074.

[9] Park, H., Ryu, G., and Kim, W., ``DropGaussian: Structural regularization for sparse-view gaussian splatting,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 21600--21609 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.02012.

[10] Somraj, N. and Soundararajan, R., ``ViP-NeRF: Visibility prior for sparse input neural radiance fields,'' in [Proc.\ ACM SIGGRAPH Conference], 1--11 (2023). DOI: https://doi.org/10.1145/3588432.3591539.

[11] Li, J., Zhang, J., Bai, X., Zheng, J., Ning, X., Zhou, J., and Gu, L., ``DNGaussian: Optimizing sparse-view 3D gaussian radiance fields with global-local depth normalization,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 20775--20785 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01963.

[12] Zhu, Z., Fan, Z., Jiang, Y., and Wang, Z., ``FSGS: Real-time few-shot view synthesis using gaussian splatting,'' in [Proc.\ European Conference on Computer Vision (ECCV)], 145--163 (2024). DOI: https://doi.org/10.1007/978-3-031-72933-1\_9.

[13] Zhang, J., Li, J., Yu, X., Huang, L., Gu, L., Zheng, J., and Bai, X., ``CoR-GS: Sparse-view 3D gaussian splatting via co-regularization,'' in [Proc.\ European Conference on Computer Vision (ECCV)], 335--352 (2024). DOI: https://doi.org/10.1007/978-3-031-73232-4\_19.

[14] Mildenhall, B., Srinivasan, P.~P., Tancik, M., Barron, J.~T., Ramamoorthi, R., and Ng, R., ``NeRF: Representing scenes as neural radiance fields for view synthesis,'' Communications of the ACM~ 65(1), 99--106 (2021). DOI: https://doi.org/10.1145/3503250.

[15] Wang, G., Chen, Z., Loy, C.~C., and Liu, Z., ``SparseNeRF: Distilling depth ranking for few-shot novel view synthesis,'' in [Proc.\ IEEE/CVF International Conference on Computer Vision (ICCV)], 9031--9042 (2023). DOI: https://doi.org/10.1109/iccv51070.2023.00832.

[16] Deng, K., Liu, A., Zhu, J.-Y., and Ramanan, D., ``Depth-supervised NeRF: Fewer views and faster training for free,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 12872--12881 (2022). DOI: https://doi.org/10.1109/cvpr52688.2022.01254.

[17] Truong, P., Rakotosaona, M.-J., Manhardt, F., and Tombari, F., ``SPARF: Neural radiance fields from sparse and noisy poses,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 4190--4200 (2023). DOI: https://doi.org/10.1109/cvpr52729.2023.00408.

[18] Wu, R., Mildenhall, B., Henzler, P., Park, K., Gao, R., Watson, D., Srinivasan, P.~P., Verbin, D., Barron, J.~T., Poole, B., and Hoy\'nski, A., ``ReconFusion: 3D reconstruction with diffusion priors,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 21551--21561 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.02036.

[19] Barron, J.~T., Mildenhall, B., Verbin, D., Srinivasan, P.~P., and Hedman, P., ``Zip-NeRF: Anti-aliased grid-based neural radiance fields,'' in [Proc.\ IEEE/CVF International Conference on Computer Vision (ICCV)], 19697--19705 (2023). DOI: https://doi.org/10.1109/iccv51070.2023.01804.

[20] Yariv, L., Hedman, P., Reiser, C., Verbin, D., Srinivasan, P.~P., Szeliski, R., Barron, J.~T., and Mildenhall, B., ``BakedSDF: Meshing neural SDFs for real-time view synthesis.'' arXiv preprint arXiv:2302.14859 (2023). DOI: https://doi.org/10.1145/3588432.3591536.

[21] Gu\'edon, A. and Lepetit, V., ``SuGaR: Surface-aligned Gaussian splatting for efficient 3D mesh reconstruction and high-quality mesh rendering,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5354--5363 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.00512.

[22] Huang, B., Yu, Z., Chen, A., Geiger, A., and Gao, S., ``2D Gaussian splatting for geometrically accurate radiance fields.'' arXiv preprint arXiv:2403.17888 (2024). DOI: https://doi.org/10.1145/3641519.3657428.

[23] Bao, Z., Liao, G., Zhou, K., Liu, K., Li, Q., and Qiu, G., ``LoopSparseGS: Loop-based sparse-view friendly Gaussian splatting,'' IEEE Transactions on Image Processing~ 34, 3889--3902 (2025). DOI: https://doi.org/10.1109/TIP.2025.3574929.

[24] Cheng, K., Long, X., Yang, K., Yao, Y., Yin, W., Ma, Y., Wang, W., and Chen, X., ``GaussianPro: 3D Gaussian splatting with progressive propagation.'' arXiv preprint arXiv:2402.14650 (2024). DOI: https://doi.org/10.48550/arXiv.2402.14650.

[25] Zhou, Z., Xiong, Y.-J., Zhang, J.-C., Xia, C.-M., Qiu, X., and Zhan, H., ``Gradient-direction-aware density control for 3D Gaussian splatting.'' arXiv preprint arXiv:2508.09239 (2025). DOI: https://doi.org/10.48550/arXiv.2508.09239.

[26] Zheng, Y., Jiang, Z., He, S., Sun, Y., Dong, J., Zhang, H., and Du, Y., ``NexusGS: Sparse view synthesis with epipolar depth priors in 3D Gaussian splatting,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 26800--26809 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.02496.

[27] Patle, G., Girgaonkar, N., Somraj, N., and Soundararajan, R., ``AD-GS: Alternating densification for sparse-input 3D Gaussian splatting.'' arXiv preprint arXiv:2509.11003 (2025). DOI: https://doi.org/10.1145/3757377.3763993.

[28] Xiong, H., Muttukuru, S., Upadhyay, R., Chari, P., and Kadambi, A., ``SparseGS: Real-time 360° sparse view synthesis using Gaussian splatting,'' in [Proc.\ International Conference on 3D Vision (3DV)], (2025). DOI: https://doi.org/10.1109/3dv66043.2025.00100.

[29] Fang, S., Shen, I.-C., Zhang, X., Wang, Z., Wang, Y., Ding, W., Yu, G., and Igarashi, T., ``Dropping anchor and spherical harmonics for sparse-view Gaussian splatting.'' arXiv preprint arXiv:2602.20933 (2026). DOI: https://doi.org/10.48550/arXiv.2602.20933.

[30] Wang, S., Leroy, V., Cabon, Y., Chidlovskii, B., and Revaud, J., ``DUSt3R: Geometric 3D vision made easy,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 20697--20709 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01956.

[31] Fan, Z., Cong, W., Wen, K., Wang, K., Zhang, J., Ding, X., Xu, D., Ivanovic, B., Pavone, M., Pavlakos, G., Wang, Z., and Wang, Y., ``InstantSplat: Sparse-view Gaussian splatting in seconds.'' arXiv preprint arXiv:2403.20309 (2024). DOI: https://doi.org/10.48550/arXiv.2403.20309.

[32] Charatan, D., Li, S.~L., Tagliasacchi, A., and Sitzmann, V., ``pixelSplat: 3D Gaussian splats from image pairs for scalable generalizable 3D reconstruction,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 19457--19467 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01840.

[33] Chen, Y., Xu, H., Zheng, C., Zhuang, B., Pollefeys, M., Geiger, A., Cham, T.-J., and Cai, J., ``MVSplat: Efficient 3D Gaussian splatting from sparse multi-view images,'' in [Proc.\ European Conference on Computer Vision (ECCV)], 370--381 (2024). DOI: https://doi.org/10.1007/978-3-031-72664-4\_21.

[34] Cao, C., Ren, X., and Fu, Y., ``MVSFormer++: Revealing the devil in transformer's details for multi-view stereo.'' arXiv preprint arXiv:2401.11673 (2024). DOI: https://doi.org/10.48550/arXiv.2401.11673.

[35] Yang, L., Kang, B., Huang, Z., Zhao, Z., Xu, X., Feng, J., and Zhao, H., ``Depth anything V2,'' in [Advances in Neural Information Processing Systems (NeurIPS)], 37, 21875--21911 (2024). DOI: https://doi.org/10.52202/079017-0688.

[36] Wang, R., Xu, S., Dai, C., Xiang, J., Deng, Y., Tong, X., and Yang, J., ``MoGe: Unlocking accurate monocular geometry estimation for open-domain images with optimal training supervision.'' arXiv preprint arXiv:2410.19115 (2024). DOI: https://doi.org/10.1109/cvpr52734.2025.00496.

[37] Wang, J., Chen, M., Karaev, N., Vedaldi, A., Rupprecht, C., and Novotny, D., ``VGGT: Visual geometry grounded transformer,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5294--5306 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.00499.

[38] Li, J., Wen, Z., Zhang, L., Hu, J., Hou, F., Zhang, Z., and He, Y., ``GS-Octree: Octree-based 3D Gaussian splatting for robust object-level 3D reconstruction under strong lighting.'' arXiv preprint arXiv:2406.18199 (2024). DOI: https://doi.org/10.1111/cgf.15206.

[39] Laurentini, A., ``The visual hull concept for silhouette-based image understanding,'' IEEE Transactions on Pattern Analysis and Machine Intelligence~ 16(2), 150--162 (1994). DOI: https://doi.org/10.1109/34.273735.

[40] Zhang, B., Fang, C., Shrestha, R., Liang, Y., Long, X., and Tan, P., ``RaDe-GS: Rasterizing depth in Gaussian splatting.'' arXiv preprint arXiv:2406.01467 (2024). DOI: https://doi.org/10.1145/3789201.

[41] Sabour, S., Goli, L., Kopanas, G., Matthews, M., Lagun, D., Guibas, L., Jacobson, A., Fleet, D.~J., and Tagliasacchi, A., ``SpotlessSplats: Ignoring distractors in 3D Gaussian splatting.'' arXiv preprint arXiv:2406.20055 (2024). DOI: https://doi.org/10.1145/3727143.

[42] Kheradmand, S., Rebain, D., Sharma, G., Sun, W., Tseng, J., Isack, H., Kar, A., Tagliasacchi, A., and Yi, K.~M., ``3D Gaussian splatting as markov chain monte carlo.'' arXiv preprint arXiv:2404.09591 (2024). DOI: https://doi.org/10.52202/079017-2573.

[43] Fang, G. and Wang, B., ``Mini-splatting: Representing scenes with a constrained number of gaussians.'' arXiv preprint arXiv:2403.14166 (2024). DOI: https://doi.org/10.1007/978-3-031-72980-5\_10.

[44] Song, M., Lin, X., Zhang, D., Li, H., Li, X., Du, B., and Qi, L., ``D2GS: Depth-and-density guided gaussian splatting for stable and accurate sparse-view reconstruction.'' arXiv preprint arXiv:2510.08566 (2025). DOI: https://doi.org/10.48550/arXiv.2510.08566.

[45] Barron, J.~T., Mildenhall, B., Verbin, D., Srinivasan, P.~P., and Hedman, P., ``Mip-NeRF 360: Unbounded anti-aliased neural radiance fields,'' in [Proc.\ IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5460--5469 (2022). DOI: https://doi.org/10.1109/cvpr52688.2022.00539.

[46] Mildenhall, B., Srinivasan, P.~P., Ortiz-Cayon, R., Kalantari, N.~K., Ramamoorthi, R., Ng, R., and Kar, A., ``Local light field fusion: Practical view synthesis with prescriptive sampling guidelines,'' ACM Transactions on Graphics~ 38(4), 29:1--29:14 (2019). DOI: https://doi.org/10.1145/3306346.3322980.
