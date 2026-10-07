#!/usr/bin/env python3
"""Build SynGS_SPIE_A4.docx from confirmed manuscript via pandoc + SPIE reference template."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "Template" / "文件2：ProcSPIETemplate_A4.docx"
OUT = ROOT / "SynGS_SPIE_A4.docx"
FIG = ROOT / "figures" / "word_export"
BBL = ROOT / "main.bbl"
WORKDIR = ROOT / "word_build"
MD = WORKDIR / "paper.md"

REFMAP = {
    "fig:framework": "Figure 1",
    "fig:vggt_depth": "Figure 2",
    "fig:qualitative": "Figure 3",
    "tab:mip360": "Table 1",
    "tab:llff": "Table 2",
    "tab:ablation": "Table 3",
    "sec:depth_densify": "Sec. 3.3",
    "sec:dvr": "Sec. 3.4",
    "sec:visual_hull": "Sec. 3.2",
    "sec:overall": "Sec. 3.1",
    "eq:delta_d": "(1)",
    "eq:dropout_ratio": "(2)",
    "eq:color_loss": "(3)",
    "eq:dvr_loss": "(4)",
}


def load_cite_map() -> dict[str, int]:
    keys = re.findall(r"\\bibitem\{([^}]+)\}", BBL.read_text(encoding="utf-8"))
    return {k: i for i, k in enumerate(keys, 1)}


def load_refs() -> list[str]:
    text = BBL.read_text(encoding="utf-8")
    items = re.split(r"\\bibitem\{[^}]+\}", text)[1:]
    refs = []
    for raw in items:
        raw = re.sub(r"\\newblock\s*", " ", raw)
        raw = re.sub(r"\\emph\{([^}]*)\}", r"\1", raw)
        raw = re.sub(r"\{\\em\s+([^}]*)\}", r"\1", raw)
        raw = re.sub(r"\\textbf\{([^}]*)\}", r"\1", raw)
        raw = re.sub(r"\\textsuperscript\{([^}]*)\}", r"\1", raw)
        raw = re.sub(r"\\nolinebreak\\hspace\{[^}]*\}", "", raw)
        raw = re.sub(r"\$\^\\circ\$", "°", raw)
        raw = re.sub(r"\$\^\{\\circ\}\$", "°", raw)
        raw = re.sub(r"\\circ", "°", raw)
        raw = raw.replace(r"\&", "&").replace(r"\~", " ").replace(r"\,", " ").replace(r"\-", "")
        raw = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", raw)
        raw = raw.replace("{", "").replace("}", "")
        raw = re.sub(r"\s+", " ", raw).strip(" .\n")
        if raw and not raw.endswith("."):
            raw += "."
        refs.append(raw)
    return refs


def protect_math(text: str):
    slots = []

    def store(m):
        slots.append(m.group(0))
        return f"@@MATH{len(slots)-1}@@"

    text = re.sub(r"\$\$[\s\S]*?\$\$", store, text)
    text = re.sub(r"\$[^$\n]+\$", store, text)
    return text, slots


def restore_math(text: str, slots: list[str]) -> str:
    for i, s in enumerate(slots):
        text = text.replace(f"@@MATH{i}@@", s)
    return text


def cite_to_sup(text: str, cmap: dict[str, int]) -> str:
    def repl(m):
        nums = []
        for k in m.group(1).split(","):
            k = k.strip()
            if k not in cmap:
                raise KeyError(k)
            nums.append(str(cmap[k]))
        return f"<sup>[{','.join(nums)}]</sup>"

    return re.sub(r"\\cite\{([^}]+)\}", repl, text)


def strip_tex(text: str, cmap: dict[str, int]) -> str:
    def figref(m):
        return REFMAP.get(m.group(1), m.group(1))

    # Resolve latex refs before '~' -> space, to avoid "Figure Figure 1"
    text = re.sub(r"Figure~\\ref\{([^}]+)\}", figref, text)
    text = re.sub(
        r"Tables~\\ref\{([^}]+)\} and~\\ref\{([^}]+)\}",
        lambda m: f"{REFMAP.get(m.group(1), m.group(1))} and {REFMAP.get(m.group(2), m.group(2))}",
        text,
    )
    text = re.sub(r"Table~\\ref\{([^}]+)\}", figref, text)
    text = re.sub(r"Sec\.~\\ref\{([^}]+)\}", figref, text)
    text = re.sub(r"\\ref\{([^}]+)\}", figref, text)
    text = re.sub(r"\\label\{[^}]+\}", "", text)

    text = text.replace("~", " ")
    text = re.sub(r"\$\^\{\\circ\}\$", "°", text)
    text = re.sub(r"\$\^\\circ\$", "°", text)
    text = text.replace(r"D$^2$GS", "D²GS").replace(r"D\textsuperscript{2}GS", "D²GS")
    text = text.replace(r"D$^{2}$GS", "D²GS")
    text, slots = protect_math(text)
    text = cite_to_sup(text, cmap)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"*\1*", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", text)
    text = re.sub(r"\\circ", "°", text)
    text = text.replace(r"\&", "&").replace(r"\%", "%").replace(r"\,", " ")
    # remove remaining simple commands without touching math placeholders
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) if m.lastindex else "", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\s+", " ", text).strip()
    return restore_math(text, slots)


def read_tex(path: Path) -> str:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("%"):
            continue
        lines.append(line)
    return "\n".join(lines)


def extract_body(tex: str, cmap: dict[str, int]) -> str:
    """Convert a section/subsection tex chunk (no figures/tables) to markdown."""
    tex = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", "", tex, flags=re.S)
    tex = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", tex, flags=re.S)
    tex = re.sub(r"\\input\{[^}]+\}", "", tex)
    tex = re.sub(r"\\section\{[^}]*\}", "", tex)
    tex = re.sub(r"\\label\{[^}]*\}", "", tex)

    out = []

    def flush_para(p: str):
        p = p.strip()
        if not p:
            return
        out.append(strip_tex(p, cmap))

    # itemize
    def itemize_repl(m):
        items = re.findall(r"\\item\s+(.*?)(?=\\item|\Z)", m.group(1), flags=re.S)
        return "\n\n" + "\n\n".join("- " + strip_tex(it, cmap) for it in items) + "\n\n"

    tex = re.sub(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", itemize_repl, tex, flags=re.S)

    # equations
    def eq_repl(m):
        body = re.sub(r"\\label\{[^}]+\}", "", m.group(1)).strip()
        return f"\n\n$$\n{body}\n$$\n\n"

    tex = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", eq_repl, tex, flags=re.S)

    # subsections
    parts = re.split(r"(\\subsection\{[^}]+\})", tex)
    i = 0
    while i < len(parts):
        part = parts[i]
        sm = re.match(r"\\subsection\{([^}]+)\}", part)
        if sm:
            out.append(f"## {sm.group(1).strip()}")
            i += 1
            continue
        # split paragraphs
        for block in re.split(r"\n\s*\n", part):
            block = block.strip()
            if not block:
                continue
            if block.startswith("##") or block.startswith("- ") or block.startswith("$$"):
                out.append(block)
            elif "$$\n" in block or block.startswith("$$"):
                out.append(block)
            else:
                # may contain inline itemize leftovers already expanded
                if "\n\n- " in block or block.startswith("- "):
                    out.append(block)
                else:
                    flush_para(block)
        i += 1
    return "\n\n".join([x for x in out if x and x.strip()])


def build_markdown(cmap: dict[str, int], refs: list[str]) -> str:
    main = read_tex(ROOT / "main.tex")
    abs_text = strip_tex(main.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0], cmap)
    kw = "Novel View Synthesis, 3D Gaussian Splatting, Few-shot reconstruction, Geometry Prior-Guided Reconstruction, Vision Transformer"

    intro = extract_body(read_tex(ROOT / "sections" / "01_introduction.tex"), cmap)
    related = extract_body(read_tex(ROOT / "sections" / "02_related_work.tex"), cmap)
    m1 = extract_body(read_tex(ROOT / "sections" / "method" / "01_overall_framework.tex"), cmap)
    m2 = extract_body(read_tex(ROOT / "sections" / "method" / "02_visual_hull_init.tex"), cmap)
    m3tex = read_tex(ROOT / "sections" / "method" / "03_depth_guided_densification.tex")
    m3tex = re.sub(
        r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}",
        "\n\n<<<FIG2>>>\n\n",
        m3tex,
        flags=re.S,
    )
    m3a, m3b = m3tex.split("<<<FIG2>>>")
    m3_before = extract_body(m3a, cmap)
    m3_after = extract_body(m3b, cmap)
    m4 = extract_body(read_tex(ROOT / "sections" / "method" / "04_dynamic_visibility_reg.tex"), cmap)
    e1 = extract_body(read_tex(ROOT / "sections" / "experiments" / "01_experimental_setup.tex"), cmap)
    e2 = extract_body(read_tex(ROOT / "sections" / "experiments" / "02_quantitative_and_qualitative.tex"), cmap)
    e3 = extract_body(read_tex(ROOT / "sections" / "experiments" / "05_ablation_study.tex"), cmap)
    conc = extract_body(read_tex(ROOT / "sections" / "05_conclusion.tex"), cmap)

    fw = FIG / "framework.png"
    vg = FIG / "vggt_depth.png"
    qf = FIG / "qualitative.png"

    lines = []
    a = lines.append
    a("% SynGS: synergizing explicit geometry and transformer depth priors for sparse-view 3D Gaussian Splatting")
    a("% Junjie Geng*a, Ao Zhanga, and Lian Duana")
    a("% aCommunication University of China, State Key Laboratory of Media Convergence and Communication, Intelligent Network and Media Research Center, No. 1 Dingfuzhuang East Street, Chaoyang District, Beijing 100024, China")
    a("% *gjj@cuc.edu.cn")
    a("")
    a("# ABSTRACT")
    a("")
    a(abs_text)
    a("")
    a(f"**Keywords:** {kw}")
    a("")
    a("# 1. INTRODUCTION")
    a("")
    a(intro)
    a("")
    a("# 2. RELATED WORK")
    a("")
    a(related)
    a("")
    a("# 3. METHOD")
    a("")
    a(m1)
    a("")
    a(f"![Figure 1. Overview of the SynGS pipeline. The third stage applies Dynamic Visibility Regularization (DVR).]({fw})")
    a("")
    a(m2)
    a("")
    a(m3_before)
    a("")
    a(f"![Figure 2. VGGT-Depth prior used for depth-guided point cloud densification.]({vg})")
    a("")
    a(m3_after)
    a("")
    a(m4)
    a("")
    a("# 4. EXPERIMENTS")
    a("")
    a(e1)
    a("")
    a("## Quantitative and Qualitative Results")
    a("")
    a("Table 1. Performance comparisons of sparse-view synthesis on Mip-NeRF 360 (4/6/9 views). LPIPS* denotes LPIPS × 10².")
    a("")
    a("| Group | Methods | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ |")
    a("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    a("| | | 4-view | 4-view | 4-view | 6-view | 6-view | 6-view | 9-view | 9-view | 9-view |")
    for r in [
        ("NeRF-based", "RegNeRF", 19.88, 12.59, 0.841, 20.72, 13.41, 0.847, 19.70, 13.68, 0.852),
        ("", "SparseNeRF", 17.76, 12.83, 0.845, 19.74, 13.42, 0.861, 21.56, 14.36, 0.873),
        ("3DGS-based", "3DGS", 10.80, 20.31, 0.899, 8.38, 22.12, 0.913, 6.42, 24.29, 0.930),
        ("", "CoR-GS", 11.76, 20.45, 0.856, 9.28, 22.57, 0.901, 7.04, 24.73, 0.926),
        ("", "DropGaussian", 11.57, 21.76, 0.837, 8.61, 22.98, 0.895, 8.02, 24.10, 0.915),
        ("", "D²GS", 2.58, 22.35, 0.923, 2.34, 24.74, 0.937, 2.11, 27.13, 0.941),
        ("", "SynGS (Ours)", 3.89, 25.91, 0.948, 3.43, 27.93, 0.953, 3.02, 29.21, 0.961),
    ]:
        a("| " + " | ".join(map(str, r)) + " |")
    a("")
    a("Table 2. Performance comparisons of sparse-view synthesis on LLFF (4/6/9 views). LPIPS* denotes LPIPS × 10².")
    a("")
    a("| Group | Methods | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ | LPIPS*↓ | PSNR↑ | SSIM↑ |")
    a("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    a("| | | 4-view | 4-view | 4-view | 6-view | 6-view | 6-view | 9-view | 9-view | 9-view |")
    for r in [
        ("NeRF-based", "RegNeRF", 29.65, 18.55, 0.587, 22.61, 19.08, 0.760, 18.39, 22.86, 0.820),
        ("", "FreeNeRF", 30.85, 19.09, 0.624, 23.06, 19.81, 0.763, 17.94, 23.08, 0.823),
        ("3DGS-based", "3DGS", 22.93, 19.32, 0.649, 13.45, 23.80, 0.814, 9.68, 25.44, 0.860),
        ("", "CoR-GS", 19.66, 20.45, 0.696, 12.53, 23.87, 0.840, 8.94, 26.70, 0.874),
        ("", "DropGaussian", 21.93, 19.80, 0.621, 13.79, 23.41, 0.803, 9.40, 25.87, 0.868),
        ("", "D²GS", 17.98, 22.35, 0.746, 13.85, 23.91, 0.846, 8.91, 26.80, 0.871),
        ("", "SynGS (Ours)", 16.92, 23.92, 0.762, 12.54, 25.17, 0.848, 8.96, 26.71, 0.871),
    ]:
        a("| " + " | ".join(map(str, r)) + " |")
    a("")
    a(e2)
    a("")
    a(f"![Figure 3. Qualitative comparison under the 4-view sparse-input setting on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete structural boundaries than the compared methods.]({qf})")
    a("")
    a("## Ablation Study")
    a("")
    a(e3)
    a("")
    a("Table 3. Ablation study of SynGS components. LPIPS* denotes LPIPS × 10².")
    a("")
    a("| Visual Hull Init | Depth Densification | Visibility Balancing* | SSIM↑ | PSNR↑ | LPIPS*↓ |")
    a("|:---:|:---:|:---:|---:|---:|---:|")
    a("| √ |  |  | 0.865 | 17.51 | 12.80 |")
    a("| √ | √ |  | 0.902 | 24.96 | 5.20 |")
    a("| √ | √ | √ | **0.943** | **26.18** | **3.98** |")
    a("")
    a("*Visibility Balancing denotes Dynamic Visibility Regularization (DVR).")
    a("")
    a("# 5. CONCLUSION")
    a("")
    a(conc)
    a("")
    a("# REFERENCES")
    a("")
    for i, r in enumerate(refs, 1):
        a(f"[{i}] {r}")
        a("")
    return "\n".join(lines)


def run_pandoc(md_path: Path, out_path: Path) -> None:
    cmd = [
        "pandoc",
        str(md_path),
        "-f",
        "markdown+tex_math_dollars+raw_html+pipe_tables",
        "-t",
        "docx",
        f"--reference-doc={TEMPLATE}",
        "-o",
        str(out_path),
    ]
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def set_run_font(run, name="Times New Roman", size=None, bold=None):
    run.font.name = name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        from docx.oxml import OxmlElement

        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def style_or(doc, name):
    try:
        return doc.styles[name]
    except KeyError:
        return doc.styles["Normal"]


def polish(docx_path: Path) -> None:
    doc = Document(str(docx_path))
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(4.94)
        sec.left_margin = Cm(1.93)
        sec.right_margin = Cm(1.93)

    # Rebuild front matter
    body = doc.element.body
    intro_p = None
    for p in doc.paragraphs:
        if p.text.strip().startswith("1. INTRODUCTION"):
            intro_p = p._p
            break
    keep = []
    seen = False
    sectPr = None
    for c in list(body):
        if c.tag == qn("w:sectPr"):
            sectPr = c
            continue
        if intro_p is not None and c is intro_p:
            seen = True
        if seen:
            keep.append(c)
    for c in list(body):
        body.remove(c)

    def add(text, style, align=None, size=None, bold=None):
        p = doc.add_paragraph(style=style_or(doc, style))
        if align is not None:
            p.alignment = align
        if text:
            run = p.add_run(text)
            set_run_font(run, "Times New Roman", size=size, bold=bold)
        return p

    add(
        "SynGS: synergizing explicit geometry and transformer depth priors for sparse-view 3D Gaussian Splatting",
        "SPIE paper title",
        WD_ALIGN_PARAGRAPH.CENTER,
        16,
        True,
    )
    add("Junjie Geng*a, Ao Zhanga, and Lian Duana", "SPIE Authors-Affils", WD_ALIGN_PARAGRAPH.CENTER, 12)
    add(
        "aCommunication University of China, State Key Laboratory of Media Convergence and Communication, Intelligent Network and Media Research Center, No. 1 Dingfuzhuang East Street, Chaoyang District, Beijing 100024, China",
        "SPIE Authors-Affils",
        WD_ALIGN_PARAGRAPH.CENTER,
        10,
    )
    add("*gjj@cuc.edu.cn", "SPIE body text", WD_ALIGN_PARAGRAPH.CENTER, 10)

    # ABSTRACT block from pandoc may start with "# ABSTRACT" converted to Heading — insert before intro
    # keep already starts at 1. INTRODUCTION; insert abstract manually from md? Better: find ABSTRACT in original keep? 
    # Re-pandoc content includes ABSTRACT before intro. Since we discarded pre-intro, re-add abstract.
    abs_md = MD.read_text(encoding="utf-8")
    abs_body = abs_md.split("# ABSTRACT")[1].split("# 1. INTRODUCTION")[0]
    abs_body = abs_body.strip()
    kw_line = ""
    paras = []
    for block in abs_body.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("**Keywords:**"):
            kw_line = block.replace("**Keywords:**", "Keywords:")
        else:
            paras.append(block)
    add("ABSTRACT", "SPIE abstract title", WD_ALIGN_PARAGRAPH.CENTER, 11, True)
    for para in paras:
        p = add(para, "SPIE abstract body text", size=10)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if kw_line:
        add(kw_line, "SPIE keywords", size=10)

    body = doc.element.body
    # remove trailing sectPr if any from add_paragraph
    cur_sect = None
    for c in list(body):
        if c.tag == qn("w:sectPr"):
            cur_sect = c
            body.remove(c)
    for c in keep:
        body.append(c)
    if cur_sect is not None:
        body.append(cur_sect)
    elif sectPr is not None:
        body.append(sectPr)

    for p in doc.paragraphs:
        t = p.text.strip()
        st = p.style.name if p.style else ""
        if t.startswith("1. INTRODUCTION") or t.startswith("2. RELATED") or t.startswith("3. METHOD") or t.startswith("4. EXPERIMENTS") or t.startswith("5. CONCLUSION") or t == "REFERENCES":
            p.style = style_or(doc, "Heading 1")
        elif st.startswith("Heading 2") or t in (
            "Overall Framework",
            "Visual Hull Initialization",
            "VGGT-Guided Densification",
            "Dynamic Visibility Regularization",
            "Experimental Setup and Datasets",
            "Quantitative and Qualitative Results",
            "Ablation Study",
        ):
            p.style = style_or(doc, "Heading 2")
        elif t.startswith("Figure ") and len(t) > 7 and t[7].isdigit():
            p.style = style_or(doc, "SPIE figure caption")
        elif t.startswith("Table ") and len(t) > 6 and t[6].isdigit():
            p.style = style_or(doc, "SPIE table caption")
        elif re.match(r"^\[\d+\]\s", t):
            p.style = style_or(doc, "SPIE reference listing")
        elif t == "ABSTRACT":
            p.style = style_or(doc, "SPIE abstract title")
        elif t.startswith("Keywords:"):
            p.style = style_or(doc, "SPIE keywords")
        elif "paper title" in st.lower() or st == "Title":
            p.style = style_or(doc, "SPIE paper title")
        elif "author" in st.lower():
            p.style = style_or(doc, "SPIE Authors-Affils")
        elif "abstract" in st.lower():
            p.style = style_or(doc, "SPIE abstract body text")
        elif st not in ("Heading 1", "Heading 2", "SPIE figure caption", "SPIE table caption", "SPIE reference listing", "SPIE keywords", "SPIE paper title", "SPIE Authors-Affils", "SPIE abstract title", "SPIE abstract body text"):
            p.style = style_or(doc, "SPIE body text")
        for run in p.runs:
            set_run_font(run, "Times New Roman")

    for shape in doc.inline_shapes:
        try:
            shape.width = Cm(16.5)
        except Exception:
            pass

    superscript_citations(doc)
    doc.save(str(docx_path))


CITE_RUN_RE = re.compile(r"^\[\d+(?:,\d+)*\]$")


def superscript_citations(doc: Document) -> None:
    """Make in-text [n] / [n,m] citations superscript; skip References list entries."""
    in_refs = False
    for p in doc.paragraphs:
        t = p.text.strip()
        if t == "REFERENCES" or t.startswith("REFERENCES"):
            in_refs = True
            continue
        if in_refs:
            continue
        # Skip reference-style lines that begin with [n]
        if re.match(r"^\[\d+\]\s", t):
            continue
        for run in p.runs:
            if CITE_RUN_RE.match(run.text.strip()):
                run.font.superscript = True
                set_run_font(run, "Times New Roman")


def verify(docx_path: Path) -> None:
    import zipfile

    doc = Document(str(docx_path))
    texts = "\n".join(p.text for p in doc.paragraphs)
    table_text = "\n".join(c.text for t in doc.tables for row in t.rows for c in row.cells)
    all_text = texts + "\n" + table_text
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml")
    checks = {
        "title": "SynGS: synergizing explicit geometry" in texts,
        "corr_email": "gjj@cuc.edu.cn" in texts,
        "keywords": "Keywords:" in texts and "Vision Transformer" in texts,
        "fig_captions": all(x in texts for x in ("Figure 1.", "Figure 2.", "Figure 3.")),
        "table_captions": all(x in texts for x in ("Table 1.", "Table 2.", "Table 3.")),
        "syn_gs_ours_in_table": "SynGS (Ours)" in all_text,
        "refs_doi": "[1]" in texts and "DOI:" in texts,
        "no_chinese": not re.search(r"[\u4e00-\u9fff]", all_text),
        "editable_tables": len(doc.tables) >= 3,
        "images": len(doc.inline_shapes) >= 3,
        "editable_eq_omml": b"oMath" in xml,
        "intro_present": "Sparse inputs provide limited information" in texts,
        "cite_superscript": b'vertAlign w:val="superscript"' in xml or b"w:val=\"superscript\"" in xml,
    }
    print("VERIFY:")
    ok = True
    for k, v in checks.items():
        print(f"  {k}: {'OK' if v else 'FAIL'}")
        ok = ok and bool(v)
    sec = doc.sections[0]
    print(
        f"  margins_cm T/B/L/R: {sec.top_margin.cm:.2f}/{sec.bottom_margin.cm:.2f}/"
        f"{sec.left_margin.cm:.2f}/{sec.right_margin.cm:.2f}"
    )
    print(f"  page_cm: {sec.page_width.cm:.2f}x{sec.page_height.cm:.2f}")
    print(f"  paras={len(doc.paragraphs)} tables={len(doc.tables)} images={len(doc.inline_shapes)}")
    if not ok:
        raise SystemExit(1)


def main():
    WORKDIR.mkdir(exist_ok=True)
    cmap = load_cite_map()
    refs = load_refs()
    print(f"cites={len(cmap)} refs={len(refs)}")
    md = build_markdown(cmap, refs)
    MD.write_text(md, encoding="utf-8")
    print("wrote", MD, "chars", len(md))
    # sanity on math
    if "r_ is the maximum" in md or "(d)= d+" in md:
        raise SystemExit("math stripping still broken")
    tmp = WORKDIR / "pandoc_out.docx"
    run_pandoc(MD, tmp)
    shutil.copy2(tmp, OUT)
    polish(OUT)
    verify(OUT)
    print("DONE", OUT)


if __name__ == "__main__":
    main()
