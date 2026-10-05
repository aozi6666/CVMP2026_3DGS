# 参考文献状态（2026-10-01）

> bib 仅核清条目。近 3 年为主；经典 NeRF/3DGS 例外。

## 2025/2026 批次（已核清 + 已挂正文）

脚本：`bash notes/verify_2025_2026.sh` — A/B/C 题名与 id 均匹配。

| Key | 核验 | 挂载 |
|-----|------|------|
| `Fang26_DropAnSH` | CVPR 2026, OpenAccess 33312–33322；arXiv:2602.20933 | Method DVR；Related dropout |
| `Zhou26_GDAGS` | arXiv:2508.09239 题名作者；ICLR 2026（页码未核） | Method densify；Related density |
| `Zheng25_NexusGS` | CVPR 2025, OpenAccess 26800–26809；arXiv:2503.18794 | Method densify；Related depth prior |
| `Patle25_ADGS` | arXiv:2509.11003 题名作者；SIGGRAPH Asia 2025（页码未核） | Method densify；Related densify |

已在 bib、勿重复：DropGaussian / DropoutGS / D²GS / VGGT / LoopSparseGS。

## Round-2 已写入（12）

| Key | 核验 | 挂载 |
|-----|------|------|
| `Lu24_ScaffoldGS` | CVPR 2024, 20654–20664 | Intro + Related 3DGS |
| `Yu24_MipSplatting` | CVPR 2024, 19447–19456 | Intro + Related 3DGS |
| `Guedon24_SuGaR` | CVPR 2024, 5354–5363 | Related surface GS |
| `Barron23_ZipNeRF` | ICCV 2023, 19697–19705 | Related NeRF |
| `Charatan24_pixelSplat` | CVPR 2024, 19457–19467 | Related feed-forward |
| `Huang24_2DGS` | arXiv:2403.17888 | Related surface GS |
| `Cheng24_GaussianPro` | arXiv:2402.14650 | Related + Method densify |
| `Leroy24_MASt3R` | arXiv:2406.09756 | Related stereo/matching |
| `Bochkovskii24_DepthPro` | arXiv:2410.02073 | Related 深度先验 |
| `Yariv23_BakedSDF` | arXiv:2302.14859 | Related NeRF/surface |
| `Cao24_MVSFormerPP` | arXiv:2401.11673 | Related MVS |
| `Wang24_MoGe` | arXiv:2410.19115 | Related 单目几何 |

## Method-oriented（verify_method10）

| Key | arXiv | Method 挂载 |
|-----|-------|-------------|
| `Kheradmand24_3DGSMCMC` | 2404.09591 | DVR |
| `Yu24_GOF` | 2404.10772 | VH |
| `Li24_GSOctree` | 2406.18199 | Overall |
| `Zhang24_PixelGS` | 2403.15530 | bib 保留；densify 现以 GDAGS 为主 |
| `Fang24_MiniSplatting` | 2403.14166 | DVR |
| `Zhang24_RaDeGS` | 2406.01467 | Densify |
| `Sabour24_SpotlessSplats` | 2406.20055 | DVR |

## 作废 ID（勿再用）

- `2410.16145`（物理论文，非 MoGe）
- 猜错的 MVSFormer++/GOF/NeuS2 旧 id
- **排除** `2304.02643` Segment Anything

## 刻意不写进实验表

InstantSplat / MVSplat / pixelSplat / MASt3R 等仅 Related 对比。
