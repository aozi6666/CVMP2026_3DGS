from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = section.page_height, section.page_width
section.left_margin = section.right_margin = Cm(1.5)

C_SALMON = 'FCB6A5'  # \cellcolor{color_blue} RGB(252,182,165)
C_LBLUE  = 'EBEBFF'  # \cellcolor{blue!8}  8%蓝+92%白

# ── 边框工具 ──────────────────────────────────────────
def _get_tcBorders(tc_el):
    tcPr = tc_el.find(qn('w:tcPr'))
    if tcPr is None:
        tcPr = OxmlElement('w:tcPr')
        tc_el.insert(0, tcPr)
    tcB = tcPr.find(qn('w:tcBorders'))
    if tcB is None:
        tcB = OxmlElement('w:tcBorders')
        tcPr.append(tcB)
    return tcB

def border_on(tc_el, side, sz, color='000000'):
    tcB = _get_tcBorders(tc_el)
    for old in tcB.findall(qn(f'w:{side}')):
        tcB.remove(old)
    el = OxmlElement(f'w:{side}')
    el.set(qn('w:val'), 'single')
    el.set(qn('w:sz'), str(sz))
    el.set(qn('w:color'), color)
    el.set(qn('w:space'), '0')
    tcB.append(el)

def border_off(tc_el, side):
    tcB = _get_tcBorders(tc_el)
    for old in tcB.findall(qn(f'w:{side}')):
        tcB.remove(old)
    el = OxmlElement(f'w:{side}')
    el.set(qn('w:val'), 'none')
    el.set(qn('w:sz'), '0')
    el.set(qn('w:color'), 'auto')
    el.set(qn('w:space'), '0')
    tcB.append(el)

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.find(qn('w:tcPr'))
    if tcPr is None:
        tcPr = OxmlElement('w:tcPr')
        tc.insert(0, tcPr)
    for old in tcPr.findall(qn('w:shd')):
        tcPr.remove(old)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def cell_text(cell, text, bold=False):
    para = cell.paragraphs[0]
    para.clear()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.bold = bold

# ── 建表 ─────────────────────────────────────────────
# 列: col0=Methods, col1-3=4-view, col4-6=6-view, col7-9=9-view
NCOLS, NROWS = 10, 9
table = doc.add_table(rows=NROWS, cols=NCOLS)
table.style = 'Table Grid'

# 清除表级边框（保险）
tbl = table._tbl
tblPr = tbl.find(qn('w:tblPr'))
if tblPr is None:
    tblPr = OxmlElement('w:tblPr'); tbl.insert(0, tblPr)
tblBdr = tblPr.find(qn('w:tblBorders'))
if tblBdr is None:
    tblBdr = OxmlElement('w:tblBorders'); tblPr.append(tblBdr)
for side in ['top','left','bottom','right','insideH','insideV']:
    for old in tblBdr.findall(qn(f'w:{side}')): tblBdr.remove(old)
    el = OxmlElement(f'w:{side}')
    el.set(qn('w:val'),'none'); el.set(qn('w:sz'),'0'); el.set(qn('w:color'),'auto')
    tblBdr.append(el)

# ── 表头内容 ──────────────────────────────────────────
# Methods 跨两行
table.cell(0, 0).merge(table.cell(1, 0))
cell_text(table.cell(0, 0), 'Methods', bold=True)

# 三组表头
for start, label in [(1,'LLFF (4-view)'), (4,'LLFF (6-view)'), (7,'LLFF (9-view)')]:
    c = table.cell(0, start); c.merge(table.cell(0, start+2))
    cell_text(c, label, bold=True)

metrics = ['LPIPS*↓', 'PSNR↑', 'SSIM↑']
for i, m in enumerate(metrics):
    cell_text(table.cell(1, 1+i), m, bold=True)
    cell_text(table.cell(1, 4+i), m, bold=True)
    cell_text(table.cell(1, 7+i), m, bold=True)

# ── 数据内容 ──────────────────────────────────────────
rows_data = [
    ('RegNeRF',      '29.65','18.55','0.587', '22.61','19.08','0.760', '18.39','22.86','0.820'),
    ('FreeNeRF',     '30.85','19.09','0.624', '23.06','19.81','0.763', '17.94','23.08','0.823'),
    ('3DGS',         '22.93','19.32','0.649', '13.45','23.80','0.814',  '9.68','25.44','0.860'),
    ('CoR-GS',       '19.66','20.45','0.696', '12.53','23.87','0.840',  '8.94','26.70','0.874'),
    ('DropGaussian', '21.93','19.80','0.621', '13.79','23.41','0.803',  '9.40','25.87','0.868'),
    ('D²GS',         '17.98','22.35','0.746', '13.85','23.91','0.846',  '8.91','26.80','0.871'),
    ('Ours',         '16.92','23.92','0.762', '12.54','25.17','0.848',  '8.96','26.71','0.871'),
]

# 精确高亮（逐行对照 LaTeX）
# r_idx: 0=RegNeRF .. 6=Ours; col: 1-9
highlights = {
    # CoR-GS (r=3): \cellcolor{color_blue} 6v-LPIPS(col4), 9v-LPIPS(col7), 9v-SSIM(col9)
    (3,4):C_SALMON, (3,7):C_SALMON, (3,9):C_SALMON,
    # D²GS (r=5): blue!8 → 4v全(1,2,3), 6v-PSNR(5), 6v-SSIM(6), 9v-SSIM(9)
    #             color_blue → 9v-PSNR(8)
    (5,1):C_LBLUE, (5,2):C_LBLUE, (5,3):C_LBLUE,
    (5,5):C_LBLUE, (5,6):C_LBLUE,
    (5,8):C_SALMON, (5,9):C_LBLUE,
    # Ours (r=6): color_blue → 4v全(1,2,3), 6v-PSNR(5), 6v-SSIM(6)
    #             blue!8 → 6v-LPIPS(4), 9v全(7,8,9)
    (6,1):C_SALMON,(6,2):C_SALMON,(6,3):C_SALMON,
    (6,4):C_LBLUE, (6,5):C_SALMON,(6,6):C_SALMON,
    (6,7):C_LBLUE, (6,8):C_LBLUE, (6,9):C_LBLUE,
}

for r_idx, row_data in enumerate(rows_data):
    tr = r_idx + 2
    is_ours = (row_data[0] == 'Ours')
    cell_text(table.cell(tr, 0), row_data[0], bold=is_ours)
    for ci, val in enumerate(row_data[1:]):
        col = ci + 1
        cell = table.cell(tr, col)
        cell_text(cell, val, bold=is_ours)
        if (r_idx, col) in highlights:
            set_cell_bg(cell, highlights[(r_idx, col)])

# ── 列宽 ──────────────────────────────────────────────
col_widths = [Cm(2.8)] + [Cm(1.9)] * 9
for row in table.rows:
    for i, cell in enumerate(row.cells):
        if i < len(col_widths):
            cell.width = col_widths[i]

# ── 边框（精确按LaTeX tabular格式）─────────────────────
# LaTeX: {c c | ccc | ccc | ccc}  →  竖线在 col0右 / col3右 / col6右
# \toprule 三处: 表顶 / 表头后 / 表底  （行间无线）
#
# sz=18 约对应 booktabs \toprule 粗线
# sz=6  对应普通 | 竖线
THICK = 18
VTHIN = 6
RIGHT_AFTER = {0, 3, 6}  # 这些列的右侧画竖线

for row_idx, tr_el in enumerate(table._tbl.findall(qn('w:tr'))):
    col_idx = 0
    for tc_el in tr_el.findall(qn('w:tc')):
        # 计算 gridSpan
        tcPr_el = tc_el.find(qn('w:tcPr'))
        grid_span = 1
        if tcPr_el is not None:
            gs = tcPr_el.find(qn('w:gridSpan'))
            if gs is not None:
                grid_span = int(gs.get(qn('w:val'), '1'))
        last_col = col_idx + grid_span - 1

        # 上边框
        if row_idx == 0:
            border_on(tc_el, 'top', THICK)
        else:
            border_off(tc_el, 'top')

        # 下边框
        if row_idx == 1 or row_idx == NROWS - 1:
            border_on(tc_el, 'bottom', THICK)
        else:
            border_off(tc_el, 'bottom')

        # 左边框（LaTeX 无左外边框）
        border_off(tc_el, 'left')

        # 右边框
        if last_col in RIGHT_AFTER:
            border_on(tc_el, 'right', VTHIN)
        else:
            border_off(tc_el, 'right')

        col_idx += grid_span

# ── 保存 ──────────────────────────────────────────────
output = '/Users/zhangao/Desktop/中国传媒大学/论文/（Best）journal of electronic imaging/latex/FFLL数据集/table.docx'
doc.save(output)
print(f'成功保存: {output}')
