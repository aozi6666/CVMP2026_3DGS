% SynGS manuscript for SPIE A4 Word export

# ABSTRACT

In 360-degree scenes captured with sparse views, 3D Gaussian Splatting (3DGS) reconstruction is susceptible to the loss of edge detail, geometric instability in occluded regions, and overfitting to foreground regions. ⟦REV⟧To address the reconstruction difficulties arising from limited input observations, we introduce SynGS, which incorporates explicit geometric constraints and depth information into the 3D Gaussian Splatting framework.⟦/REV⟧ The proposed method leverages the visual hull to impose explicit geometric constraints and integrates a Transformer-based depth prior to facilitate global cross-view consistency, complemented by a geometry enhancement pipeline. By combining reliable depth filtering with fine-grained structural detail recovery and incorporating a dynamic visibility regularization strategy, our approach enables adaptive reweighting of supervision signals during optimization. ⟦REV⟧The experimental findings indicate favorable PSNR and SSIM results for SynGS. In the Mip-NeRF 360 experiments, its PSNR and SSIM values exceed those reported for the selected baseline methods under the evaluated input-view configurations,⟦/REV⟧ reaching 25.91 dB in PSNR and 0.948 in SSIM using only four input views. On LLFF, the improvements are more apparent in the four- and six-view settings, while the nine-view results remain comparable to those of other evaluated methods.

**Keywords:** Novel View Synthesis, 3D Gaussian Splatting, Few-shot reconstruction, Geometry Prior-Guided Reconstruction, Vision Transformer

# INTRODUCTION

Sparse inputs provide limited information about visible regions, causing 3D reconstruction methods to overfit local observations and struggle to maintain global geometric consistency <sup>[1]</sup>. Sparse observations also introduce greater geometric ambiguity, making occluded regions, textureless areas, and view boundaries prone to missing geometry, structural distortions, and degraded appearance <sup>[2]</sup>. ⟦REV⟧Kerbl et al.⟦/REV⟧ <sup>[3]</sup> ⟦REV⟧proposed 3D Gaussian Splatting (3DGS), which achieves fast training and real-time rendering through a tile-based rasterization mechanism. Subsequent developments have further enhanced the representation through structured Gaussian organization⟦/REV⟧ <sup>[4]</sup>. Under sparse views, Structure-from-Motion (SfM) <sup>[5]</sup> often recovers incomplete point clouds. Since 3DGS relies on SfM cameras and sparse points for initialization, weak coverage harms geometric convergence <sup>[6]</sup>. Limited cross-view constraints further cause floaters and pseudo-geometry <sup>[7]</sup>, while sparse supervision <sup>[8]</sup> and visibility imbalance aggravate overfitting <sup>[9]</sup>.

Existing sparse-view methods have explored depth regularization <sup>[10]</sup>, Gaussian densification <sup>[11]</sup>, co-regularization <sup>[12]</sup>, and Gaussian dropout <sup>[8]</sup> to improve reconstruction. Nevertheless, incomplete initial geometry and overfitting during optimization remain challenges when only a few observations are available. ⟦REV⟧To mitigate these challenges, we develop SynGS within the sparse-view 3DGS setting, where geometry-guided Gaussian initialization is coupled with regularization during training.⟦/REV⟧ By strengthening initial geometric support and mitigating overfitting during optimization, SynGS improves reconstruction robustness under severely limited view coverage. The main contributions are:

- **Visual Hull Initialization.** We incorporate a visual hull derived from multi-view silhouettes to provide an explicit geometric constraint for Gaussian initialization. This constraint complements incomplete SfM observations and helps establish a more reliable initial spatial distribution of Gaussian primitives.

- **VGGT-Guided Densification.** We develop a pre-optimization densification strategy that back-projects cross-view-consistent depth estimates from VGGT to supplement the sparse initial point set. By introducing additional geometric samples before training, this strategy improves geometric coverage in under-observed regions.

- **Dynamic Visibility Regularization.** We incorporate Dynamic Visibility Regularization during training to stochastically mask Gaussian primitives, redistribute optimization gradients, and mitigate overfitting under limited-view supervision. ⟦REV⟧Together with the geometry-enhanced initialization, this regularization contributes to more robust reconstruction when only a limited number of input views are available.⟦/REV⟧

# RELATED WORK

⟦REV⟧In neural rendering, Neural Radiance Fields (NeRF) employ an implicit radiance field representation, allowing high-quality images of unseen viewpoints to be synthesized through differentiable rendering⟦/REV⟧ <sup>[13]</sup>. Under sparse views, however, insufficient observations cause severe geometric ambiguity. Depth-guided approaches further improve structural consistency <sup>[14]</sup>, while other methods constrain unobserved regions <sup>[2]</sup>. ⟦REV⟧In contrast to implicit radiance field representations, 3D Gaussian Splatting (3DGS) models scenes explicitly using optimizable Gaussian primitives, with differentiable rasterization supporting efficient training and real-time rendering⟦/REV⟧ <sup>[3]</sup>. Beyond the original formulation, structured Gaussian representations improve robustness and view-adaptive rendering <sup>[4]</sup>. Depth-based approaches introduce additional geometric supervision <sup>[10]</sup>, while densification-based methods improve Gaussian coverage <sup>[11]</sup>. Other strategies include epipolar depth priors <sup>[15]</sup>. Others explore co-regularization <sup>[12]</sup> and Gaussian dropout <sup>[8]</sup>.

⟦REV⟧Monocular depth estimators provide useful cues for underconstrained views⟦/REV⟧ <sup>[16]</sup>. Although depth supervision, Gaussian densification, and training-time regularization have improved sparse-view reconstruction, limited-view observations can still result in incomplete initial geometry and overfitting during optimization. To address these challenges, SynGS combines explicit visual-hull constraints with a VGGT-based multi-view depth prior <sup>[17]</sup> to augment the initial Gaussian geometry before optimization, and incorporates Dynamic Visibility Regularization during training to alleviate sparse-view overfitting.

# METHOD

## Overall Framework

⟦REV⟧SynGS is developed as a sparse-view 3D Gaussian Splatting⟦/REV⟧ <sup>[3]</sup> ⟦REV⟧framework that combines explicit geometric initialization, depth-guided point cloud densification, and visibility-aware optimization.⟦/REV⟧ Figure 1 ⟦REV⟧illustrates the overall pipeline, which takes sparsely captured images and their corresponding foreground masks as input.⟦/REV⟧ While recent variants organize Gaussians with structured scaffolds <sup>[4]</sup>, SynGS focuses on silhouette-based initialization and depth-guided densification under sparse posed inputs.

First, **Visual Hull Initialization** constructs a coarse geometric prior from multi-view silhouettes and generates an initial point cloud. Then, **VGGT-Guided Densification** exploits cross-view depth priors to supplement missing geometry and produce a depth-enhanced point cloud for Gaussian initialization. Finally, **Dynamic Visibility Regularization (DVR)** is applied during 3DGS optimization to rebalance supervision under sparse visibility and reduce overfitting. The complete process proceeds from the Visual Hull point cloud, through depth densification and Gaussian initialization, to DVR-regularized optimization.

![Figure 1. Overview of the SynGS pipeline. The third stage applies Dynamic Visibility Regularization (DVR).](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/framework.png)

## Visual Hull Initialization

Under sparse views, Structure-from-Motion (SfM) <sup>[5]</sup> often produces sparse and incomplete point clouds. Weak coverage then destabilizes 3DGS optimization. We construct a Visual Hull prior from sparse multi-view images, camera parameters, and foreground masks, with light mask cleanup at boundaries. With known cameras, silhouettes are back-projected into 3D, and multi-view silhouette consistency defines a coarse geometric envelope of the target <sup>[18]</sup>.

Candidate points are retained only when their projections agree with all valid foreground masks, then cleaned by one-time statistical and radius-based outlier filtering. The scaffold is stable but coarse: silhouette-based reconstruction cannot fully recover concave regions and fine structures. Sec. 3.3 supplements the missing geometry before Gaussian initialization.

## VGGT-Guided Densification

Silhouettes alone miss concave regions and fine structures. We densify the Visual Hull point cloud with **VGGT-Depth**: from a pre-trained VGGT backbone <sup>[17]</sup>, a depth prior adaptation branch with cross-attention over multi-view tokens and a lightweight fusion head predicts per-view depth and confidence. Unlike a frozen monocular depth network <sup>[16]</sup>, the adaptation branch is conditioned on multi-view tokens (Figure 2).

![Figure 2. VGGT-Depth prior used for depth-guided point cloud densification.](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/vggt_depth.png)

We use the Visual Hull AABB diagonal $L$ as the scene-scale reference. For each view, masked depth MAE against dataset ground-truth depth is used only to filter views and rays during densification (not at inference or when computing metrics); it is normalized by the 95th percentile over validation views to obtain $q_v$. Views with $q_v<0.4$ are discarded. If fewer than $0.8N$ views remain, densification is skipped and the Visual Hull point cloud is retained. Remaining views keep regions that pass VGGT-Depth confidence and depth consistency. With tolerance

$$
\Delta(d)=\alpha d+\beta,\qquad
\alpha=0.01,\quad \beta=0.002L,
$$

we reject low-confidence or inconsistent observations before back-projection.

Point supplementation runs only along reliable rays. For each point, the top $K=3$ reliable views are selected; candidates are sampled around the predicted depth and back-projected. Here supplementation is applied offline to the Visual Hull point cloud before training. Complementary work injects epipolar depth priors into sparse-view Gaussian reconstruction <sup>[15]</sup>; we instead use adapted VGGT-Depth predictions for back-projection. Supplementary points are merged via two-stage voxel fusion and deduplication ($0.01L$ then $0.004L$).

⟦REV⟧The densified points are used to initialize Gaussian centers, with the scale of each Gaussian determined by the average distance to its $k=8$ nearest neighbors. Color information from multiple views is combined using weights derived from depth consistency and VGGT confidence.⟦/REV⟧ Opacity is set from cross-view consistency and clipped to $[0.2,0.8]$. Uneven supervision remains under sparse views; we address this with DVR (Sec. 3.4).

## Dynamic Visibility Regularization

Sparse-view optimization remains strongly visibility-dependent. Distant, occluded, or poorly observed Gaussians appear in fewer views or pixels and receive weaker reconstruction gradients <sup>[7,8]</sup>. Visibility priors have also been explored to regularize sparse-input radiance fields <sup>[9]</sup>. We use DVR via progressive Gaussian dropout.

At iteration $t$, DVR randomly masks a subset of Gaussians for dropout rendering. The dropout ratio grows linearly:

$$
r_t=\min\left(r_{\max},\,\gamma\frac{t}{T}\right),
$$

where $t$ and $T$ are the current and total iterations, $r_{\max}$ is the maximum dropout ratio, and $\gamma=0.1$--$0.2$ controls the growth rate. Early training keeps weak dropout for geometric convergence; later training increases it against sparse-view overfitting.

Used alone, random dropout can induce opacity or scale compensation; we keep a full-render branch as an anchor. Unlike compensated rendering that rescales retained primitives <sup>[8]</sup>, the dropout branch is left uncompensated, while the full set is rendered in parallel under the same target. ⟦REV⟧We denote the images rendered using the complete Gaussian set and the dropout-masked Gaussian set by $I_{\mathrm{full}}$ and $I_{\mathrm{drop}}$, respectively, while $I$ represents the ground-truth image. The standard color loss is formulated as follows:⟦/REV⟧

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

where $\beta=0.5$--$1.0$. Related sparse-view designs further modulate masking with depth and density cues <sup>[19]</sup>; DVR instead uses a progressive random schedule with an uncompensated dropout branch.

# EXPERIMENTS

## Experimental Setup and Datasets

⟦REV⟧The evaluation of SynGS is conducted using two datasets: Mip-NeRF 360, which contains unbounded 360° scenes⟦/REV⟧ <sup>[20]</sup>⟦REV⟧, and LLFF, which consists of forward-facing real-world captures⟦/REV⟧ <sup>[21]</sup>⟦REV⟧. Images from both datasets are downsampled by a factor of 8.⟦/REV⟧ Mip-NeRF 360 scenes are tested with 4, 6, and 9 uniformly sampled input views. Metrics are PSNR, SSIM, and LPIPS. We compare SynGS with the NeRF- and 3DGS-based methods listed in Table 1 and Table 2.

Training follows the standard 3DGS framework. Depth priors come from VGGT-Depth. Consistent with Sec. 3.3, view- and ray-level selection during densification may use dataset ground-truth depth only as a filter; novel-view rendering and all reported metrics do not use ground-truth depth. The model is trained for 30K iterations, with 3DGS initialization optimized for 10K iterations. Floaters are periodically removed during training. ⟦REV⟧The experiments are implemented in PyTorch and executed on an NVIDIA RTX 4090 GPU.⟦/REV⟧

## Quantitative and Qualitative Results

Table 1. Performance comparisons of sparse-view synthesis on Mip-NeRF 360 (4/6/9 views). LPIPS* denotes LPIPS × 10².

[[[TABLE_MIP360]]]

Table 2. Performance comparisons of sparse-view synthesis on LLFF (4/6/9 views). LPIPS* denotes LPIPS × 10².

[[[TABLE_LLFF]]]

**Mip-NeRF 360 and LLFF.** Table 1 reports the results on Mip-NeRF 360 under the 4-, 6-, and 9-view settings. ⟦REV⟧On Mip-NeRF 360, SynGS achieves higher PSNR and SSIM values relative to the evaluated baseline methods under the 4-, 6-, and 9-view configurations,⟦/REV⟧ with a more noticeable PSNR difference in the 4-view case: 25.91 dB, compared with 22.35 dB for D²GS <sup>[19]</sup>. However, D²GS obtains lower LPIPS values across the three settings, indicating an advantage in perceptual similarity. Table 2 shows a similar trend. With four views, SynGS achieves favorable results in PSNR, SSIM, and LPIPS; ⟦REV⟧in the six-view LLFF setting, SynGS records higher PSNR and SSIM values than the baseline approaches included in the comparison,⟦/REV⟧ with LPIPS close to the lowest reported value. ⟦REV⟧In the nine-view LLFF configuration, the performance differences among the evaluated 3DGS-based approaches are relatively limited. Compared with SynGS, D²GS⟦/REV⟧ <sup>[19]</sup> ⟦REV⟧reports a slightly higher PSNR and a lower LPIPS, whereas CoR-GS⟦/REV⟧ <sup>[12]</sup> ⟦REV⟧achieves a marginally higher SSIM.⟦/REV⟧ Overall, SynGS shows more pronounced improvements in the four- and six-view settings, suggesting that the proposed framework may be particularly beneficial when the geometric information available from the input views is severely limited.

**Qualitative Results.** Figure 3 shows the 4-view comparison on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete object boundaries, and preserves finer structures where baselines show broken contours or missing details.

![Figure 3. Qualitative comparison under the 4-view sparse-input setting on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete structural boundaries than the compared methods.](/Users/zhihu/Desktop/CUC/EI会议/CVMP2026_3DGS/figures/word_export/qualitative.png)

## Ablation Study



Table 3. Ablation study of SynGS components. LPIPS* denotes LPIPS × 10².

[[[TABLE_ABLATION]]]

⟦/REV⟧ Unlike Table 1, which reports dataset-wide averages, the ablation is a separate protocol and is not the 4-view mean in Table 1.

Visual Hull Initialization establishes the geometric baseline at 17.51 dB PSNR. Adding Depth Densification raises PSNR to 24.96 dB, the largest gain in the ablation. Adding DVR further improves the full configuration to 26.18 dB, with gains in SSIM and LPIPS.

*Visibility Balancing denotes Dynamic Visibility Regularization (DVR).

# CONCLUSION

We present SynGS for sparse-view 3DGS, combining **Visual Hull Initialization**, **VGGT-Guided Densification**, and **Dynamic Visibility Regularization** for more reliable initialization, geometry completion, and reduced sparse-view overfitting. SynGS shows more pronounced improvements under highly sparse-view conditions, particularly in PSNR and SSIM with four or six input views. ⟦REV⟧With nine input views, on Mip-NeRF 360, SynGS continues to outperform the compared approaches in terms of PSNR and SSIM, whereas its performance on LLFF is generally comparable to that of the other evaluated methods.⟦/REV⟧ However, the additional geometry introduced during initialization incurs memory and computational overhead. ⟦REV⟧Our future research will investigate ways to improve the efficiency of geometry augmentation, aiming to lower the associated computational and memory overhead without compromising reconstruction quality.⟦/REV⟧

References

Yang, J., Pavone, M., and Wang, Y., "FreeNeRF: Improving few-shot neural rendering with free frequency regularization," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 8254–8263 (2023). DOI: https://doi.org/10.1109/cvpr52729.2023.00798.

Niemeyer, M., Barron, J. T., Mildenhall, B., Sajjadi, M. S. M., Geiger, A., and Radwan, N., "RegNeRF: Regularizing neural radiance fields for view synthesis from sparse inputs," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5480–5490 (2022). DOI: https://doi.org/10.1109/cvpr52688.2022.00540.

Kerbl, B., Kopanas, G., Leimkühler, T., and Drettakis, G., "3D gaussian splatting for real-time radiance field rendering," ACM Transactions on Graphics 42(4), 139:1–139:14 (2023). DOI: https://doi.org/10.1145/3592433.

Lu, T., Yu, M., Xu, L., Xiangli, Y., Wang, L., Lin, D., and Dai, B., "Scaffold-GS: Structured 3D gaussians for view-adaptive rendering," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 20654–20664 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01952.

Schönberger, J. L. and Frahm, J.-M., "Structure-from-motion revisited," in [Proc. IEEE Conference on Computer Vision and Pattern Recognition (CVPR)], 4104–4113 (2016). DOI: https://doi.org/10.1109/cvpr.2016.445.

Chung, J., Oh, J., and Lee, K. M., "Depth-regularized optimization for 3D gaussian splatting in few-shot images," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)], 811–820 (2024). DOI: https://doi.org/10.1109/cvprw63382.2024.00086.

Xu, Y., Wang, L., Chen, M., Ao, S., Li, L., and Guo, Y., "DropoutGS: Dropping out gaussians for better sparse-view rendering," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 701–710 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.00074.

Park, H., Ryu, G., and Kim, W., "DropGaussian: Structural regularization for sparse-view gaussian splatting," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 21600–21609 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.02012.

Somraj, N. and Soundararajan, R., "ViP-NeRF: Visibility prior for sparse input neural radiance fields," in [Proc. ACM SIGGRAPH Conference], 1–11 (2023). DOI: https://doi.org/10.1145/3588432.3591539.

Li, J., Zhang, J., Bai, X., Zheng, J., Ning, X., Zhou, J., and Gu, L., "DNGaussian: Optimizing sparse-view 3D gaussian radiance fields with global-local depth normalization," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 20775–20785 (2024). DOI: https://doi.org/10.1109/cvpr52733.2024.01963.

Zhu, Z., Fan, Z., Jiang, Y., and Wang, Z., "FSGS: Real-time few-shot view synthesis using gaussian splatting," in [Proc. European Conference on Computer Vision (ECCV)], 145–163 (2024). DOI: https://doi.org/10.1007/978-3-031-72933-1_9.

Zhang, J., Li, J., Yu, X., Huang, L., Gu, L., Zheng, J., and Bai, X., "CoR-GS: Sparse-view 3D gaussian splatting via co-regularization," in [Proc. European Conference on Computer Vision (ECCV)], 335–352 (2024). DOI: https://doi.org/10.1007/978-3-031-73232-4_19.

Mildenhall, B., Srinivasan, P. P., Tancik, M., Barron, J. T., Ramamoorthi, R., and Ng, R., "NeRF: Representing scenes as neural radiance fields for view synthesis," Communications of the ACM 65(1), 99–106 (2021). DOI: https://doi.org/10.1145/3503250.

Wang, G., Chen, Z., Loy, C. C., and Liu, Z., "SparseNeRF: Distilling depth ranking for few-shot novel view synthesis," in [Proc. IEEE/CVF International Conference on Computer Vision (ICCV)], 9031–9042 (2023). DOI: https://doi.org/10.1109/iccv51070.2023.00832.

Zheng, Y., Jiang, Z., He, S., Sun, Y., Dong, J., Zhang, H., and Du, Y., "NexusGS: Sparse view synthesis with epipolar depth priors in 3D Gaussian splatting," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 26800–26809 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.02496.

Yang, L., Kang, B., Huang, Z., Zhao, Z., Xu, X., Feng, J., and Zhao, H., "Depth anything V2," in [Advances in Neural Information Processing Systems (NeurIPS)], 37, 21875–21911 (2024). DOI: https://doi.org/10.52202/079017-0688.

Wang, J., Chen, M., Karaev, N., Vedaldi, A., Rupprecht, C., and Novotny, D., "VGGT: Visual geometry grounded transformer," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5294–5306 (2025). DOI: https://doi.org/10.1109/cvpr52734.2025.00499.

Laurentini, A., "The visual hull concept for silhouette-based image understanding," IEEE Transactions on Pattern Analysis and Machine Intelligence 16(2), 150–162 (1994). DOI: https://doi.org/10.1109/34.273735.

Song, M., Lin, X., Zhang, D., Li, H., Li, X., Du, B., and Qi, L., "D2GS: Depth-and-density guided gaussian splatting for stable and accurate sparse-view reconstruction." arXiv preprint arXiv:2510.08566 (2025). DOI: https://doi.org/10.48550/arXiv.2510.08566.

Barron, J. T., Mildenhall, B., Verbin, D., Srinivasan, P. P., and Hedman, P., "Mip-NeRF 360: Unbounded anti-aliased neural radiance fields," in [Proc. IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)], 5460–5469 (2022). DOI: https://doi.org/10.1109/cvpr52688.2022.00539.

Mildenhall, B., Srinivasan, P. P., Ortiz-Cayon, R., Kalantari, N. K., Ramamoorthi, R., Ng, R., and Kar, A., "Local light field fusion: Practical view synthesis with prescriptive sampling guidelines," ACM Transactions on Graphics 38(4), 29:1–29:14 (2019). DOI: https://doi.org/10.1145/3306346.3322980.
