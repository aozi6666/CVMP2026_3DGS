# Citation Audit + 专业处置建议

> 原则：**引用服务主张，不服务旧编号。**  
> 会议版只保留「正文真正支撑句子的文献」；编号交给 BibTeX。

正文占位 **26** 个；你列表 **48** 条。约一半可语义回收，其余必须重挂或外补。

---

## 0. 我作为学术写作的明确推荐（先做这个）

### 推荐总策略：**语义重建 bib（R1），不要修旧编号**

1. **丢弃**「正文 [n] = 列表第 n 条」假设（已证伪：SfM→VGGT、VGGT→LPIPS 等）。  
2. 对每个 `\cite`：**先读句子主张 → 再选文献 → 再写 BibTeX key**。  
3. **只收录被 cite 的条目**（SPIE 6 页尤其如此）；#31–#48 未引用的先不进 bib。  
4. **删除污染条** #25；合并重复 #5/#11。  
5. key 用可读名：`Kerbl23_3DGS`，禁止继续用 `ref24` 这种易与旧号混淆的 key。

**不推荐**：把 1–48 原样灌进 `references.bib` 再硬改编号——会再次埋雷。

---

## 1. 按「句子类型」选文献（出错率最低）

| 句子在主张什么 | 该引什么 | 怎么挑 |
|----------------|----------|--------|
| **方法首提**（NeRF / 3DGS / VGGT） | 原始论文 | 作者+年份+会议；用 CVF / ACM DL / 官方 GitHub bib |
| **对比方法 / Related 同类工作** | 你实验表里出现的方法 + 同问题代表性工作 | 表里有的必须能在 Related/Setup 对齐 |
| **数据集** | 数据集原论文 | Mip-NeRF 360 → Barron CVPR’22；LLFF → Mildenhall TOG’19（Local Light Field Fusion） |
| **指标定义** | 指标原论文 | SSIM → Wang TIP’04；LPIPS → Zhang CVPR’18 |
| **实现细节 / loss**（$\mathcal{L}_1$+D-SSIM） | 你跟随的框架原文 | 3DGS Kerbl 一文通常足够；不必硬凑两篇无关文 |
| **对比差异点**（“unlike compensated dropout”） | **被对比的那篇** | 必须是 DropGaussian（有 compensation），不能用 TrackGS |
| **经典工具**（SfM / COLMAP） | 领域标准引用 | COLMAP：Schönberger CVPR’16；不要用 Level-S²fM 冒充“传统 SfM” |
| **Visual Hull** | 经典或你方法真正依赖的几何文献 | 优先经典 VH / 多视图轮廓；你列表 #18–#20 可选 1–2 篇，勿引 Mip-NeRF 360 |
| **一般性困难陈述**（稀疏难、易过拟合） | 1 篇强相关代表作即可 | FreeNeRF / RegNeRF；**避免**学位论文、无关领域 |

---

## 2. 对你这篇：逐条「怎么搞」（可执行）

### 2.1 直接采用列表中的（高置信，建议保留）

| 用途 | 用你列表 | 建议 BibTeX key |
|------|----------|-----------------|
| FreeNeRF（稀疏过拟合） | #2 | `Yang23_FreeNeRF` |
| NeRF | #6 | `Mildenhall21_NeRF` |
| SparseNeRF | #7 | `Wang23_SparseNeRF` |
| DS-NeRF | #8 | `Deng22_DSNeRF` |
| RegNeRF | #9 | `Niemeyer22_RegNeRF` |
| 3DGS | #10 | `Kerbl23_3DGS` |
| DNGaussian | #12 | `Li24_DNGaussian` |
| FSGS | #13 | `Zhu24_FSGS` |
| SparseGS | #14 | `Xiong24_SparseGS` |
| 统计离群点过滤 | #22 | `Balta18_SOR` |
| VGGT | **#24**（不是 #30） | `Wang25_VGGT` |
| DropoutGS（稀疏 dropout 正则，可选） | #26 | `Xu25_DropoutGS` |
| Mip-NeRF 360 **数据集** | **#27** | `Barron22_MipNeRF360` |
| LLFF **数据集** | **#28** | `Mildenhall19_LLFF` |
| SSIM | #29 | `Wang04_SSIM` |
| LPIPS | #30 | `Zhang18_LPIPS` |

### 2.2 必须外补（列表不够或没有）

| 缺口 | 推荐标准引用 | 检索关键词（复制到 Google Scholar） |
|------|--------------|--------------------------------------|
| **SfM / COLMAP** | Schönberger & Frahm, **Structure-from-Motion Revisited**, CVPR 2016 | `COLMAP Structure-from-Motion Revisited Schönberger` |
| **DropGaussian**（有 opacity compensation；对应正文 unlike…） | Park et al., **DropGaussian**, CVPR 2025 | `DropGaussian Structural Regularization Sparse-view CVPR 2025` |
| **Depth-regularized 3DGS**（若 Intro 要保留 “depth-reg 3DGS” 而非重复 #5） | Chung et al. CVPRW 2024（你的 #5，保留一条即可） | 已有 |

可选加强（非必须）：
- Visual Hull 经典：Laurentini **The Visual Hull Concept for Silhouette-Based Image Understanding**, PAMI 1994 —— 比 #18–#20 更“标准教材级”。  
- 若不想加经典文，从 #18–#20 选 **1 篇**与“多视图轮廓/visual hull”最贴近的即可。

### 2.3 建议删或降级（易出错）

| 条目 | 建议 | 原因 |
|------|------|------|
| #25 加纳辍学论文 | **删除** | 污染，绝不能出现 |
| #5 与 #11 重复 | **只留一条** | 重复引用不专业 |
| #3 学位论文 | Intro 困难句 **可不引** 或换 FreeNeRF/RegNeRF | 会议审稿对学位论文引用不友好 |
| #1 国内综述 / #4 SIFT 文 | 非必要不引 | 与 SynGS 主张弱相关 |
| #15 SC-NeuS / #16 Sparse3D | Related 若写 “sparse 3DGS” 建议换成 **CoR-GS / DropGaussian** 等表内方法 | 表面/扩散 ≠ 你的 3DGS 主线 |
| #31–#48 | **默认不进会议 bib** | 未在正文出现；堆砌像凑数 |
| #42–#45 等被旧号误指者 | 不按号保留 | 与句子主张不符 |

### 2.4 正文里「一个占位两处语义」必须拆开

- 旧 `ref26`：Intro 讲 floater → 引 **DropoutGS / DropGaussian / depth-reg GS**；Method 讲 Visual Hull → 引 **VH 文献**。  
  → **拆成两个 key**，否则必然有一处错。  
- 旧 `ref11`：只说 rasterization 效率 → **只引 Kerbl23**，删重复的 depth-reg 条。  
- 旧 `ref42,ref43`：训练 loss → **引 Kerbl23**（3DGS 原 loss）；若某处讨论指标定义再引 SSIM/LPIPS。

---

## 3. 缺文献时：怎么检索才不容易错

### 3.1 检索顺序（推荐）
1. **Google Scholar** 精确题名 / 作者+关键词  
2. **CVF Open Access**（CVPR/ICCV/ECCV）下官方 bib  
3. **项目页 / 官方 GitHub** 的 Citation 块（VGGT、3DGS 都有）  
4. arXiv 仅作预印本补充；最终尽量用 **正式会议/期刊版本**（年份、页码以正式版为准）

### 3.2 录取规则（满足再写入 bib）
- [ ] 标题、作者、年份、会议/期刊 **与 PDF 首页一致**  
- [ ] 你在正文中的表述，确实是该文支持的主张（不是“同领域随便一篇”）  
- [ ] 若是对比方法：最好与 **实验表中的方法名**一致  
- [ ] 一篇一个职责；不要一篇同时冒充 SfM + VGGT + 数据集  

### 3.3 从「其他地方引入」的合法来源
- 你实验对比过的方法论文（CoR-GS、D²GS、DropGaussian…）— **优先**  
- 方法所依赖的 backbone / 数据集 / 指标原论文 — **必须**  
- 经典工具论文（COLMAP、Visual Hull）— **标准且安全**  
- **不要**：从无关综述、错误自动生成列表、或交叉学科串台条目里“捡编号”

---

## 4. 建议的会议版最小引用集（约 18–22 篇）

**必引**  
FreeNeRF；NeRF；SparseNeRF；DS-NeRF；RegNeRF；3DGS；DNGaussian；FSGS；SparseGS；COLMAP；VGGT；Visual Hull（经典或 #18–20 择一）；Balta SOR；DropGaussian；DropoutGS（可选）；Mip-NeRF 360；LLFF；SSIM；LPIPS；Chung depth-reg 3DGS（可选一条）。

**表内还有但 Related 未写全的**（建议 Related/Setup 语义对齐时补 cite，避免“表有文无”）  
CoR-GS、D²GS、DropGaussian（若作 baseline）。

---

## 5. 操作流程（你确认后我可以执行）

```text
1) 定最小文献清单（上表）
2) 从 CVF/ACM/官方页导出/手写 references.bib（可读 key）
3) 全文替换 \cite{refN} → 新 key（按句子语义，拆开双重用途）
4) 编译 bibtex；人工抽查：每条 cite 旁边读一句，是否“这篇真支持这句”
5) 终检：无 #25；无重复；数据集/指标/VGGT/SfM/DropGaussian 全部对上
```

---

## 6. 请你拍板（我按此执行，不再猜）

我的默认专业选择如下（你可改）：

| 项 | 默认推荐 |
|----|----------|
| B1 | **R1 语义重挂** |
| B2 | **补 COLMAP (Schönberger CVPR’16)**，不用 #17 冒充传统 SfM |
| B3 | **补 DropGaussian** 作为 compensation 对比；DropoutGS 可另作相关工作 |
| B4 | **#31–#48 不进会议 bib**（未引用） |
| B5 | Related 里 **15/16 换成更贴 3DGS 的表内方法**（或删这两 cite） |
| Visual Hull | 优先 **Laurentini PAMI’94**；若你坚持只用现有列表 → 用 #18–#20 选 1–2 |
| Intro `ref3` | **不引学位论文**；与 `ref2` 合并引 FreeNeRF 或再加 RegNeRF |
| loss 的 ref42/43 | **改引 Kerbl23**；SSIM/LPIPS 仅在谈指标时引用 |

回复：`按你默认执行` 或逐条改 B2/B3/…  
确认后我再改 `references.bib` + `sections` 的 `\cite{}`（这一步才会动正文引用）。

---

## 附录：旧占位速查（勿再当真理）

| 占位 | 正文在说什么 | 列表错指风险 |
|------|--------------|--------------|
| ref24 | SfM | 旧列表 #24=VGGT |
| ref30 | VGGT | 旧列表 #30=LPIPS |
| ref44/45 | 数据集 | 应为 #27/#28 |
| ref29 | 去噪 | 应为 #22 |
| ref40 | compensated dropout | 应补 DropGaussian |
| ref25 | — | 污染，删除 |
