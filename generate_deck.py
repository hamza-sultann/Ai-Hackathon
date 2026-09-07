import os
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

os.makedirs('charts', exist_ok=True)

# -------------------------------------------------------------
# Color Palette Constants (Istikshaf Grid Noir)
# -------------------------------------------------------------
C_BG_HEX = '#11150A'
C_CARD_HEX = '#181D11'
C_CARD_ALT_HEX = '#1F2516'
C_LIME_HEX = '#B6F542'
C_CYAN_HEX = '#45DCEB'
C_CORAL_HEX = '#FFB4AB'
C_ORANGE_HEX = '#FFA726'
C_TEXT_HEX = '#E1E4D2'
C_MUTED_HEX = '#A0A891'
C_BORDER_HEX = '#2E3523'

C_BG = RGBColor(17, 21, 10)
C_CARD = RGBColor(24, 29, 17)
C_CARD_ALT = RGBColor(31, 37, 22)
C_LIME = RGBColor(182, 245, 66)
C_CYAN = RGBColor(69, 220, 235)
C_CORAL = RGBColor(255, 180, 171)
C_ORANGE = RGBColor(255, 167, 38)
C_TEXT = RGBColor(225, 228, 210)
C_WHITE = RGBColor(255, 255, 255)
C_MUTED = RGBColor(160, 168, 145)
C_BORDER = RGBColor(46, 53, 35)

FONT_HEADING = 'Trebuchet MS'
FONT_BODY = 'Segoe UI'
FONT_MONO = 'Consolas'

# -------------------------------------------------------------
# 1. Regenerate High-Res Clean Charts (ZERO Overlaps / Collisions)
# -------------------------------------------------------------
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = C_TEXT_HEX
plt.rcParams['axes.labelcolor'] = C_TEXT_HEX
plt.rcParams['xtick.color'] = C_MUTED_HEX
plt.rcParams['ytick.color'] = C_MUTED_HEX

# Chart 1: DISCO Losses
fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

discos = ['IESCO\n(Islamabad)', 'FESCO\n(Faisalabad)', 'LESCO\n(Lahore)', 'MEPCO\n(Multan)', 'K-Electric\n(Karachi)', 'QESCO\n(Quetta)', 'HESCO\n(Hyderabad)', 'SEPCO\n(Sukkur)', 'PESCO\n(Peshawar)']
losses = [8.2, 9.4, 12.8, 15.1, 15.3, 26.5, 28.2, 35.8, 37.4]
colors = [C_LIME_HEX if x < 13 else C_CYAN_HEX if x < 20 else C_ORANGE_HEX if x < 30 else C_CORAL_HEX for x in losses]

y_pos = np.arange(len(discos))
bars = ax.barh(y_pos, losses, color=colors, height=0.62, edgecolor='#3A422E', linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(discos, fontsize=8)
ax.set_xlabel('Non-Technical Loss Rate (%)', fontsize=9, labelpad=8, color=C_MUTED_HEX)
ax.set_title('Pakistan DISCO Power Loss Landscape', fontsize=11.5, pad=12, fontweight='bold', color=C_TEXT_HEX)
ax.axvline(18.5, color=C_ORANGE_HEX, linestyle='--', linewidth=1.2, alpha=0.8, label='National Avg: 18.5%')

for bar, loss in zip(bars, losses):
    ax.text(loss + 0.6, bar.get_y() + bar.get_height()/2, f"{loss:.1f}%", va='center', ha='left', fontsize=8.5, color='#FFFFFF', fontweight='bold')

ax.set_xlim(0, 44)
ax.grid(axis='x', color='#262C1D', linestyle=':', alpha=0.6)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
for s in ['left', 'bottom']: ax.spines[s].set_color(C_BORDER_HEX)
ax.legend(loc='lower right', fontsize=8, framealpha=0.4, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)
plt.tight_layout()
fig.savefig('charts/disco_losses.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 2: 24-Hour Diurnal Load Profiles & Theft Signatures (CLEAN, ZERO OVERLAP)
fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

hours = np.arange(24)
baseline = np.array([0.15, 0.13, 0.12, 0.11, 0.14, 0.22, 0.45, 0.52, 0.40, 0.32, 0.29, 0.28, 0.28, 0.27, 0.29, 0.31, 0.36, 0.48, 0.85, 0.92, 0.88, 0.72, 0.45, 0.25])
solar = baseline.copy()
solar[10:16] = np.array([0.08, 0.04, 0.02, 0.03, 0.06, 0.12])
peak_shaver = baseline.copy()
peak_shaver[18:22] = np.array([0.02, 0.02, 0.03, 0.03])
night_ac = baseline.copy()
night_ac[0:6] = np.array([0.04, 0.03, 0.03, 0.03, 0.04, 0.05])

ax.plot(hours, baseline, color='#FFFFFF', linewidth=2.4, label='Normal Baseline Load')
ax.plot(hours, solar, color=C_CYAN_HEX, linewidth=2.2, linestyle='-.', label='Rooftop Solar Duck Curve')
ax.plot(hours, peak_shaver, color=C_CORAL_HEX, linewidth=2.4, label='Peak Shaver Theft (6-10 PM)')
ax.plot(hours, night_ac, color=C_ORANGE_HEX, linewidth=2.0, linestyle=':', label='Night AC Bypass (11 PM-5 AM)')
ax.axvspan(18, 22, color=C_CORAL_HEX, alpha=0.12, label='NEPRA Peak Window (2.5x Cost)')

ax.set_ylim(-0.05, 1.25)
ax.set_xlim(0, 23)
ax.set_xticks(np.arange(0, 24, 3))
ax.set_xticklabels(['12 AM', '3 AM', '6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM'], fontsize=8.5, color=C_MUTED_HEX)
ax.set_ylabel('Load Draw (kWh / Hour)', fontsize=9, color=C_MUTED_HEX, labelpad=6)
ax.set_xlabel('Time of Day (24-Hour Diurnal Stream)', fontsize=9, color=C_MUTED_HEX, labelpad=6)
ax.set_title('Hourly Diurnal Profiles: Legitimate vs. Tamper Signatures', fontsize=11, pad=12, fontweight='bold', color=C_TEXT_HEX)
ax.grid(color='#262C1D', linestyle=':', alpha=0.7)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
for s in ['left', 'bottom']: ax.spines[s].set_color(C_BORDER_HEX)

# Place legend in top-left empty space (y: 0.7 to 1.2, x: 0 to 6)
ax.legend(loc='upper left', fontsize=7.8, framealpha=0.6, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)
plt.tight_layout()
fig.savefig('charts/diurnal_theft_signatures.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 3: AMI Uplift Benchmarks (CLEAN, ZERO OVERLAP)
fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

archetypes = ['Peak Shaver', 'Fixed Shunt', 'Night AC', 'Direct Kunda', 'Overall']
monthly_recall = [10.6, 38.3, 20.8, 14.9, 20.3]
ami_recall = [58.3, 63.9, 39.6, 29.5, 45.7]

x = np.arange(len(archetypes))
width = 0.35

rects1 = ax.bar(x - width/2, monthly_recall, width, label='Track 1 (Monthly Billing)', color='#4E573F', edgecolor='#333B28', linewidth=0.8)
rects2 = ax.bar(x + width/2, ami_recall, width, label='Track 2 (Hourly Smart Meter)', color=C_LIME_HEX, edgecolor='#8CBF2A', linewidth=0.8)

ax.set_ylabel('Detection Recall Rate (%)', fontsize=9, color=C_MUTED_HEX, labelpad=6)
ax.set_title('Track 1 (Monthly) vs Track 2 (Smart Meter) Recall', fontsize=11, pad=14, fontweight='bold', color=C_TEXT_HEX)
ax.set_xticks(x)
ax.set_xticklabels(archetypes, fontsize=8.5, color=C_TEXT_HEX)
ax.set_ylim(0, 85)
ax.grid(axis='y', color='#262C1D', linestyle=':', alpha=0.7)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
for s in ['left', 'bottom']: ax.spines[s].set_color(C_BORDER_HEX)

# Place legend in upper right
ax.legend(loc='upper right', fontsize=8, framealpha=0.6, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)

for r1, r2 in zip(rects1, rects2):
    h1 = r1.get_height()
    h2 = r2.get_height()
    ax.annotate(f'{h1:.1f}%', xy=(r1.get_x() + r1.get_width()/2, h1), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=7.5, color=C_MUTED_HEX)
    ax.annotate(f'{h2:.1f}%', xy=(r2.get_x() + r2.get_width()/2, h2), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8, fontweight='bold', color=C_LIME_HEX)

# 5.5x Leap badge cleanly placed above Peak Shaver
ax.annotate('5.5x Leap\n(+47.8%)', xy=(0.18, 62), xytext=(0.18, 73),
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#1E2818', edgecolor=C_CYAN_HEX, lw=1),
            arrowprops=dict(arrowstyle='->', color=C_CYAN_HEX, lw=1.5),
            fontsize=7.5, fontweight='bold', color=C_CYAN_HEX)

plt.tight_layout()
fig.savefig('charts/ami_uplift_benchmarks.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 4: DISCO Revenue Recovery Waterfall
fig, ax = plt.subplots(figsize=(6.8, 4.6), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

categories = ['Current\nAnnual Loss', 'Targeted\nDetected Theft', 'Direct Power\nRecovery', 'Reduced Raid\nWaste', 'Net Annual\nRecovery']
values = [-18.5, 15.6, 12.4, 1.8, 14.2]
colors = [C_CORAL_HEX, C_CYAN_HEX, C_LIME_HEX, C_ORANGE_HEX, C_LIME_HEX]

bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor='#3A422E', linewidth=0.8)
ax.set_ylabel('Billion PKR / Year (LESCO Scale)', fontsize=9, color=C_MUTED_HEX, labelpad=6)
ax.set_title('DISCO Fiscal Recovery Model (Per 3.5M Consumers)', fontsize=11, pad=12, fontweight='bold', color=C_TEXT_HEX)
ax.axhline(0, color=C_BORDER_HEX, linewidth=1.2)
ax.grid(axis='y', color='#262C1D', linestyle=':', alpha=0.6)
for s in ['top', 'right']: ax.spines[s].set_visible(False)
for s in ['left', 'bottom']: ax.spines[s].set_color(C_BORDER_HEX)

for bar, val in zip(bars, values):
    y = bar.get_height()
    va = 'bottom' if y >= 0 else 'top'
    sign = "+" if y > 0 else ""
    ax.text(bar.get_x() + bar.get_width()/2, y + (0.5 if y>=0 else -1.2), f"{sign}{val:.1f}B", ha='center', va=va, fontsize=8, fontweight='bold', color='#FFFFFF')

ax.set_ylim(-21, 18)
plt.tight_layout()
fig.savefig('charts/roi_recovery.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

print("Regenerated all 4 charts with zero text collisions.")

# -------------------------------------------------------------
# 2. PowerPoint Slide Generation: 16 Expanded Slides
# -------------------------------------------------------------
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def ensure_deck_bg():
    src = 'charts/bg_transmission_lines.jpg'
    dst = 'charts/bg_transmission_lines_deck.jpg'
    if os.path.exists(src) and not os.path.exists(dst):
        from PIL import Image
        import numpy as np
        img = Image.open(src).convert('RGBA')
        w, h = img.size
        bg_base = Image.new('RGBA', (w, h), (17, 21, 10, 255))
        mask = np.zeros((h, w), dtype=np.float32)
        for y in range(h):
            factor = 0.35 + 0.35 * (y / h)
            mask[y, :] = factor
        mask_img = Image.fromarray((mask * 255).astype(np.uint8))
        composite = Image.composite(img, bg_base, mask_img).convert('RGB')
        composite.save(dst, quality=95)

ensure_deck_bg()

def apply_background(slide):
    bg_img = 'charts/bg_transmission_lines_deck.jpg'
    if os.path.exists(bg_img):
        pic = slide.shapes.add_picture(bg_img, 0, 0, prs.slide_width, prs.slide_height)
        return pic
    else:
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

def add_header(slide, tag_text, title_text, subtitle_text=""):
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(6.0), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_LIME

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.36), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = C_MUTED

def add_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.0)
    else:
        shape.line.fill.background()
    return shape

def add_bullet(tf, title, body, color=C_TEXT, space=8):
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.text = f"• {title}: "
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = color
    if space > 0:
        p.space_before = Pt(space)
    
    run = p.add_run()
    run.text = body
    run.font.name = FONT_BODY
    run.font.size = Pt(9.5)
    run.font.bold = False
    run.font.color.rgb = C_MUTED

def add_kpi(slide, left, top, width, height, value, label, sublabel="", val_color=C_LIME):
    add_card(slide, left, top, width, height, bg_color=C_CARD)
    tb = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.14), width - Inches(0.36), height - Inches(0.28))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p1 = tf.paragraphs[0]
    p1.text = value
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = val_color
    
    p2 = tf.add_paragraph()
    p2.text = label.upper()
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT
    p2.space_before = Pt(4)
    
    if sublabel:
        p3 = tf.add_paragraph()
        p3.text = sublabel
        p3.font.name = FONT_BODY
        p3.font.size = Pt(8.5)
        p3.font.color.rgb = C_MUTED
        p3.space_before = Pt(2)

def set_speaker_notes(slide, script, qa=""):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = f"VERBATIM SPEAKER SCRIPT:\n{script}\n\nANTICIPATED JUDGE Q&A DEFENSE:\n{qa}"

# =========================================================================
# SLIDE 1: Title & Executive Vision
# =========================================================================
s1 = prs.slides.add_slide(blank_layout)
apply_background(s1)

banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.85), Inches(11.733), Inches(0.05))
banner.fill.solid()
banner.fill.fore_color.rgb = C_LIME
banner.line.fill.background()

tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.733), Inches(2.3))
tf1 = tb1.text_frame
tf1.word_wrap = True
tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0
p = tf1.paragraphs[0]
p.text = "ISTIKSHAF  [ استکشاف ]"
p.font.name = FONT_HEADING
p.font.size = Pt(50)
p.font.bold = True
p.font.color.rgb = C_LIME

p2 = tf1.add_paragraph()
p2.text = "Autonomous Agentic Revenue Protection & Explainable Grid AI"
p2.font.name = FONT_HEADING
p2.font.size = Pt(24)
p2.font.bold = True
p2.font.color.rgb = C_WHITE
p2.space_before = Pt(8)

p3 = tf1.add_paragraph()
p3.text = "Physics-Grounded Enterprise Intelligence Engine Defeating Non-Technical Losses across Pakistan's Power Grid"
p3.font.name = FONT_BODY
p3.font.size = Pt(14)
p3.font.color.rgb = C_TEXT
p3.space_before = Pt(6)

# 3 Primary Impact Metrics (Bigger, Bolder)
add_kpi(s1, Inches(0.8), Inches(3.6), Inches(3.6), Inches(1.9), "PKR 2.65T", "Circular Debt Crisis", "Suffocating national CPPA liquidity", C_CORAL)
add_kpi(s1, Inches(4.8), Inches(3.6), Inches(3.6), Inches(1.9), "PKR 520B+", "Annual Revenue Lost", "Stolen via kundas & meter bypasses", C_ORANGE)
add_kpi(s1, Inches(8.8), Inches(3.6), Inches(3.733), Inches(1.9), "19.3x", "Raid Precision Gain", "From 3.6% to 69.7% targeted accuracy", C_LIME)

# Prominent Team Section
tb_team = s1.shapes.add_textbox(Inches(0.8), Inches(5.72), Inches(11.733), Inches(0.35))
tf_team = tb_team.text_frame
tf_team.margin_left = tf_team.margin_top = tf_team.margin_right = tf_team.margin_bottom = 0
p_th = tf_team.paragraphs[0]
p_th.text = "CORE ENGINEERING & RESEARCH TEAM"
p_th.font.name = FONT_MONO
p_th.font.size = Pt(11)
p_th.font.bold = True
p_th.font.color.rgb = C_LIME

team = [
    ("Hadiah Batool", "Core ML & Research"),
    ("Hashim Khushal Khan", "Grid Physics & Modeling"),
    ("Hamza Sultan", "System & Agent Architecture"),
    ("Huda Ali", "Data & Streaming Pipeline")
]

def add_team_member(slide, left, top, width, height, name, role):
    card = add_card(slide, left, top, width, height, bg_color=C_CARD_ALT, border_color=RGBColor(80, 100, 50))
    tb = slide.shapes.add_textbox(left + Inches(0.16), top + Inches(0.14), width - Inches(0.32), height - Inches(0.28))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p1 = tf.paragraphs[0]
    p1.text = name
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p2 = tf.add_paragraph()
    p2.text = role.upper()
    p2.font.name = FONT_MONO
    p2.font.size = Pt(9.0)
    p2.font.bold = True
    p2.font.color.rgb = C_CYAN
    p2.space_before = Pt(4)

w_tm = Inches(2.783)
gap = Inches(0.20)
for idx, (m_name, m_role) in enumerate(team):
    add_team_member(s1, Inches(0.8) + idx * (w_tm + gap), Inches(6.12), w_tm, Inches(0.95), m_name, m_role)

set_speaker_notes(s1,
    "Judges and energy sector leaders: Every year, over 520 Billion Rupees vanishes from Pakistan's power grid into thin air. It is called Non-Technical Loss—power theft, illegal hookups, and meter tampering. It is the primary engine behind Pakistan's crippling 2.65 Trillion Rupee circular debt. Today, our team—Hadiah Batool, Hashim Khushal Khan, Hamza Sultan, and Huda Ali—presents Istikshaf: an autonomous, physics-grounded enterprise AI platform that transforms revenue protection from blind manual spot-checks into precision enforcement.",
    "Q: Why hasn't this been solved by smart meters?\nA: Because 65% of Pakistan's grid relies on legacy analog meters, and national AMI rollout will take 15 years. Istikshaf is engineered as a dual-track architecture: it solves grid theft on legacy analog meters today with 69.7% precision, while instantly unlocking a 5.5x detection surge when smart meters are connected."
)

# =========================================================================
# SLIDE 2: Macroeconomic Breakdown: Pakistan Power Sector in Numbers
# =========================================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "Macro Economic Crisis", "The Bleeding Grid: Pakistan's Power Sector in Numbers", "10 Distribution Companies lose between 8% and 38% of distributed electricity annually")

add_card(s2, Inches(0.8), Inches(1.85), Inches(5.2), Inches(5.0))
tb = s2.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.8), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "THE CIRCULAR DEBT ACCELERATOR"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "National Average NTL (18.5%)", "Non-technical loss across Pakistan's distribution grid averages 18.5%, with regional hot-spots like PESCO (37.4%) and SEPCO (35.8%) hemorrhaging over a third of distributed energy.", space=6)
add_bullet(tf, "Fiscal Black Hole", "Over PKR 520 Billion is stolen annually, forcing repetitive tariff hikes that penalize law-abiding consumers while leaving utility balance sheets insolvent.", space=8)
add_bullet(tf, "IMF Conditionalities", "Stabilizing circular debt is a non-negotiable structural benchmark for sovereign credit ratings and macroeconomic liquidity.", space=8)

s2.shapes.add_picture('charts/disco_losses.png', Inches(6.3), Inches(1.85), width=Inches(6.233))

set_speaker_notes(s2,
    "Look at this landscape. Distribution loss is not a marginal leak; it is an economic hemorrhage. In PESCO and SEPCO, more than one in every three kilowatt-hours distributed simply vanishes. Even in relatively efficient zones like LESCO and K-Electric, losses exceed 12 to 15 percent. This is why tariffs keep rising for honest families—to cover the cost of stolen energy.",
    "Q: Can DISCOs survive without subsidies if theft continues?\nA: No. CPPA-G liquidity collapses without sovereign subsidies unless NTL is brought under 10% nationwide."
)

# =========================================================================
# SLIDE 3: Distribution Infrastructure & Physical Reality (STYLIZED KHAMBA IMAGE)
# =========================================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "Physical Distribution Reality", "The Infrastructure Battleground: Feeders, Transformers & Khambe", "How physical energy distribution operates across 11kV overhead radial feeders")

# Image on Left
if os.path.exists('charts/cyber_pole.jpg'):
    s3.shapes.add_picture('charts/cyber_pole.jpg', Inches(0.8), Inches(1.85), width=Inches(6.0))

# Content on Right
add_card(s3, Inches(7.1), Inches(1.85), Inches(5.433), Inches(5.0))
tb = s3.shapes.add_textbox(Inches(7.3), Inches(2.05), Inches(5.033), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "THE 3-TIER GRID HIERARCHY"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "11kV Primary Distribution Feeders", "Radial medium-voltage lines spanning long geographic distances, subject to high non-linear thermal dissipation (I²R losses).", space=6)
add_bullet(tf, "Pole-Mounted Transformers (PMTs / Khambe)", "Step down 11kV to 415V/230V for local clusters of 30-35 consumers. The critical aggregation choke-point where energy balance must be conserved.", space=8)
add_bullet(tf, "Low-Voltage Drop Lines & Kundas", "Uninsulated overhead conductors where illegal kunda hooks are physically attached to bypass wall-mounted meters completely.", space=8)
add_bullet(tf, "65% Analog Meter Fleet", "Legacy spinning aluminum disc meters vulnerable to external magnetic braking, needle jamming, and neutral loop cuts.", space=8)

set_speaker_notes(s3,
    "To solve power theft in Pakistan, you must understand the physical infrastructure. Electricity flows from 132kV substations down 11kV radial feeders into Pole-Mounted Transformers—the local 'Khamba'. Each khamba feeds roughly 30 to 35 households. This is the vulnerable frontier: low-voltage drop lines where unmetered kundas are hooked. 65% of the meters on these walls are mechanical discs with zero remote telemetry.",
    "Q: Why don't linemen just cut down every kunda they see?\nA: Kundas are frequently connected only at night during peak hours or summer heatwaves and removed before morning inspections, or linemen are paid off by local syndicates."
)

# =========================================================================
# SLIDE 4: Why Conventional Utility Audits Fail
# =========================================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Operational Vulnerability", "Why Current Utility Audits Fail: Blind Spot-Checks & Bribery", "Traditional revenue protection relies on manual guesswork that misses 96% of theft")

# 3 Cards Layout
w3 = Inches(3.75)
h3 = Inches(4.9)

add_card(s4, Inches(0.8), Inches(1.9), w3, h3)
tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. THE 3.6% RANDOM HIT RATE"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Blind Manual Patrols", "Linemen drive patrol trucks down streets inspecting random connections. Over 96 out of 100 inspections find nothing.", space=6)
add_bullet(tf, "Enormous Logistical Waste", "DISCOs burn millions in fuel, vehicle maintenance, and inspector man-hours with virtually zero deterrence.", space=8)

add_card(s4, Inches(4.78), Inches(1.9), w3, h3)
tb = s4.shapes.add_textbox(Inches(4.98), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. THE COLLUSION RING"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_ORANGE
add_bullet(tf, "Handheld Terminal Fraud", "Corrupt meter readers enter artificially suppressed readings for commercial plazas in exchange for monthly bribes.", space=6)
add_bullet(tf, "Corrupted Inspection Logs", "Historical utility databases are poisoned: innocent consumers are falsely cited while heavy industrial thieves remain unrecorded.", space=8)

add_card(s4, Inches(8.76), Inches(1.9), Inches(3.773), h3)
tb = s4.shapes.add_textbox(Inches(8.96), Inches(2.1), Inches(3.373), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "3. WESTERN AI FAILURES"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Presupposes 100% Smart Grid", "Foreign models assume 15-minute cellular telemetry and continuous 99.9% grid uptime.", space=6)
add_bullet(tf, "Confounder Blindness", "Treats unscheduled load-shedding blackouts and rooftop solar net-metering as criminal meter tampering.", space=8)

set_speaker_notes(s4,
    "Why are DISCO inspection teams failing? Because they are flying blind. They conduct manual spot checks that find theft on barely 3 out of every 100 raids. Worse, meter readers collude with commercial consumers, manually entering lower numbers in their handheld devices. And off-the-shelf Western AI fails because it doesn't understand Pakistan's grid realities.",
    "Q: How does Istikshaf bypass corrupted meter reader reports?\nA: Istikshaf balances energy at the transformer totalizer level: even if a meter reader under-reports consumer units, the energy gap at the PMT reveals the deficit mathematically."
)

# =========================================================================
# SLIDE 5: Grid Confounders That Break Standard AI
# =========================================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "Domain Complexity", "Local Grid Confounders That Break Conventional AI Models", "How load shedding, rooftop solar, and extreme climate generate false positives")

w2 = Inches(5.7)
h2 = Inches(2.35)

add_card(s5, Inches(0.8), Inches(1.9), w2, h2)
tb = s5.shapes.add_textbox(Inches(1.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. UNSCHEDULED LOAD SHEDDING (OUTAGES)"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_ORANGE
add_bullet(tf, "The Feeder Outage Trap", "When feeder uptime drops to 75% during rolling blackouts, all 33 consumers on a transformer drop consumption simultaneously.", space=4)
add_bullet(tf, "Istikshaf Normalization", "Our uptime-discount feature divides usage deviation by feeder uptime: Usage_Dev / Uptime_feeder, neutralizing blackout false alarms.", space=4)

add_card(s5, Inches(6.8), Inches(1.9), w2, h2)
tb = s5.shapes.add_textbox(Inches(7.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. ROOFTOP SOLAR DUCK CURVE (NET-METERING)"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Midday Plunge (70-90% Drop)", "Residential solar prosumers export power during sunny midday hours, mimicking sudden meter tampering.", space=4)
add_bullet(tf, "Istikshaf Solar Gate", "Hard-gated to 0.0 for registered net-metering accounts, achieving 100% specificity (0.00% false alarms on solar homes).", space=4)

add_card(s5, Inches(0.8), Inches(4.5), w2, h2)
tb = s5.shapes.add_textbox(Inches(1.0), Inches(4.65), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "3. CLIMATIC LOAD COUPLING"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "45°C Heatwaves vs Winter Gas Gaps", "Extreme summer nocturnal air-conditioning load contrasts with winter morning electric geyser spikes.", space=4)
add_bullet(tf, "Istikshaf Seasonal Baseline", "Models historical month-of-year baselines coupled with dynamic seasonal threshold adjustment agents.", space=4)

add_card(s5, Inches(6.8), Inches(4.5), w2, h2)
tb = s5.shapes.add_textbox(Inches(7.0), Inches(4.65), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "4. POVERTY BIAS VS. CRIMINAL THEFT"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Arrears Conflation", "Tariff hikes leave low-income households with unpaid debt. Off-the-shelf models treat debt as criminal theft.", space=4)
add_bullet(tf, "Istikshaf Debt Normalization", "Arrears are annualized and bounded at [0, 10], separating economic hardship from deliberate meter bypass.", space=4)

set_speaker_notes(s5,
    "Here is why naive machine learning creates public relations disasters for DISCOs: when load shedding strikes, power usage drops across the feeder. An off-the-shelf model flags the entire neighborhood as a theft syndicate. When an honest citizen installs solar panels, their midday grid draw drops 85%—naive AI triggers a police raid. Istikshaf builds physical invariance into the features, eliminating these false alarms completely.",
    "Q: What happens if an unregistered solar user drops their load?\nA: The Midday Duck Index captures the solar generation signature specifically between 10 AM and 3 PM while evening peak draw remains high, separating solar generation from full-day theft."
)

# =========================================================================
# SLIDE 6: The 51.8 Million Telemetry Engine (SUBSTATION / FEEDER IMAGE)
# =========================================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Data Engineering & Scale", "The 51.8 Million Telemetry Engine: Grounded in Physics", "Dual-track architecture modeling 10,000 grid consumers and 51.8M hourly smart meter records")

# Image on Left
if os.path.exists('charts/feeder_substation.jpg'):
    s6.shapes.add_picture('charts/feeder_substation.jpg', Inches(0.8), Inches(1.85), width=Inches(6.0))

# Content on Right
add_card(s6, Inches(7.1), Inches(1.85), Inches(5.433), Inches(5.0))
tb = s6.shapes.add_textbox(Inches(7.3), Inches(2.05), Inches(5.033), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "TRACK 1 & TRACK 2 ARCHITECTURAL SPECS"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "30 Feeders & 300 PMTs", "10,000 consumers mapped across a complete 3-tier distribution hierarchy operating over 36 consecutive months (360k panel records).", space=6)
add_bullet(tf, "Thermodynamic Energy Balance", "First Law of Thermodynamics enforced: |Injected - (Billed + Stolen + Technical Loss)| < 0.5 kWh across all 300 transformers every month.", space=8)
add_bullet(tf, "51,819,270 Hourly Interval Rows", "2,000 AMI consumers disaggregated into 36 months of 1-hour interval readings in 322MB Snappy Parquet.", space=8)
add_bullet(tf, "Sub-Minute Big Data Execution", "Out-of-core PyArrow batch streaming processes the entire 51.8M dataset in 5.5 minutes using < 200MB RAM.", space=8)

set_speaker_notes(s6,
    "Look at the scale of our data engineering. Track 1 captures 10,000 consumers across 30 feeders and 300 transformers over 3 full years. Every single transformer adheres to thermodynamic conservation laws. Track 2 disaggregates 2,000 smart meter consumers into 51.8 million hourly telemetry readings. Our out-of-core PyArrow engine processes the entire 51.8 million records in 5.5 minutes on lightweight hardware.",
    "Q: Can your pipeline handle live streaming smart meter feeds?\nA: Yes. The PyArrow batch aggregator operates on micro-batches, allowing sub-second incremental feature updates as hourly smart meter payloads arrive."
)

# =========================================================================
# SLIDE 7: High-Frequency AMI Smart Meter Telemetry (SMART METER IMAGE)
# =========================================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Next-Gen Metering", "High-Frequency Smart Meters: Unmasking Time-of-Use Bypass", "Why 1-hour AMI interval streams unlock a 5.5x increase in catching evasive theft")

# Image on Left
if os.path.exists('charts/smart_meter.jpg'):
    s7.shapes.add_picture('charts/smart_meter.jpg', Inches(0.8), Inches(1.85), width=Inches(6.0))

# Content on Right
add_card(s7, Inches(7.1), Inches(1.85), Inches(5.433), Inches(5.0))
tb = s7.shapes.add_textbox(Inches(7.3), Inches(2.05), Inches(5.033), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "THE AMI TELEMETRY REVOLUTION"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "The Peak-Hour Shaver Blindspot", "Consumers who bypass meters only between 6 PM and 10 PM show only a ~6% drop in monthly totals, making them virtually invisible on monthly bills (10.6% recall).", space=6)
add_bullet(tf, "Hourly Interval Disaggregation", "At 1-hour resolution, the peak window flatline drops to zero while daytime usage remains normal—a glaring, unmistakable theft signature.", space=8)
add_bullet(tf, "5.5x Recall Surge (58.3%)", "Connecting AMI smart meter data boosts Peak Shaver detection recall by +47.8 points, from 10.6% to 58.3%.", space=8)
add_bullet(tf, "75% Bandwidth Cost Reduction", "We prove that 1-hour interval sampling captures >90% of maximum theft signal while cutting cellular SIM transmission costs by 75% vs 15-minute polling.", space=8)

set_speaker_notes(s7,
    "Here is why smart meters are revolutionary when paired with Istikshaf: Consider the Peak Shaver. Under NEPRA rules, peak units cost 2.5 times more. A consumer bypasses the meter strictly between 6 PM and 10 PM. On a monthly bill, this looks like a minor 6% drop—invisible. But at 1-hour resolution, their peak window drops to zero while daytime is active. Our model catches 58.3% of these evaders—a 5.5-fold increase.",
    "Q: Why not sample at 15-minute intervals?\nA: In Pakistan, transmitting 15-minute telemetry over cellular SIMs quadruples telecom data costs and battery drain on meters without providing statistically significant detection uplift over 1-hour sampling."
)

# =========================================================================
# SLIDE 8: 14 Behavioral Archetypes: Theft Vectors vs. Confounders
# =========================================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Domain Taxonomy", "Unmasking 14 Behavioral Archetypes: 8 Theft Vectors & 6 Confounders", "Comprehensive mathematical modeling of real-world consumer behavior in Pakistan")

w2 = Inches(5.7)
h2 = Inches(5.0)

# Left Column: Theft
add_card(s8, Inches(0.8), Inches(1.85), w2, h2)
tb = s8.shapes.add_textbox(Inches(1.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "8 ILLICIT THEFT ARCHETYPES (8.0% GROUND TRUTH)"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Slab Defender (150)", "Pins meter reading below 200/300 kWh threshold to avoid NEPRA punitive slab multipliers.", space=4)
add_bullet(tf, "Peak Hour Shaver (100)", "Shunts load strictly during high-cost peak window (6 PM-10 PM).", space=4)
add_bullet(tf, "Nighttime AC Shunt (120)", "Bypasses meter at night during summer months (11 PM-5 AM) to run heavy bedroom cooling.", space=4)
add_bullet(tf, "Direct Kunda Hookup (150)", "Bare wire over overhead distribution line escalating in 5 stages to 92% bypass.", space=4)
add_bullet(tf, "Gradual Mechanical Slowdown (100)", "Needle/magnetic resistance on analog disc decaying 2-3% each month.", space=4)
add_bullet(tf, "Fixed Resistor Shunt (100)", "Hardware CT resistor shunting 45-55% load year-round.", space=4)
add_bullet(tf, "Collusion & Intermittent (80)", "Corrupt reader routes (shaving 20%) and burst welding/machinery hookups.", space=4)

# Right Column: Confounders
add_card(s8, Inches(6.8), Inches(1.85), w2, h2)
tb = s8.shapes.add_textbox(Inches(7.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "6 LEGITIMATE CONFOUNDERS (92.0% POPULATION)"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Solar Prosumer (1,200)", "Rooftop solar net-metering producing deep midday duck curve, isolated via net-metering gating (0.00% FPR).", space=6)
add_bullet(tf, "Seasonal Village Traveler (300)", "Extended trips to ancestral villages for 1-3 months; sharp 90% drops that mimic sudden theft before rebounding.", space=6)
add_bullet(tf, "Energy Efficient Upgrade (300)", "Permanent 15-35% step-down drop from retrofitting inverter ACs and LED lighting.", space=6)
add_bullet(tf, "Vacant Properties (500)", "Unoccupied homes drawing only phantom standby power (5-15 kWh/month).", space=6)
add_bullet(tf, "Low-Income Frugal (300)", "Lifeline tariff consumers (<50 kWh/mo) with basic lighting and single ceiling fan.", space=6)
add_bullet(tf, "Standard Household (6,600)", "Baseline residential consumption coupled with ambient summer cooling curves.", space=6)

set_speaker_notes(s8,
    "Theft in Pakistan is not uniform. It follows distinct human strategies. We modeled 14 precise archetypes. Consider the Slab Defender: crossing 200 units doubles your per-unit bill, so consumers tamper only near the end of the month. Or the Nighttime AC user who flips a bypass switch strictly while sleeping. We also model legitimate confounders like village travelers and inverter upgrades so innocent consumers are protected.",
    "Q: How does the model identify collusion among meter readers?\nA: Collusion archetypes occur along specific meter reader route IDs (R-COL-01 to 05). By correlating route IDs with transformer loss percentiles, the system detects collective reader suppression."
)

# =========================================================================
# SLIDE 9: Diurnal Load Curves & Tampering Signatures (CLEAN CHART SLIDE)
# =========================================================================
s9 = prs.slides.add_slide(blank_layout)
apply_background(s9)
add_header(s9, "Telemetry Signatures", "24-Hour Diurnal Curves: Unmasking Peak Shavers & Solar Ducks", "High-frequency interval resolution separates legitimate clean energy from criminal bypass")

# Left Column: Concise Takeaways
add_card(s9, Inches(0.8), Inches(1.85), Inches(5.2), Inches(5.0))
tb = s9.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.8), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "DIURNAL SIGNATURE ANALYSIS"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "White Curve (Normal Baseline)", "Clear morning peak at 8 AM and evening peak at 8 PM, matching REWD-P empirical Pakistani load profiles.", space=6)
add_bullet(tf, "Cyan Curve (Solar Duck Curve)", "Midday grid draw drops to near-zero between 10 AM and 3 PM during maximum solar irradiance, then rebounds for evening peak.", space=8)
add_bullet(tf, "Coral Curve (Peak Shaver Theft)", "Normal daytime consumption, followed by an abrupt flatline drop during the 6 PM-10 PM peak tariff window.", space=8)
add_bullet(tf, "Orange Curve (Night AC Shunt)", "Heavy power draw during evening, followed by an illicit zero-draw bypass between 11 PM and 5 AM.", space=8)

# Right Column: Clean Chart
s9.shapes.add_picture('charts/diurnal_theft_signatures.png', Inches(6.3), Inches(1.85), width=Inches(6.233))

set_speaker_notes(s9,
    "Look at this chart. This is why high-frequency interval data transforms detection. In white is the normal Pakistani household. In cyan is a solar prosumer—notice the deep midday duck curve, but notice how it rebounds in the evening. In coral is the Peak Shaver: active all day, but flatlining strictly during the NEPRA peak window. In orange is the Night AC bypass. These signatures are unmistakable at hourly resolution.",
    "Q: How do you handle cellular GPRS packet drops in smart meters?\nA: Our interval engine models 1.5% cellular telemetry packet drops (NaNs) and uses rolling spline interpolation to ensure robust feature extraction despite intermittent connectivity."
)

# =========================================================================
# SLIDE 10: Two-Stage Hybrid ML Architecture
# =========================================================================
s10 = prs.slides.add_slide(blank_layout)
apply_background(s10)
add_header(s10, "Machine Learning Design", "The Two-Stage Hybrid Inference Engine: Unsupervised + Supervised", "Stacking out-of-fold anomaly scoring with asymmetric cost-weighted boosted ensembles")

w3 = Inches(3.75)
h3 = Inches(4.9)

add_card(s10, Inches(0.8), Inches(1.9), w3, h3)
tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 1: ISOLATION FOREST"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Unsupervised Zero-Day Detection", "Standard supervised models fail on novel tampering methods. Isolation Forest isolates abnormal geometric vectors without labels.", space=6)
add_bullet(tf, "5-Fold GroupKFold Validation", "Trained grouped strictly by consumer_id across 36 months, preventing temporal or spatial leakage.", space=8)
add_bullet(tf, "Out-of-Fold Anomaly Score", "Generates an unbiased out-of-fold score fed directly as a feature into the Stage 2 classifier.", space=8)

add_card(s10, Inches(4.78), Inches(1.9), w3, h3)
tb = s10.shapes.add_textbox(Inches(4.98), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 2: COST-WEIGHTED XGBOOST"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Asymmetric Cost Weighting", "Enforces scale_pos_weight = 11.5, penalizing missed theft 11.5x more than false alarms to overcome 8% class imbalance.", space=6)
add_bullet(tf, "Multi-Modal Feature Fusion", "Combines Stage 1 anomaly scores with 12 Track 1 grid features and 7 Track 2 interval ratios.", space=8)
add_bullet(tf, "TreeSHAP Explainer Engine", "Extracts local Shapley value attributions for every single decision, producing tribunal-grade evidence dockets.", space=8)

add_card(s10, Inches(8.76), Inches(1.9), Inches(3.773), h3)
tb = s10.shapes.add_textbox(Inches(8.96), Inches(2.1), Inches(3.373), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 3: PLATT CALIBRATION"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Frozen Logistic Sigmoid", "Uncalibrated boosted trees compress probabilities near 0.1-0.3. FrozenEstimator fits a smooth sigmoid on calibration split.", space=6)
add_bullet(tf, "Probability Surge to 73.3%", "Scales raw pseudo-probabilities up to 73.3%, providing trustworthy confidence scores for DISCO operations.", space=8)
add_bullet(tf, "Operational Decision Tiers", "High Risk (P >= 0.70): Field Raid Dispatch.\nMedium Risk (0.50 <= P < 0.70): Automated Soft Nudge.", space=8)

set_speaker_notes(s10,
    "Here is why our architecture is unmatched. We combine unsupervised and supervised intelligence. An Out-of-Fold Isolation Forest scans for 'unknown unknowns'—brand-new tampering tricks never seen in training. That signal feeds into an extreme gradient-boosted ensemble tuned with an asymmetric 11.5x penalty on missed theft. Finally, a frozen Platt Scaler calibrates the outputs into true probabilities that utility executives can stake their budgets on.",
    "Q: Why use GroupKFold on consumer_id?\nA: Standard K-Fold splits random rows, leaking past months of a consumer into the test set of the same consumer. GroupKFold ensures a consumer's entire 36-month panel is either completely in train or completely in test."
)

# =========================================================================
# SLIDE 11: 19 Advanced Domain-Grounded Features
# =========================================================================
s11 = prs.slides.add_slide(blank_layout)
apply_background(s11)
add_header(s11, "Feature Engineering", "19 Advanced Domain Features: Invariance Engineering Defeating Confounders", "Mathematical formulations specifically engineered to eliminate false alarms and detect structural breaks")

w2 = Inches(5.7)
h2 = Inches(2.35)

add_card(s11, Inches(0.8), Inches(1.9), w2, h2)
tb = s11.shapes.add_textbox(Inches(1.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. VECTORIZED CUSUM CHANGE-POINT BREAKS"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Break Formula", "S_t = Max(0, S_{t-1} + (Mean_base - x_t) - k). Evaluates cumulative deviation peaks to pinpoint the exact month theft began without future leakage.", space=4)
add_bullet(tf, "Clean 3-Month Anchor", "Anchoring against uncontaminated initial months prevents rolling baselines from absorbing creeping theft into the 'new normal'.", space=4)

add_card(s11, Inches(6.8), Inches(1.9), w2, h2)
tb = s11.shapes.add_textbox(Inches(7.0), Inches(2.05), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. PMT PERCENTILE LOSS RANKING"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Monthly Percentile Rank", "Transforms raw transformer technical loss into a normalized 0.0-1.0 percentile rank across all 300 PMTs for each calendar month.", space=4)
add_bullet(tf, "Weather Invariance", "Eliminates grid-wide summer/winter technical dissipation spikes, isolating localized high-theft transformer pockets.", space=4)

add_card(s11, Inches(0.8), Inches(4.5), w2, h2)
tb = s11.shapes.add_textbox(Inches(1.0), Inches(4.65), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "3. LOAD-SHEDDING & SOLAR INVARIANCE GATES"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_ORANGE
add_bullet(tf, "Uptime Normalization", "Consumer deviation divided by feeder uptime percentage: Usage_Dev / Uptime_feeder. If power was cut 25%, usage drop is discounted to zero.", space=4)
add_bullet(tf, "Solar Net-Metering Gate", "Hard-gated to 0.0 for registered prosumers, eliminating wrongful accusations against solar adoption.", space=4)

add_card(s11, Inches(6.8), Inches(4.5), w2, h2)
tb = s11.shapes.add_textbox(Inches(7.0), Inches(4.65), w2 - Inches(0.4), h2 - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "4. 7 SCALE-INVARIANT AMI LOAD RATIOS"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Peak Window Flatline", "Measures fraction of peak hours (6-10 PM) below 0.05 kWh—exposing Peak Shaver bypasses with 5.5x recall gain.", space=4)
add_bullet(tf, "Night AC & Midday Duck Ratios", "Scale-invariant ratios comparing nocturnal summer draw and midday solar troughs against daily baselines.", space=4)

set_speaker_notes(s11,
    "We engineered 19 domain-grounded features. Our vectorized CUSUM algorithm detects the exact month a bypass began, without leaking future data. Our clean baseline anchor prevents rolling averages from absorbing stolen power. And our uptime-discount feature normalizes consumer draw against feeder availability, meaning load shedding never triggers a false alarm.",
    "Q: Why are scale-invariant ratios critical for Track 2?\nA: Scale-invariant ratios look at the *shape* of consumption rather than absolute kilowatt-hours, allowing the model to detect theft on 1 kW small shops and 50 kW commercial plazas with identical mathematical precision."
)

# =========================================================================
# SLIDE 12: Empirical Benchmarks & Smart-Meter Uplift (CLEAN CHART SLIDE)
# =========================================================================
s12 = prs.slides.add_slide(blank_layout)
apply_background(s12)
add_header(s12, "Benchmark Verification", "Proven Operational Uplift: 19.3x Precision & 5.5x Peak Uplift", "Rigorous out-of-sample evaluation on isolated 20% test splits across 72,000 consumer-months")

# Left Column: Performance Metrics
add_card(s12, Inches(0.8), Inches(1.85), Inches(5.2), Inches(5.0))
tb = s12.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.8), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "RIGOROUS EVALUATION PROOF"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "19.3x Precision Multiplier", "Istikshaf achieves 69.7% precision on standard monthly billing data, compared to the 3.6% baseline yield of random DISCO line audits.", space=6)
add_bullet(tf, "Recall More Than Doubled", "Overall detection recall rises from 20.3% to 45.7% when AMI smart-meter telemetry is enabled (+25.4 points).", space=8)
add_bullet(tf, "5.5x Leap on Peak Evaders", "Peak Shaver recall surges from 10.6% on monthly bills to 58.3% on interval streams (+47.8 points).", space=8)
add_bullet(tf, "Zero Solar False Alarms", "Maintains 100.00% specificity (0.00% false positive rate) on registered solar net-metering prosumers.", space=8)

# Right Column: Clean Chart
s12.shapes.add_picture('charts/ami_uplift_benchmarks.png', Inches(6.3), Inches(1.85), width=Inches(6.233))

set_speaker_notes(s12,
    "The numbers prove our superiority. In standard monthly grids, Istikshaf delivers 69.7% precision—a 19.3-fold increase in raid efficiency over current utility spot-checks. When smart meters are introduced, our streaming engine more than doubles recall to 45.7% and achieves a 5.5x increase in catching peak-hour evaders. All while delivering a zero-percent false alarm rate on solar homes.",
    "Q: How do you verify these metrics are out-of-sample?\nA: All metrics are computed strictly on the held-out 20% evaluation split (Months 31 to 36, grouped by consumer_id). The model was never exposed to these consumers during training or calibration."
)

# =========================================================================
# SLIDE 13: The 8-Agent Autonomous Swarm
# =========================================================================
s13 = prs.slides.add_slide(blank_layout)
apply_background(s13)
add_header(s13, "Autonomous Enforcement", "The 8-Agent Autonomous Swarm: Eliminating the Human Bottleneck", "Multi-agent dispatch orchestrator automating triage, deduplication, and field routing")

w4 = Inches(2.78)
h4 = Inches(5.0)

add_card(s13, Inches(0.8), Inches(1.9), w4, h4)
tb = s13.shapes.add_textbox(Inches(0.95), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. CONFAIR & AUDIT"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Confound Checker", "Intercepts raw model alerts. Cancels flags if feeder uptime dropped below 80% or solar export is active.", space=6)
add_bullet(tf, "Audit Logger", "Writes cryptographic, append-only logs for compliance, ensuring every dispatch decision is legally defensible.", space=8)

add_card(s13, Inches(3.78), Inches(1.9), w4, h4)
tb = s13.shapes.add_textbox(Inches(3.93), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. DEDUP & HISTORY"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Case Dedup Guard", "Prevents redundant dispatching by verifying whether an open investigation docket already exists in SQLite.", space=6)
add_bullet(tf, "Recidivism Checker", "Cross-references repeat offender registries and boosts raid priority for repeat violators caught in prior cycles.", space=8)

add_card(s13, Inches(6.76), Inches(1.9), w4, h4)
tb = s13.shapes.add_textbox(Inches(6.91), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "3. ROUTING & NUDGE"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_ORANGE
add_bullet(tf, "Dual-Router Agent", "Splits flags into two channels: detailed SHAP dossiers for HQ analysts, and concise field orders for linemen.", space=6)
add_bullet(tf, "Soft-Warning Nudge", "Sends automated billing SMS nudges for mid-risk cases (0.50 <= P < 0.70), prompting self-correction with 0 raid costs.", space=8)

add_card(s13, Inches(9.74), Inches(1.9), Inches(2.79), h4)
tb = s13.shapes.add_textbox(Inches(9.89), Inches(2.1), Inches(2.49), h4 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "4. LOCALIZE & PRIVACY"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Urdu Localization", "Translates SHAP vectors into natural Roman Urdu dispatched via SMS to field linemen mobile phones.", space=6)
add_bullet(tf, "PII Masking Agent", "Hashes and masks consumer identities before external dispatch, preserving consumer privacy.", space=8)

set_speaker_notes(s13,
    "A probability score on a dashboard recovers zero rupees. That is why we built the Istikshaf 8-Agent Swarm. The Confound Agent verifies feeder uptime. The Dedup Guard ensures crews aren't dispatched twice to the same site. The Recidivism Agent tracks repeat offenders. And our Soft-Warning Agent automatically nudges medium-risk consumers via SMS, recovering revenue before spending raid resources.",
    "Q: How does the agent loop integrate with SMS gateways?\nA: The Dual-Router outputs standard REST webhooks compatible with Twilio or local Pakistani telecom SMS aggregators (e.g. Jazz, Telenor, Zong)."
)

# =========================================================================
# SLIDE 14: TreeSHAP Explainability & Roman Urdu Field Operations
# =========================================================================
s14 = prs.slides.add_slide(blank_layout)
apply_background(s14)
add_header(s14, "Explainability & Field Ops", "Defensible in Court, Actionable on the Street: SHAP & Roman Urdu", "Translating complex mathematical attributions into tribunal evidence and lineman action")

add_card(s14, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s14.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "LEGAL REVENUE PROTECTION DOCKET (ENGLISH)"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Consumer ID", "C-000480 | Sanctioned Load: 15 kW (Commercial Plaza)", space=4)
add_bullet(tf, "Grid Topology", "Feeder F-12 / PMT-0114 (Transformer Loss: 94th Percentile)", space=4)
add_bullet(tf, "Calibrated Risk", "71.4% [HIGH RISK - DISPATCH ENFORCEMENT TEAM]", space=4)
add_bullet(tf, "Primary Factor 1", "Peak Window Flatline: 0.00 kW on 84.6% of peak hours (6-10 PM) despite 3.8 kW daytime draw (SHAP Impact: +0.34).", space=6)
add_bullet(tf, "Primary Factor 2", "Vectorized CUSUM Break: Abrupt 48% drop detected starting Month 11; persisted continuously for 25 months (SHAP Impact: +0.21).", space=6)
add_bullet(tf, "Primary Factor 3", "Transformer Energy Balance: PMT-0114 non-technical loss rose by 14.2% concurrently with consumer drop (SHAP Impact: +0.12).", space=6)

add_card(s14, Inches(6.8), Inches(1.85), Inches(5.733), Inches(5.0), bg_color=C_CARD_ALT)
tb = s14.shapes.add_textbox(Inches(7.0), Inches(2.05), Inches(5.333), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "FIELD CREW SMS DISPATCH (ROMAN URDU)"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME

p_box = tf.add_paragraph()
p_box.text = '📱 MOBILE ALERT SENT TO SDO / LINEMAN IN CHARGE:'
p_box.font.name = FONT_MONO
p_box.font.size = Pt(9.5)
p_box.font.bold = True
p_box.font.color.rgb = C_MUTED
p_box.space_before = Pt(8)

p_sms = tf.add_paragraph()
p_sms.text = '========================================\n' \
             'BA-HAWAALA CONSUMER: C-000480\n' \
             'FEEDER: F-12  |  PMT: PMT-0114\n' \
             'THEFT RISK: 71.4% (INTEHAYI KHATRAK)\n' \
             '----------------------------------------\n' \
             'TAFSEELAT-E-CHOORI:\n' \
             '1. Sham 6 se 10 bajay k doran meter par\n' \
             '   84% load gayab paya gaya hai.\n' \
             '2. PMT-0114 par line loss 14.2% barh chuka\n' \
             '   hai customer k drop k sath.\n' \
             '3. CUSUM break se pata chalta hai k\n' \
             '   tampering 25 mahino se jari hai.\n' \
             '----------------------------------------\n' \
             'HUKM: Fori enforcement team rawana\n' \
             'karein aur bypass switch zabt karein.\n' \
             '========================================'
p_sms.font.name = FONT_MONO
p_sms.font.size = Pt(10)
p_sms.font.color.rgb = C_LIME
p_sms.space_before = Pt(4)

set_speaker_notes(s14,
    "AI must be defensible in tribunal hearings and actionable for linemen who don't read English machine learning vectors. Using TreeSHAP, every inspection docket details the exact physical factors that triggered the alert. Our Urdu Localization Agent translates these technical attributions into natural Roman Urdu, sent directly to field inspectors' mobile phones via SMS. No guesswork, no ambiguity—just actionable intelligence.",
    "Q: How do you verify the Roman Urdu messages don't hallucinate?\nA: The localization agent uses constrained slot-filling templates bound directly to the top TreeSHAP features, ensuring zero LLM hallucination."
)

# =========================================================================
# SLIDE 15: Istikshaf Grid Noir Tactical Command Center
# =========================================================================
s15 = prs.slides.add_slide(blank_layout)
apply_background(s15)
add_header(s15, "Enterprise Platform", "Istikshaf Grid Noir: Tactical Command Center & 3D Digital Twin", "High-density dark mode desktop application engineered for 24/7 utility control rooms")

w3 = Inches(3.75)
h3 = Inches(4.9)

add_card(s15, Inches(0.8), Inches(1.9), w3, h3)
tb = s15.shapes.add_textbox(Inches(1.0), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. 3D WEBGL DIGITAL TWIN"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Spatial Grid Topology", "Renders 30 11kV primary feeders and 300 pole-mounted transformers in an interactive 3D WebGL force-directed graph.", space=6)
add_bullet(tf, "Dynamic Load Heatmaps", "Visualizes real-time power injection, technical loss dissipation, and localized transformer overload in high-contrast neon accents.", space=8)
add_bullet(tf, "Theft Pocket Clustering", "Highlights transformer loss hot-spots where coordinated theft rings operate.", space=8)

add_card(s15, Inches(4.78), Inches(1.9), w3, h3)
tb = s15.shapes.add_textbox(Inches(4.98), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. CONSUMER DEEP-DIVE"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Dual-Horizon Visualizer", "Side-by-side display of 36-month monthly billing history alongside 24-hour diurnal load shapes.", space=6)
add_bullet(tf, "TreeSHAP Waterfall Cards", "Interactive feature contribution waterfall showing exactly why the consumer was flagged.", space=8)
add_bullet(tf, "Live Counterfactual Testing", "Admin workbench allowing engineers to simulate load shifts and test model sensitivity.", space=8)

add_card(s15, Inches(8.76), Inches(1.9), Inches(3.773), h3)
tb = s15.shapes.add_textbox(Inches(8.96), Inches(2.1), Inches(3.373), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "3. ENFORCEMENT DISPATCH"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_ORANGE
add_bullet(tf, "Revenue Recovery Ranker", "Rank-orders field raids by expected financial recovery: Recoverable_PKR = P_theft * Deficit_kWh * Tariff.", space=6)
add_bullet(tf, "Geospatial Crew Routing", "Clusters nearby high-risk transformers to optimize inspector patrol routes and fuel efficiency.", space=8)
add_bullet(tf, "One-Click Dispatch", "Triggers automated Roman Urdu SMS dispatch and logs immutable audit trails.", space=8)

set_speaker_notes(s15,
    "We packaged this intelligence into Istikshaf Grid Noir—a tactical, dark-mode desktop command center engineered specifically for utility operations. Designed on an information-dense 12-column grid, it allows dispatchers to monitor transformer health, interact with our 3D grid digital twin, inspect consumer histories, and trigger enforcement raids with a single click.",
    "Q: How fast does the UI load on large consumer databases?\nA: The UI utilizes client-side virtualized tables and streaming JSON pagination, ensuring sub-100ms render speeds even on 100,000+ consumer records."
)

# =========================================================================
# SLIDE 16: Fiscal Impact, DISCO ROI & The Sovereign Verdict
# =========================================================================
s16 = prs.slides.add_slide(blank_layout)
apply_background(s16)
add_header(s16, "Business Case & Verdict", "Unlocking Billions: The DISCO ROI Model & Sovereign Impact", "Transforming utility balance sheets and securing Pakistan's energy future")

add_card(s16, Inches(0.8), Inches(1.85), Inches(5.2), Inches(5.0))
tb = s16.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.8), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "FINANCIAL MODEL & SOVEREIGN VERDICT"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "PKR 14.2 Billion / Year", "Projected net recoverable revenue per major DISCO (LESCO scale: 3.5M consumers) through targeted detection and retroactive recovery.", space=4)
add_bullet(tf, "19.3x Raid Efficiency", "Hit rate surges from 3.6% to 69.7%, slashing vehicle fuel and wasted inspector hours by over 80%.", space=6)
add_bullet(tf, "< 45 Days Payback Period", "Software deployment costs recovered within the first 6 weeks of active operational raids.", space=6)
add_bullet(tf, "National Sovereign Impact", "Scaling across all 10 DISCOs recovers an estimated PKR 140+ Billion annually, directly cutting Circular Debt by 5% yearly.", space=6)
add_bullet(tf, "Deployment-Ready Platform", "Audited, physics-grounded, and ready for 90-day pilot deployment on high-loss 11kV feeders.", space=6)
add_bullet(tf, "The Engineering Team", "Hadiah Batool, Hashim Khushal Khan, Hamza Sultan, Huda Ali.", space=6, color=C_CYAN)

# Right Column: Chart
s16.shapes.add_picture('charts/roi_recovery.png', Inches(6.3), Inches(1.85), width=Inches(6.233))

set_speaker_notes(s16,
    "Let's conclude with economics. Today, DISCO inspection teams spend millions finding theft on barely 3 out of every 100 raids. With Istikshaf, 7 out of 10 raids catch verified theft. For a utility like LESCO, this translates to over 14 Billion Rupees in annual revenue recovery with a payback period of under 45 days. Scaled across Pakistan, this recovers 140 Billion Rupees annually and directly breaks the Circular Debt spiral. Istikshaf is ready for deployment. Thank you.",
    "Q: What are the immediate next steps to deploy in a utility?\nA: Phase 1: 90-day pilot deployment on 5 high-loss 11kV feeders in LESCO (Lahore). Phase 2: Integration with DISCO CIS/billing databases. Phase 3: Nationwide scaling across all 10 DISCO jurisdictions."
)

output_pptx = "Istikshaf_Executive_Presentation.pptx"
prs.save(output_pptx)
print(f"Presentation with 16 expanded slides saved successfully to '{output_pptx}'.")
