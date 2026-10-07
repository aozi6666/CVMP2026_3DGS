#!/usr/bin/env python3
"""Build SynGS_SPIE_A4.docx from confirmed manuscript via pandoc + SPIE reference template."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "Template" / "文件2：ProcSPIETemplate_A4.docx"
OUT = ROOT / "SynGS_SPIE_A4.docx"
OUT_COPY = ROOT / "output" / "SynGS_SPIE_A4.docx"
FIG = ROOT / "figures" / "word_export"
BBL = ROOT / "main.bbl"
WORKDIR = ROOT / "word_build"
MD = WORKDIR / "paper.md"

MARKER_T1 = "[[[TABLE_MIP360]]]"
MARKER_T2 = "[[[TABLE_LLFF]]]"
MARKER_T3 = "[[[TABLE_ABLATION]]]"

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

CITE_RUN_RE = re.compile(r"^\[\d+(?:,\d+)*\]$")


def load_cite_map() -> dict[str, int]:
    keys = re.findall(r"\\bibitem\{([^}]+)\}", BBL.read_text(encoding="utf-8"))
    return {k: i for i, k in enumerate(keys, 1)}


_ACCENT = {
    '"': {"a": "ä", "e": "ë", "i": "ï", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü"},
    "'": {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "n": "ń", "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú"},
    "`": {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù"},
    "^": {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"},
    "~": {"n": "ñ", "a": "ã", "o": "õ"},
}


def _accent_repl(mark: str):
    table = _ACCENT[mark]

    def repl(m):
        return table.get(m.group(1), m.group(1))

    return repl


def latex_to_plain(raw: str) -> str:
    raw = re.sub(r"\\newblock\s*", " ", raw)
    raw = re.sub(r"\\emph\{([^}]*)\}", r"\1", raw)
    raw = re.sub(r"\{\\em\s+([^}]*)\}", r"\1", raw)
    raw = re.sub(r"\\textbf\{([^}]*)\}", r"\1", raw)
    raw = re.sub(r"\{\\bf\s+([^}]*)\}", r"\1", raw)
    raw = re.sub(r"\\textsuperscript\{([^}]*)\}", r"\1", raw)
    raw = re.sub(r"\\nolinebreak\\hspace\{[^}]*\}", "", raw)
    raw = re.sub(r"\$\^\\circ\$", "°", raw)
    raw = re.sub(r"\$\^\{\\circ\}\$", "°", raw)
    raw = re.sub(r"\\circ", "°", raw)
    for mark in ('"', "'", "`", "^", "~"):
        esc = re.escape(mark)
        raw = re.sub(rf"\\{esc}\{{([A-Za-z])\}}", _accent_repl(mark), raw)
        raw = re.sub(rf"\\{esc}([A-Za-z])", _accent_repl(mark), raw)
    raw = raw.replace(r"\&", "&").replace(r"\%", "%")
    raw = raw.replace(r"\~", " ").replace(r"\,", " ").replace(r"\-", "")
    raw = raw.replace(r"\ ", " ").replace(r"\.", ".")
    raw = raw.replace("``", '"').replace("''", '"').replace("`", "'")
    raw = raw.replace("---", "—").replace("--", "–")
    raw = raw.replace("~", " ")
    raw = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", raw)
    raw = raw.replace("{", "").replace("}", "").replace("\\", "")
    raw = re.sub(r"\s+", " ", raw).strip(" .\n")
    if raw and not raw.endswith("."):
        raw += "."
    return raw


def load_refs() -> list[str]:
    text = BBL.read_text(encoding="utf-8")
    items = re.split(r"\\bibitem\{[^}]+\}", text)[1:]
    refs = []
    for raw in items:
        plain = latex_to_plain(raw)
        if plain:
            refs.append(plain)
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


def extract_body(tex: str, cmap: dict[str, int], keep_subsections: bool = True) -> str:
    tex = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", "", tex, flags=re.S)
    tex = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", "", tex, flags=re.S)
    tex = re.sub(r"\\input\{[^}]+\}", "", tex)
    tex = re.sub(r"\\section\{[^}]*\}", "", tex)
    tex = re.sub(r"\\label\{[^}]*\}", "", tex)

    out = []

    def itemize_repl(m):
        items = re.findall(r"\\item\s+(.*?)(?=\\item|\Z)", m.group(1), flags=re.S)
        return "\n\n" + "\n\n".join("- " + strip_tex(it, cmap) for it in items) + "\n\n"

    tex = re.sub(r"\\begin\{itemize\}(.*?)\\end\{itemize\}", itemize_repl, tex, flags=re.S)

    def eq_repl(m):
        body = re.sub(r"\\label\{[^}]+\}", "", m.group(1)).strip()
        return f"\n\n$$\n{body}\n$$\n\n"

    tex = re.sub(r"\\begin\{equation\}(.*?)\\end\{equation\}", eq_repl, tex, flags=re.S)

    parts = re.split(r"(\\subsection\{[^}]+\})", tex)
    i = 0
    while i < len(parts):
        part = parts[i]
        sm = re.match(r"\\subsection\{([^}]+)\}", part)
        if sm:
            if keep_subsections:
                out.append(f"## {sm.group(1).strip()}")
            i += 1
            continue
        for block in re.split(r"\n\s*\n", part):
            block = block.strip()
            if not block:
                continue
            if block.startswith("##") or block.startswith("- ") or block.startswith("$$") or "$$\n" in block:
                out.append(block)
            else:
                t = strip_tex(block, cmap)
                if t:
                    out.append(t)
        i += 1
    return "\n\n".join([x for x in out if x and x.strip()])


def drop_md_headings(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not ln.startswith("#")]
    return "\n".join(lines).strip()


def build_markdown(cmap: dict[str, int], refs: list[str]) -> str:
    main = read_tex(ROOT / "main.tex")
    abs_text = strip_tex(main.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0], cmap)
    kw = "Novel View Synthesis, 3D Gaussian Splatting, Few-shot reconstruction, Geometry Prior-Guided Reconstruction, Vision Transformer"

    intro = extract_body(read_tex(ROOT / "sections" / "01_introduction.tex"), cmap)
    related = extract_body(read_tex(ROOT / "sections" / "02_related_work.tex"), cmap)
    m1 = extract_body(read_tex(ROOT / "sections" / "method" / "01_overall_framework.tex"), cmap)
    m2 = extract_body(read_tex(ROOT / "sections" / "method" / "02_visual_hull_init.tex"), cmap)
    m3tex = read_tex(ROOT / "sections" / "method" / "03_depth_guided_densification.tex")
    m3tex = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", "\n\n<<<FIG2>>>\n\n", m3tex, flags=re.S)
    m3a, m3b = m3tex.split("<<<FIG2>>>")
    m3_before = extract_body(m3a, cmap)
    m3_after = extract_body(m3b, cmap, keep_subsections=False)
    m4 = extract_body(read_tex(ROOT / "sections" / "method" / "04_dynamic_visibility_reg.tex"), cmap)
    e1 = extract_body(read_tex(ROOT / "sections" / "experiments" / "01_experimental_setup.tex"), cmap)
    e2 = drop_md_headings(extract_body(read_tex(ROOT / "sections" / "experiments" / "02_quantitative_and_qualitative.tex"), cmap, keep_subsections=False))
    e3 = drop_md_headings(extract_body(read_tex(ROOT / "sections" / "experiments" / "05_ablation_study.tex"), cmap, keep_subsections=False))
    conc = extract_body(read_tex(ROOT / "sections" / "05_conclusion.tex"), cmap)

    fw, vg, qf = FIG / "framework.png", FIG / "vggt_depth.png", FIG / "qualitative.png"
    lines = []
    a = lines.append
    a("% SynGS manuscript for SPIE A4 Word export")
    a("")
    a("# ABSTRACT")
    a("")
    a(abs_text)
    a("")
    a(f"**Keywords:** {kw}")
    a("")
    # No manual section numbers — Heading 1 style auto-numbers
    a("# INTRODUCTION")
    a("")
    a(intro)
    a("")
    a("# RELATED WORK")
    a("")
    a(related)
    a("")
    a("# METHOD")
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
    a("# EXPERIMENTS")
    a("")
    a(e1)
    a("")
    a("## Quantitative and Qualitative Results")
    a("")
    a("Table 1. Performance comparisons of sparse-view synthesis on Mip-NeRF 360 (4/6/9 views). LPIPS* denotes LPIPS × 10².")
    a("")
    a(MARKER_T1)
    a("")
    a("Table 2. Performance comparisons of sparse-view synthesis on LLFF (4/6/9 views). LPIPS* denotes LPIPS × 10².")
    a("")
    a(MARKER_T2)
    a("")
    a(e2)
    a("")
    a(f"![Figure 3. Qualitative comparison under the 4-view sparse-input setting on Mip-NeRF 360. SynGS produces fewer floating artifacts and more complete structural boundaries than the compared methods.]({qf})")
    a("")
    a("## Ablation Study")
    a("")
    # Keep lead-in sentence before Table 3
    lead, _, rest = e3.partition("Table 3")
    a(lead.strip())
    a("")
    a("Table 3. Ablation study of SynGS components. LPIPS* denotes LPIPS × 10².")
    a("")
    a(MARKER_T3)
    a("")
    # remaining ablation discussion after table (if any), skip duplicated caption fragments
    if rest:
        rest = re.sub(r"^[^.\n]*\.\s*", "", rest, count=1).strip()
        if rest:
            a(rest)
            a("")
    a("*Visibility Balancing denotes Dynamic Visibility Regularization (DVR).")
    a("")
    a("# CONCLUSION")
    a("")
    a(conc)
    a("")
    # Not Heading 1 — polished to SPIEreferences; body uses SPIE reference listing auto [n]
    a("References")
    a("")
    for r in refs:
        a(r)
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


def set_cell_text(cell, text, bold=False, size=8, align="center"):
    cell.text = ""
    p = cell.paragraphs[0]
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "left":
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(str(text))
    set_run_font(run, "Times New Roman", size=size, bold=bold)


def merge_row_cells(table, row, c1, c2):
    table.cell(row, c1).merge(table.cell(row, c2))


def set_table_borders(table) -> None:
    """Match ProcSPIETemplate_A4 table borders (single, sz=4, centered)."""
    tbl = table._tbl
    if is_eq_number_table(tbl):
        return
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)
    for child in list(tblPr):
        if child.tag in (qn("w:tblBorders"), qn("w:jc")):
            tblPr.remove(child)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        elem = OxmlElement(f"w:{edge}")
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), "4")
        elem.set(qn("w:space"), "0")
        elem.set(qn("w:color"), "auto")
        borders.append(elem)
    tblPr.append(borders)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    tblPr.append(jc)


MATH_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
CONTENT_TWIPS = 9718  # A4 minus 1.93 cm left/right
EQ_NUM_TWIPS = 850
H1_NUM_ID = "3"  # template Heading 1 multilevel list
METHOD_H2 = {
    "Overall Framework",
    "Visual Hull Initialization",
    "VGGT-Guided Densification",
    "Dynamic Visibility Regularization",
}


def clear_line_spacing_override(p) -> None:
    """Match template: no paragraph-level line spacing; rely on SPIE styles (single + after=120)."""
    pPr = p._p.pPr
    if pPr is None:
        return
    spacing = pPr.find(qn("w:spacing"))
    if spacing is None:
        return
    for attr in (qn("w:line"), qn("w:lineRule")):
        if attr in spacing.attrib:
            del spacing.attrib[attr]
    if len(spacing.attrib) == 0:
        pPr.remove(spacing)


def set_num_pr(p, ilvl: str, num_id: str) -> None:
    pPr = p._p.get_or_add_pPr()
    old = pPr.find(qn("w:numPr"))
    if old is not None:
        pPr.remove(old)
    num_pr = OxmlElement("w:numPr")
    ilvl_el = OxmlElement("w:ilvl")
    ilvl_el.set(qn("w:val"), ilvl)
    nid_el = OxmlElement("w:numId")
    nid_el.set(qn("w:val"), num_id)
    num_pr.append(ilvl_el)
    num_pr.append(nid_el)
    pPr.append(num_pr)


def _twip_attr(tag: str, twips: int, typ: str = "dxa"):
    el = OxmlElement(tag)
    el.set(qn("w:w"), str(twips))
    el.set(qn("w:type"), typ)
    return el


def is_eq_number_table(tbl) -> bool:
    rows = tbl.findall(qn("w:tr"))
    if len(rows) != 1:
        return False
    cells = rows[0].findall(qn("w:tc"))
    if len(cells) != 2:
        return False
    texts = ["".join(t.text or "" for t in c.findall(f".//{qn('w:t')}")) for c in cells]
    return bool(re.fullmatch(r"\(\d+\)", texts[1].strip()))


def number_display_equations(doc: Document) -> int:
    """Put display OMML in a borderless 2-col table: equation | (n) at right."""
    n = 0
    for p in list(doc.paragraphs):
        om_para = p._p.find(f".//{MATH_NS}oMathPara")
        if om_para is None:
            continue
        om = om_para.find(f"{MATH_NS}oMath")
        if om is None:
            continue
        n += 1
        tbl = OxmlElement("w:tbl")
        tbl_pr = OxmlElement("w:tblPr")
        tbl_pr.append(_twip_attr("w:tblW", CONTENT_TWIPS))
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "center")
        tbl_pr.append(jc)
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            elem = OxmlElement(f"w:{edge}")
            elem.set(qn("w:val"), "nil")
            borders.append(elem)
        tbl_pr.append(borders)
        tbl.append(tbl_pr)
        grid = OxmlElement("w:tblGrid")
        for w in (CONTENT_TWIPS - EQ_NUM_TWIPS, EQ_NUM_TWIPS):
            gc = OxmlElement("w:gridCol")
            gc.set(qn("w:w"), str(w))
            grid.append(gc)
        tbl.append(grid)

        tr = OxmlElement("w:tr")

        tc_eq = OxmlElement("w:tc")
        tc_eq_pr = OxmlElement("w:tcPr")
        tc_eq_pr.append(_twip_attr("w:tcW", CONTENT_TWIPS - EQ_NUM_TWIPS))
        tc_eq.append(tc_eq_pr)
        p_eq = OxmlElement("w:p")
        p_eq_pr = OxmlElement("w:pPr")
        p_style = OxmlElement("w:pStyle")
        p_style.set(qn("w:val"), "SPIEbodytext")
        p_eq_pr.append(p_style)
        jc_eq = OxmlElement("w:jc")
        jc_eq.set(qn("w:val"), "center")
        p_eq_pr.append(jc_eq)
        p_eq.append(p_eq_pr)
        p_eq.append(om)
        tc_eq.append(p_eq)
        tr.append(tc_eq)

        tc_n = OxmlElement("w:tc")
        tc_n_pr = OxmlElement("w:tcPr")
        tc_n_pr.append(_twip_attr("w:tcW", EQ_NUM_TWIPS))
        v_align = OxmlElement("w:vAlign")
        v_align.set(qn("w:val"), "center")
        tc_n_pr.append(v_align)
        tc_n.append(tc_n_pr)
        p_n = OxmlElement("w:p")
        p_n_pr = OxmlElement("w:pPr")
        p_n_style = OxmlElement("w:pStyle")
        p_n_style.set(qn("w:val"), "SPIEbodytext")
        p_n_pr.append(p_n_style)
        jc_n = OxmlElement("w:jc")
        jc_n.set(qn("w:val"), "right")
        p_n_pr.append(jc_n)
        p_n.append(p_n_pr)
        r_n = OxmlElement("w:r")
        r_pr = OxmlElement("w:rPr")
        r_fonts = OxmlElement("w:rFonts")
        r_fonts.set(qn("w:ascii"), "Times New Roman")
        r_fonts.set(qn("w:hAnsi"), "Times New Roman")
        r_fonts.set(qn("w:eastAsia"), "Times New Roman")
        r_pr.append(r_fonts)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "20")
        r_pr.append(sz)
        r_n.append(r_pr)
        t_n = OxmlElement("w:t")
        t_n.text = f"({n})"
        r_n.append(t_n)
        p_n.append(r_n)
        tc_n.append(p_n)
        tr.append(tc_n)
        tbl.append(tr)

        p._p.addprevious(tbl)
        parent = p._p.getparent()
        parent.remove(p._p)
    return n


def build_mip360_table(doc: Document):
    # 9 cols: Methods + 3*3 metrics; plus side group col => 10? PDF: empty | Methods | 3 groups
    # Use 11 cols: group, method, 9 metrics — merge header groups
    rows = [
        ("NeRF-based", "RegNeRF", "19.88", "12.59", "0.841", "20.72", "13.41", "0.847", "19.70", "13.68", "0.852"),
        ("", "SparseNeRF", "17.76", "12.83", "0.845", "19.74", "13.42", "0.861", "21.56", "14.36", "0.873"),
        ("3DGS-based", "3DGS", "10.80", "20.31", "0.899", "8.38", "22.12", "0.913", "6.42", "24.29", "0.930"),
        ("", "CoR-GS", "11.76", "20.45", "0.856", "9.28", "22.57", "0.901", "7.04", "24.73", "0.926"),
        ("", "DropGaussian", "11.57", "21.76", "0.837", "8.61", "22.98", "0.895", "8.02", "24.10", "0.915"),
        ("", "D²GS", "2.58", "22.35", "0.923", "2.34", "24.74", "0.937", "2.11", "27.13", "0.941"),
        ("", "SynGS (Ours)", "3.89", "25.91", "0.948", "3.43", "27.93", "0.953", "3.02", "29.21", "0.961"),
    ]
    t = doc.add_table(rows=2 + len(rows), cols=11)
    try:
        t.style = "Normal Table"
    except KeyError:
        pass
    set_cell_text(t.cell(0, 0), "", size=8)
    set_cell_text(t.cell(0, 1), "Methods", bold=True, size=8)
    set_cell_text(t.cell(0, 2), "Mip-NeRF 360 (4-view)", bold=True, size=8)
    set_cell_text(t.cell(0, 5), "Mip-NeRF 360 (6-view)", bold=True, size=8)
    set_cell_text(t.cell(0, 8), "Mip-NeRF 360 (9-view)", bold=True, size=8)
    merge_row_cells(t, 0, 2, 4)
    merge_row_cells(t, 0, 5, 7)
    merge_row_cells(t, 0, 8, 10)
    metrics = ["LPIPS*↓", "PSNR↑", "SSIM↑"] * 3
    set_cell_text(t.cell(1, 0), "", size=7)
    set_cell_text(t.cell(1, 1), "", size=7)
    for i, m in enumerate(metrics):
        set_cell_text(t.cell(1, 2 + i), m, bold=True, size=7)
    for ri, row in enumerate(rows):
        r = 2 + ri
        for ci, val in enumerate(row):
            set_cell_text(t.cell(r, ci), val, bold=(val == "SynGS (Ours)"), size=8, align="center" if ci >= 2 else "left")
    # merge group labels
    t.cell(2, 0).merge(t.cell(3, 0))
    set_cell_text(t.cell(2, 0), "NeRF-based", bold=True, size=7)
    t.cell(4, 0).merge(t.cell(8, 0))
    set_cell_text(t.cell(4, 0), "3DGS-based", bold=True, size=7)
    set_table_borders(t)
    return t


def build_llff_table(doc: Document):
    rows = [
        ("NeRF-based", "RegNeRF", "29.65", "18.55", "0.587", "22.61", "19.08", "0.760", "18.39", "22.86", "0.820"),
        ("", "FreeNeRF", "30.85", "19.09", "0.624", "23.06", "19.81", "0.763", "17.94", "23.08", "0.823"),
        ("3DGS-based", "3DGS", "22.93", "19.32", "0.649", "13.45", "23.80", "0.814", "9.68", "25.44", "0.860"),
        ("", "CoR-GS", "19.66", "20.45", "0.696", "12.53", "23.87", "0.840", "8.94", "26.70", "0.874"),
        ("", "DropGaussian", "21.93", "19.80", "0.621", "13.79", "23.41", "0.803", "9.40", "25.87", "0.868"),
        ("", "D²GS", "17.98", "22.35", "0.746", "13.85", "23.91", "0.846", "8.91", "26.80", "0.871"),
        ("", "SynGS (Ours)", "16.92", "23.92", "0.762", "12.54", "25.17", "0.848", "8.96", "26.71", "0.871"),
    ]
    t = doc.add_table(rows=2 + len(rows), cols=11)
    try:
        t.style = "Normal Table"
    except KeyError:
        pass
    set_cell_text(t.cell(0, 0), "", size=8)
    set_cell_text(t.cell(0, 1), "Methods", bold=True, size=8)
    set_cell_text(t.cell(0, 2), "LLFF (4-view)", bold=True, size=8)
    set_cell_text(t.cell(0, 5), "LLFF (6-view)", bold=True, size=8)
    set_cell_text(t.cell(0, 8), "LLFF (9-view)", bold=True, size=8)
    merge_row_cells(t, 0, 2, 4)
    merge_row_cells(t, 0, 5, 7)
    merge_row_cells(t, 0, 8, 10)
    metrics = ["LPIPS*↓", "PSNR↑", "SSIM↑"] * 3
    set_cell_text(t.cell(1, 0), "", size=7)
    set_cell_text(t.cell(1, 1), "", size=7)
    for i, m in enumerate(metrics):
        set_cell_text(t.cell(1, 2 + i), m, bold=True, size=7)
    for ri, row in enumerate(rows):
        r = 2 + ri
        for ci, val in enumerate(row):
            set_cell_text(t.cell(r, ci), val, bold=(val == "SynGS (Ours)"), size=8, align="center" if ci >= 2 else "left")
    t.cell(2, 0).merge(t.cell(3, 0))
    set_cell_text(t.cell(2, 0), "NeRF-based", bold=True, size=7)
    t.cell(4, 0).merge(t.cell(8, 0))
    set_cell_text(t.cell(4, 0), "3DGS-based", bold=True, size=7)
    set_table_borders(t)
    return t


def build_ablation_table(doc: Document):
    t = doc.add_table(rows=4, cols=6)
    try:
        t.style = "Normal Table"
    except KeyError:
        pass
    headers = [
        "Visual Hull Init",
        "Depth Densification",
        "Visibility Balancing*",
        "SSIM↑",
        "PSNR↑",
        "LPIPS*↓",
    ]
    for i, h in enumerate(headers):
        set_cell_text(t.cell(0, i), h, bold=True, size=8)
    data = [
        ("√", "", "", "0.865", "17.51", "12.80"),
        ("√", "√", "", "0.902", "24.96", "5.20"),
        ("√", "√", "√", "0.943", "26.18", "3.98"),
    ]
    for ri, row in enumerate(data):
        for ci, val in enumerate(row):
            set_cell_text(t.cell(1 + ri, ci), val, bold=(ri == 2 and ci >= 3), size=8)
    set_table_borders(t)
    return t


def replace_marker_with_table(doc: Document, marker: str, builder):
    for p in list(doc.paragraphs):
        if p.text.strip() == marker:
            tbl = builder(doc)
            p._p.addnext(tbl._tbl)
            parent = p._p.getparent()
            parent.remove(p._p)
            return True
    print("WARN: marker not found", marker)
    return False


def reorder_experiments_block(doc: Document) -> None:
    """Ensure order: Table1 caption+table, e2 text, Table2 caption+table, Fig3, Ablation..."""
    # Current md order may put both e2 text before Table2. Acceptable if Table1 is before e2.
    # Move Table 2 caption+table to after first results paragraph if needed — skip if already OK.
    pass


def polish(docx_path: Path) -> None:
    doc = Document(str(docx_path))
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(4.94)
        sec.left_margin = Cm(1.93)
        sec.right_margin = Cm(1.93)

    body = doc.element.body
    intro_p = None
    for p in doc.paragraphs:
        if p.text.strip() in ("INTRODUCTION", "1. INTRODUCTION") or p.text.strip().endswith("INTRODUCTION"):
            if "INTRODUCTION" in p.text.strip() and "Sparse" not in p.text:
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

    def add_parts(parts, style, align=None, size=None):
        """parts: list of (text, superscript_bool)."""
        p = doc.add_paragraph(style=style_or(doc, style))
        if align is not None:
            p.alignment = align
        for text, sup in parts:
            run = p.add_run(text)
            set_run_font(run, "Times New Roman", size=size)
            run.font.superscript = bool(sup)
        return p

    add(
        "SynGS: synergizing explicit geometry and transformer depth priors for sparse-view 3D Gaussian Splatting",
        "SPIE paper title",
        WD_ALIGN_PARAGRAPH.CENTER,
        16,
        True,
    )
    # Template: name* + superscript affil letter
    add_parts(
        [
            ("Junjie Geng*", False),
            ("a", True),
            (", Ao Zhang", False),
            ("a", True),
            (", and Lian Duan", False),
            ("a", True),
        ],
        "SPIE Authors-Affils",
        WD_ALIGN_PARAGRAPH.CENTER,
        12,
    )
    add_parts(
        [
            ("a", True),
            (
                "Communication University of China, State Key Laboratory of Media Convergence and Communication, "
                "Intelligent Network and Media Research Center, No. 1 Dingfuzhuang East Street, Chaoyang District, "
                "Beijing 100024, China",
                False,
            ),
        ],
        "SPIE Authors-Affils",
        WD_ALIGN_PARAGRAPH.CENTER,
        10,
    )
    add("*gjj@cuc.edu.cn", "SPIE body text", WD_ALIGN_PARAGRAPH.CENTER, 10)

    abs_md = MD.read_text(encoding="utf-8")
    abs_body = abs_md.split("# ABSTRACT")[1].split("# INTRODUCTION")[0].strip()
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
    add("Abstract", "SPIE abstract title", WD_ALIGN_PARAGRAPH.CENTER, 11, True)
    for para in paras:
        p = add(para, "SPIE abstract body text", size=10)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if kw_line:
        add(kw_line, "SPIE keywords", size=10)

    body = doc.element.body
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

    # Replace table markers before style pass
    replace_marker_with_table(doc, MARKER_T1, build_mip360_table)
    replace_marker_with_table(doc, MARKER_T2, build_llff_table)
    replace_marker_with_table(doc, MARKER_T3, build_ablation_table)

    h1_names = {"INTRODUCTION", "RELATED WORK", "METHOD", "EXPERIMENTS", "CONCLUSION"}
    h2_names = {
        "Overall Framework",
        "Visual Hull Initialization",
        "VGGT-Guided Densification",
        "Dynamic Visibility Regularization",
        "Experimental Setup and Datasets",
        "Quantitative and Qualitative Results",
        "Ablation Study",
    }

    in_refs = False
    for p in doc.paragraphs:
        clear_line_spacing_override(p)
        t = p.text.strip()
        st = p.style.name if p.style else ""

        # Strip accidental manual numbering
        t_norm = re.sub(r"^\d+\.\s+", "", t)

        if t_norm in ("REFERENCES", "References") or t == "References":
            p.style = style_or(doc, "SPIEreferences")
            if p.runs:
                p.runs[0].text = "References"
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.add_run("References")
            for r in p.runs:
                set_run_font(r, "Times New Roman", 11, True)
            in_refs = True
            continue

        if in_refs:
            # reference body lines — no manual [n]
            if t and not t.startswith("Table ") and not t.startswith("Figure "):
                p.style = style_or(doc, "SPIE reference listing")
            for run in p.runs:
                set_run_font(run, "Times New Roman", 9)
            continue

        if t_norm in h1_names:
            if t != t_norm and p.runs:
                p.runs[0].text = t_norm
                for r in p.runs[1:]:
                    r.text = ""
            p.style = style_or(doc, "Heading 1")
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=11, bold=True)
            continue
        if t_norm in h2_names or st.startswith("Heading 2"):
            p.style = style_or(doc, "Heading 2")
            if t_norm in METHOD_H2:
                set_num_pr(p, "1", H1_NUM_ID)
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=10, bold=True)
            continue
        if t.startswith("Figure ") and len(t) > 7 and t[7].isdigit():
            p.style = style_or(doc, "SPIE figure caption")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=9)
            continue
        if t.startswith("Table ") and len(t) > 6 and t[6].isdigit():
            p.style = style_or(doc, "SPIE table caption")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=9)
            continue
        if t in ("ABSTRACT", "Abstract"):
            p.style = style_or(doc, "SPIE abstract title")
            if p.runs:
                p.runs[0].text = "Abstract"
                for r in p.runs[1:]:
                    r.text = ""
            for run in p.runs:
                set_run_font(run, "Times New Roman", 11, True)
            continue
        if t.startswith("Keywords:"):
            p.style = style_or(doc, "SPIE keywords")
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=10)
            continue
        if st not in (
            "Heading 1",
            "Heading 2",
            "SPIE figure caption",
            "SPIE table caption",
            "SPIE keywords",
            "SPIE paper title",
            "SPIE Authors-Affils",
            "SPIE abstract title",
            "SPIE abstract body text",
            "SPIEreferences",
            "SPIE reference listing",
        ):
            p.style = style_or(doc, "SPIE body text")

        st = p.style.name if p.style else ""
        if st in ("SPIE body text", "SPIE abstract body text"):
            if not (t.startswith("*") and "@" in t):
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for run in p.runs:
                set_run_font(run, "Times New Roman", size=10)
        else:
            for run in p.runs:
                set_run_font(run, "Times New Roman")

    for p in doc.paragraphs:
        if p._p.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing") is not None:
            if not p.text.strip():
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for shape in doc.inline_shapes:
        try:
            shape.width = Cm(16.5)
        except Exception:
            pass

    n_eq = number_display_equations(doc)
    print(f"numbered display equations: {n_eq}")

    for tbl in doc.tables:
        set_table_borders(tbl)

    superscript_citations(doc)
    doc.save(str(docx_path))


def superscript_citations(doc: Document) -> None:
    in_refs = False
    for p in doc.paragraphs:
        t = p.text.strip()
        if t in ("REFERENCES", "References"):
            in_refs = True
            continue
        if in_refs:
            continue
        if p.style and p.style.name == "SPIE reference listing":
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

    h1 = [p.text.strip() for p in doc.paragraphs if p.style and p.style.name == "Heading 1"]
    h2 = [p for p in doc.paragraphs if p.style and p.style.name == "Heading 2"]
    ref_paras = [p for p in doc.paragraphs if p.style and p.style.name == "SPIE reference listing"]
    manual_ref = sum(1 for p in ref_paras if re.match(r"^\[\d+\]\s", p.text.strip()))
    manual_h1 = sum(1 for t in h1 if re.match(r"^\d+\.\s+", t))

    def _num_id(p):
        pPr = p._p.pPr
        if pPr is None or pPr.numPr is None or pPr.numPr.numId is None:
            return None
        return str(pPr.numPr.numId.val)

    method_h2 = [p for p in h2 if p.text.strip() in METHOD_H2]
    other_h2 = [p for p in h2 if p.text.strip() not in METHOD_H2]
    fig_caps = [p for p in doc.paragraphs if p.style and p.style.name == "SPIE figure caption"]
    body_sz = []
    for p in doc.paragraphs:
        if p.style and p.style.name == "SPIE body text" and p.text.strip() and not p.text.strip().startswith("*"):
            for r in p.runs:
                if r.font.size is not None:
                    body_sz.append(r.font.size.pt)
            if body_sz:
                break
    eq_n = sum(1 for t in doc.tables if is_eq_number_table(t._tbl))
    ref_blob = "\n".join(p.text for p in ref_paras)

    checks = {
        "title": "SynGS: synergizing explicit geometry" in texts,
        "corr_email": "gjj@cuc.edu.cn" in texts,
        "keywords": "Keywords:" in texts and "Vision Transformer" in texts,
        # Template stores "Abstract"; style PrincipalHding applies w:caps so Word shows ABSTRACT
        "abstract_title": re.search(r"(?m)^Abstract\s*$", texts) is not None,
        "affil_superscript": any(
            r.font.superscript and r.text == "a"
            for p in doc.paragraphs
            if p.style and p.style.name == "SPIE Authors-Affils"
            for r in p.runs
        ),
        "fig_captions": all(x in texts for x in ("Figure 1.", "Figure 2.", "Figure 3.")),
        "fig_caption_justify": all(p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY for p in fig_caps) and len(fig_caps) >= 3,
        "table_captions": all(x in texts for x in ("Table 1.", "Table 2.", "Table 3.")),
        "syn_gs_ours_in_table": "SynGS (Ours)" in table_text,
        "merged_header_mip": "Mip-NeRF 360 (4-view)" in table_text,
        "merged_header_llff": "LLFF (4-view)" in table_text,
        "refs_doi": "DOI:" in texts,
        "ref_style_count": len(ref_paras) >= 40,
        "no_manual_ref_prefix": manual_ref == 0,
        "no_latex_refs": not re.search(r'``|\\"|Leimk"u|Sch"o|Proc\.\\', ref_blob),
        "no_manual_h1_number": manual_h1 == 0,
        "h1_has_introduction": any(t == "INTRODUCTION" for t in h1),
        "method_h2_numbered": bool(method_h2) and all(_num_id(p) == H1_NUM_ID for p in method_h2),
        "other_h2_unnumbered": all(_num_id(p) != H1_NUM_ID for p in other_h2),
        "body_10pt": body_sz and all(abs(s - 10) < 0.1 for s in body_sz),
        "no_chinese": not re.search(r"[\u4e00-\u9fff]", all_text),
        "editable_tables": len(doc.tables) >= 3,
        "images": len(doc.inline_shapes) >= 3,
        "editable_eq_omml": b"oMath" in xml,
        "intro_present": "Sparse inputs provide limited information" in texts,
        "cite_superscript": b"superscript" in xml,
        "table_borders": all(
            t._tbl.tblPr is not None and t._tbl.tblPr.find(qn("w:tblBorders")) is not None for t in doc.tables
        ),
        "eq_numbers": eq_n >= 4,
    }
    print("VERIFY:")
    ok = True
    for k, v in checks.items():
        print(f"  {k}: {'OK' if v else 'FAIL'}")
        ok = ok and bool(v)
    print("  Heading1 texts:", h1)
    print(f"  tables={len(doc.tables)} ref_paras={len(ref_paras)}")
    if not ok:
        raise SystemExit(1)


def main():
    WORKDIR.mkdir(exist_ok=True)
    OUT_COPY.parent.mkdir(exist_ok=True)
    cmap = load_cite_map()
    refs = load_refs()
    print(f"cites={len(cmap)} refs={len(refs)}")
    md = build_markdown(cmap, refs)
    MD.write_text(md, encoding="utf-8")
    print("wrote", MD, "chars", len(md))
    if "r_ is the maximum" in md or "(d)= d+" in md:
        raise SystemExit("math stripping still broken")
    if "# 1. INTRODUCTION" in md or re.search(r"^\[1\] ", md, re.M):
        raise SystemExit("manual numbering still present in markdown")
    tmp = WORKDIR / "pandoc_out.docx"
    run_pandoc(MD, tmp)
    shutil.copy2(tmp, OUT)
    polish(OUT)
    verify(OUT)
    shutil.copy2(OUT, OUT_COPY)
    print("DONE", OUT)
    print("COPY", OUT_COPY)


if __name__ == "__main__":
    main()
