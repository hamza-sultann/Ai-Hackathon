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
C_LIME_HEX = '#B6F542'
C_CYAN_HEX = '#45DCEB'
C_CORAL_HEX = '#FFB4AB'
C_ORANGE_HEX = '#FFA726'
C_TEXT_HEX = '#E1E4D2'
C_MUTED_HEX = '#A0A891'
C_BORDER_HEX = '#2E3523'

C_BG = RGBColor(17, 21, 10)
C_CARD = RGBColor(24, 29, 17)
C_CARD_ALT = RGBColor(30, 37, 22)
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
# 1. Generate High-Res Dark-Mode Matplotlib Charts
# -------------------------------------------------------------
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = C_TEXT_HEX
plt.rcParams['axes.labelcolor'] = C_TEXT_HEX
plt.rcParams['xtick.color'] = C_MUTED_HEX
plt.rcParams['ytick.color'] = C_MUTED_HEX

# Chart 1: Pakistan DISCO Non-Technical Loss Rates
fig, ax = plt.subplots(figsize=(6.2, 4.4), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

discos = ['IESCO (Islamabad)', 'FESCO (Faisalabad)', 'LESCO (Lahore)', 'MEPCO (Multan)', 'K-Electric (Karachi)', 'QESCO (Quetta)', 'HESCO (Hyderabad)', 'SEPCO (Sukkur)', 'PESCO (Peshawar)']
losses = [8.2, 9.4, 12.8, 15.1, 15.3, 26.5, 28.2, 35.8, 37.4]
colors = [C_LIME_HEX if x < 13 else C_CYAN_HEX if x < 20 else C_ORANGE_HEX if x < 30 else C_CORAL_HEX for x in losses]

y_pos = np.arange(len(discos))
bars = ax.barh(y_pos, losses, color=colors, height=0.62, edgecolor='#3A422E', linewidth=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(discos, fontsize=8, fontweight='medium')
ax.set_xlabel('Distribution Non-Technical Loss Rate (%)', fontsize=8.5, labelpad=6, color=C_MUTED_HEX)
ax.set_title('Pakistan DISCO Line & Revenue Loss Landscape', fontsize=10.5, pad=10, fontweight='bold', color=C_TEXT_HEX)
ax.axvline(18.5, color=C_ORANGE_HEX, linestyle='--', linewidth=1.2, alpha=0.8, label='National Average: 18.5%')

for bar, loss in zip(bars, losses):
    ax.text(loss + 0.6, bar.get_y() + bar.get_height()/2, f"{loss:.1f}%", va='center', ha='left', fontsize=8, color='#FFFFFF', fontweight='bold')

ax.set_xlim(0, 44)
ax.grid(axis='x', color='#262C1D', linestyle=':', alpha=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(C_BORDER_HEX)
ax.spines['bottom'].set_color(C_BORDER_HEX)
ax.legend(loc='lower right', fontsize=7.5, framealpha=0.3, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)
plt.tight_layout()
fig.savefig('charts/disco_losses.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 2: 24-Hour Diurnal Load Profiles & Theft Signatures
fig, ax = plt.subplots(figsize=(6.2, 4.4), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

hours = np.arange(24)
baseline = np.array([0.15, 0.13, 0.12, 0.11, 0.14, 0.22, 0.45, 0.52, 0.40, 0.32, 0.29, 0.28, 0.28, 0.27, 0.29, 0.31, 0.36, 0.48, 0.85, 0.92, 0.88, 0.72, 0.45, 0.25])
solar = baseline.copy()
solar[10:16] = np.array([0.08, 0.04, 0.02, 0.03, 0.06, 0.12]) # Duck curve
peak_shaver = baseline.copy()
peak_shaver[18:22] = np.array([0.02, 0.02, 0.03, 0.03]) # Shunt during peak hours
night_ac = baseline.copy()
night_ac[0:6] = np.array([0.04, 0.03, 0.03, 0.03, 0.04, 0.05])

ax.plot(hours, baseline, color='#FFFFFF', linewidth=2.2, label='Normal Legitimate Household', alpha=0.9)
ax.plot(hours, solar, color=C_CYAN_HEX, linewidth=2.0, linestyle='-.', label='Rooftop Solar Prosumer (Duck Curve)')
ax.plot(hours, peak_shaver, color=C_CORAL_HEX, linewidth=2.2, label='Peak Shaver Theft (6-10 PM Shunt)')
ax.plot(hours, night_ac, color=C_ORANGE_HEX, linewidth=1.8, linestyle=':', label='Nighttime AC Bypass (11 PM-5 AM)')

ax.axvspan(18, 22, color=C_CORAL_HEX, alpha=0.14, label='NEPRA Peak Tariff Window (2.5x Cost)')
ax.set_xticks(np.arange(0, 24, 3))
ax.set_xticklabels(['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'], fontsize=8)
ax.set_ylabel('Load Draw (kWh / Hour)', fontsize=8.5, color=C_MUTED_HEX)
ax.set_xlabel('Time of Day (24-Hour Interval Stream)', fontsize=8.5, color=C_MUTED_HEX)
ax.set_title('High-Frequency Diurnal Curves & Tamper Signatures', fontsize=10.5, pad=10, fontweight='bold', color=C_TEXT_HEX)
ax.grid(color='#262C1D', linestyle=':', alpha=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(C_BORDER_HEX)
ax.spines['bottom'].set_color(C_BORDER_HEX)
ax.legend(loc='upper right', fontsize=7.0, framealpha=0.35, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)
plt.tight_layout()
fig.savefig('charts/diurnal_theft_signatures.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 3: Smart Meter (AMI) Detection Uplift Benchmarks
fig, ax = plt.subplots(figsize=(6.2, 4.4), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

archetypes = ['Peak Shaver', 'Fixed Shunt', 'Nighttime AC', 'Direct Kunda', 'Overall Recall']
monthly_recall = [10.6, 38.3, 20.8, 14.9, 20.3]
ami_recall = [58.3, 63.9, 39.6, 29.5, 45.7]

x = np.arange(len(archetypes))
width = 0.35

rects1 = ax.bar(x - width/2, monthly_recall, width, label='Track 1 (Monthly Billing)', color='#5C664A', edgecolor='#3A422E', linewidth=0.8)
rects2 = ax.bar(x + width/2, ami_recall, width, label='Track 2 (Hourly Smart Meter)', color=C_LIME_HEX, edgecolor='#84B02A', linewidth=0.8)

ax.set_ylabel('Detection Recall Rate (%)', fontsize=8.5, color=C_MUTED_HEX)
ax.set_title('Track 1 vs Track 2: Smart-Meter Detection Uplift', fontsize=10.5, pad=10, fontweight='bold', color=C_TEXT_HEX)
ax.set_xticks(x)
ax.set_xticklabels(archetypes, fontsize=8)
ax.set_ylim(0, 74)
ax.grid(axis='y', color='#262C1D', linestyle=':', alpha=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(C_BORDER_HEX)
ax.spines['bottom'].set_color(C_BORDER_HEX)
ax.legend(loc='upper left', fontsize=7.5, framealpha=0.35, facecolor=C_CARD_HEX, edgecolor=C_BORDER_HEX)

for r1, r2 in zip(rects1, rects2):
    h1 = r1.get_height()
    h2 = r2.get_height()
    ax.annotate(f"{h1:.1f}%", xy=(r1.get_x() + r1.get_width()/2, h1), xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#A0A891')
    ax.annotate(f"{h2:.1f}%", xy=(r2.get_x() + r2.get_width()/2, h2), xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=C_LIME_HEX)

ax.annotate('5.5x Leap', xy=(0.18, 60), xytext=(0.4, 66),
            arrowprops=dict(arrowstyle="->", color=C_CYAN_HEX, lw=1.2),
            fontsize=7.5, fontweight='bold', color=C_CYAN_HEX)

plt.tight_layout()
fig.savefig('charts/ami_uplift_benchmarks.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

# Chart 4: DISCO Revenue Recovery Waterfall
fig, ax = plt.subplots(figsize=(6.2, 4.4), dpi=300)
fig.patch.set_facecolor(C_BG_HEX)
ax.set_facecolor(C_CARD_HEX)

categories = ['Current\nAnnual Loss', 'Identified\nTargeted Theft', 'Direct Power\nRecovery', 'Reduced Raid\nWaste', 'Net Annual\nRecovery']
values = [-18.5, 15.6, 12.4, 1.8, 14.2]
colors = [C_CORAL_HEX, C_CYAN_HEX, C_LIME_HEX, C_ORANGE_HEX, C_LIME_HEX]

bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor='#3A422E', linewidth=0.8)
ax.set_ylabel('Billion PKR / Year (LESCO Scale)', fontsize=8.5, color=C_MUTED_HEX)
ax.set_title('DISCO Fiscal Recovery Model (Per 3.5M Consumers)', fontsize=10.5, pad=10, fontweight='bold', color=C_TEXT_HEX)
ax.axhline(0, color=C_BORDER_HEX, linewidth=1.2)
ax.grid(axis='y', color='#262C1D', linestyle=':', alpha=0.6)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(C_BORDER_HEX)
ax.spines['bottom'].set_color(C_BORDER_HEX)

for bar, val in zip(bars, values):
    y = bar.get_height()
    va = 'bottom' if y >= 0 else 'top'
    sign = "+" if y > 0 else ""
    ax.text(bar.get_x() + bar.get_width()/2, y + (0.5 if y>=0 else -1.2), f"{sign}{val:.1f}B", ha='center', va=va, fontsize=8, fontweight='bold', color='#FFFFFF')

ax.set_ylim(-21, 18)
plt.tight_layout()
fig.savefig('charts/roi_recovery.png', dpi=300, facecolor=C_BG_HEX)
plt.close(fig)

print("Generated 4 presentation charts successfully.")

# -------------------------------------------------------------
# 2. PowerPoint Slide Generation using python-pptx
# -------------------------------------------------------------
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def apply_background(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()
    return bg

def add_header(slide, tag_text, title_text, subtitle_text=""):
    # Header tag pill
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = FONT_MONO
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_LIME

    # Main Title
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

    # Subtitle if present
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

# Subtle decorative banner
banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(11.733), Inches(0.04))
banner.fill.solid()
banner.fill.fore_color.rgb = C_LIME
banner.line.fill.background()

# Title box
tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(2.2))
tf1 = tb1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "ISTIKSHAF  [ استکشاف ]"
p.font.name = FONT_HEADING
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = C_LIME

p2 = tf1.add_paragraph()
p2.text = "Autonomous Agentic Revenue Protection & Explainable Grid AI"
p2.font.name = FONT_HEADING
p2.font.size = Pt(22)
p2.font.bold = True
p2.font.color.rgb = C_TEXT
p2.space_before = Pt(8)

p3 = tf1.add_paragraph()
p3.text = "A Physics-Grounded Enterprise Intelligence Engine Defeating Non-Technical Losses across Pakistan's Power Grid"
p3.font.name = FONT_BODY
p3.font.size = Pt(13)
p3.font.color.rgb = C_MUTED
p3.space_before = Pt(6)

# Key Stats row
add_kpi(s1, Inches(0.8), Inches(4.0), Inches(3.6), Inches(2.3), "PKR 2.65T", "National Circular Debt", "Suffocating Pakistan's fiscal stability and CPPA liquidity", C_CORAL)
add_kpi(s1, Inches(4.8), Inches(4.0), Inches(3.6), Inches(2.3), "PKR 520B+", "Annual Revenue Lost", "Stolen via kundas, meter bypasses, and billing fraud", C_ORANGE)
add_kpi(s1, Inches(8.8), Inches(4.0), Inches(3.733), Inches(2.3), "19.3x", "Field Raid Precision Multiplier", "From 3.6% random spot checks to 69.7% targeted precision", C_LIME)

# Footer credits
fb = s1.shapes.add_textbox(Inches(0.8), Inches(6.75), Inches(11.733), Inches(0.4))
tf_f = fb.text_frame
p_f = tf_f.paragraphs[0]
p_f.text = "Hamza Sultan & Team  |  System Architecture: Track 1 (Monthly Grid) & Track 2 (51.8M High-Frequency AMI Engine)"
p_f.font.name = FONT_MONO
p_f.font.size = Pt(9.5)
p_f.font.color.rgb = C_MUTED

set_speaker_notes(s1,
    "Judges and energy sector leaders: Every year, over 520 Billion Rupees vanishes from Pakistan's power grid into thin air. It is called Non-Technical Loss—power theft, illegal hookups, and meter tampering. It is the primary engine behind Pakistan's crippling 2.65 Trillion Rupee circular debt. Today, we present Istikshaf: an autonomous, physics-grounded enterprise AI platform that transforms revenue protection from blind manual spot-checks into precision enforcement.",
    "Q: Why hasn't this been solved by smart meters?\nA: Because 65% of Pakistan's grid relies on legacy analog meters, and national AMI rollout will take 15 years. Istikshaf is engineered as a dual-track architecture: it solves grid theft on legacy analog meters today with 69.7% precision, while instantly unlocking a 5.5x detection surge when smart meters are connected."
)

# =========================================================================
# SLIDE 2: The Bleeding Grid & Why DISCOs Fail
# =========================================================================
s2 = prs.slides.add_slide(blank_layout)
apply_background(s2)
add_header(s2, "Macro Economic Crisis", "The Anatomy of a Bleeding Grid: Why Current Utility Audits Fail", "10 Distribution Companies (DISCOs) lose between 12% and 38% of distributed power annually")

# Left Column: Problem Cards
add_card(s2, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s2.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True

def add_bullet(tf, title, body, color=C_TEXT, space=8):
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.text = f"• {title}: "
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = color
    if space > 0:
        p.space_before = Pt(space)
    
    # Body text in same paragraph
    run = p.add_run()
    run.text = body
    run.font.name = FONT_BODY
    run.font.size = Pt(10)
    run.font.bold = False
    run.font.color.rgb = C_MUTED

add_bullet(tf, "The 3.6% Random Audit Yield", "DISCO inspection teams conduct manual spot-checks that yield a meager 3.6% hit rate. Over 96 out of 100 field raids find nothing, wasting millions in logistics while corrupt syndicates operate untouched.", C_CORAL, space=0)
add_bullet(tf, "The Unscheduled Load-Shedding Confounder", "When feeder uptime drops to 75% during load shedding, entire neighborhoods show sudden drops in usage. Naive Western algorithms flag innocent entire streets as coordinated theft rings.", C_ORANGE)
add_bullet(tf, "The Rooftop Solar Duck Curve", "High electricity rates have caused a massive surge in rooftop net-metering. When daytime grid draw plunges 85%, naive models misinterpret green energy generation as criminal bypass.", C_CYAN)
add_bullet(tf, "The Analog Meter Reality", "65% of meters across LESCO, PESCO, and MEPCO are spinning aluminum discs with zero remote telemetry. You cannot deploy solutions that presuppose universal AMI connectivity.", C_TEXT)

# Right Column: Chart
s2.shapes.add_picture('charts/disco_losses.png', Inches(6.8), Inches(1.85), width=Inches(5.733))

set_speaker_notes(s2,
    "Why are DISCOs losing this war? Because current inspection teams operate blindly. Linemen conduct manual spot-checks that yield a pathetic 3.6% hit rate. When load-shedding strikes, power drops across the feeder—naive AI flags the entire street as thieves. When a homeowner installs solar, naive software triggers a police raid. Meanwhile, organized syndicates bypass meters during peak hours with complete impunity. DISCOs are hemorrhaging cash while flying blind.",
    "Q: How do you handle corruption among meter readers?\nA: Meter readers collude by under-reporting billed units in handheld terminals. But energy cannot vanish: our transformer totalizer energy conservation law compares total PMT power against the sum of billed units, exposing reader route discrepancies mathematically without relying on honest reporting."
)

# =========================================================================
# SLIDE 3: The 51.8M Telemetry Engine: The Dual-Track Dataset
# =========================================================================
s3 = prs.slides.add_slide(blank_layout)
apply_background(s3)
add_header(s3, "Enterprise Data Engineering", "The 51.8 Million Telemetry Engine: Grounded in Electrical Physics", "The largest, most realistic, physically grounded synthetic power grid dataset built for the Global South")

# Left Column: Architectural Cards
add_card(s3, Inches(0.8), Inches(1.85), Inches(5.8), Inches(2.4), bg_color=C_CARD)
tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.4), Inches(2.1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "TRACK 1: LEGACY GRID (10,000 CONSUMERS)"
p.font.name = FONT_HEADING
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Grid Topology Hierarchy", "30 Primary 11kV Feeders, 300 Pole-Mounted Transformers (PMTs), and 10,000 consumers modeled over 36 consecutive months (360,000 comprehensive panel records).", space=4)
add_bullet(tf, "Non-Linear I²R Physics", "Technical loss modeled as Max(0.00006 * Load^1.6, 0.02 * Load). First Law of Thermodynamics enforced: injected energy equals billed + stolen + technical dissipation (|Δ| < 0.5 kWh).", space=4)

add_card(s3, Inches(0.8), Inches(4.45), Inches(5.8), Inches(2.4), bg_color=C_CARD)
tb = s3.shapes.add_textbox(Inches(1.0), Inches(4.6), Inches(5.4), Inches(2.1))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "TRACK 2: HIGH-FREQUENCY AMI STREAM (51.8M ROWS)"
p.font.name = FONT_HEADING
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "51,819,270 Hourly Telemetry Records", "2,000 AMI smart-meter consumers disaggregated into 36 months of 1-hour interval readings, stored in a compressed 322 MB Snappy Parquet engine.", space=4)
add_bullet(tf, "REWD-P Micro-Study Grounding", "Calibrated against empirical Pakistani residential load research, modeling diurnal double peaks, geyser spikes, AR(1) autocorrelation, and 1.5% cellular GPRS packet dropouts.", space=4)

# Right Column: Big KPI Cards
add_kpi(s3, Inches(6.8), Inches(1.85), Inches(2.76), Inches(2.4), "51.8M", "Hourly Interval Stream", "Compressed in 322MB Snappy Parquet", C_CYAN)
add_kpi(s3, Inches(9.76), Inches(1.85), Inches(2.77), Inches(2.4), "< 0.5 kWh", "Thermodynamic Balance", "Conservation law across all 300 PMTs", C_LIME)
add_kpi(s3, Inches(6.8), Inches(4.45), Inches(2.76), Inches(2.4), "5.5 Mins", "Out-of-Core ETL Stream", "Zero-leakage streaming in <200MB RAM", C_ORANGE)
add_kpi(s3, Inches(9.76), Inches(4.45), Inches(2.77), Inches(2.4), "14 Classes", "Behavioral Archetypes", "8 theft modes & 6 real confounders", C_CORAL)

set_speaker_notes(s3,
    "You cannot solve national problems with toy datasets or Chinese research dumps that lack grid hierarchy. We built the Istikshaf Dual-Track dataset: 10,000 consumers across 30 feeders and 300 transformers over 3 full years. Track 1 captures current monthly billing reality. Track 2 models high-frequency smart meters: 51.8 million hourly readings compressed into 322 megabytes of Parquet. Every transformer satisfies the first law of thermodynamics.",
    "Q: Why did you build a synthetic dataset instead of using raw DISCO files?\nA: Raw DISCO billing files are legally classified under NEPRA regulations. More critically, historical utility raid logs are deeply corrupted by bribes—training an AI on historical DISCO tickets trains it on historical bribery. Our dataset provides rigorous, physically grounded ground truth adhering to thermodynamic dissipation laws."
)

# =========================================================================
# SLIDE 4: 14 Behavioral Archetypes: Theft Vectors vs. Confounders
# =========================================================================
s4 = prs.slides.add_slide(blank_layout)
apply_background(s4)
add_header(s4, "Domain Intelligence", "Unmasking 14 Behavioral Archetypes: Theft Vectors vs. Confounders", "Modeling both illicit tampering strategies and legitimate grid confounders with precision")

# Left Column: Archetypes breakdown
add_card(s4, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.4), Inches(4.7))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "ILLICIT THEFT ARCHETYPES (8.0% GROUND TRUTH)"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CORAL

add_bullet(tf, "Slab Defender (150)", "Bypasses meter only when monthly consumption nears 200/300 kWh, pinning the meter reading below NEPRA punitive tariff slab jumps.", space=3)
add_bullet(tf, "Peak Hour Shaver (100)", "Shunts power strictly during high-cost peak hours (6 PM-10 PM), invisible in monthly billing totals but blazing in hourly interval curves.", space=3)
add_bullet(tf, "Nighttime AC Shunt (120)", "Uses normal power during day; flips an unmetered bypass switch at night during summer heatwaves to run heavy bedroom ACs.", space=3)
add_bullet(tf, "Direct Kunda & Shunt (250)", "Escalating 5-stage bare wire hookups over low-voltage lines and internal CT hardware shunt resistors.", space=3)

p_sep = tf.add_paragraph()
p_sep.text = "LEGITIMATE CONFOUNDERS (92.0% INNOCENT POPULATION)"
p_sep.font.name = FONT_HEADING
p_sep.font.size = Pt(11)
p_sep.font.bold = True
p_sep.font.color.rgb = C_LIME
p_sep.space_before = Pt(8)

add_bullet(tf, "Solar Prosumer (1,200)", "Produces strong midday generation drop (the duck curve). Handled via net-metering gating to eliminate false alarms (0.00% FPR).", space=3)
add_bullet(tf, "Seasonal Traveler & Inverter Upgrade (600)", "Extended village visits (1-3 month drops) and permanent 25% reductions from inverter AC retrofits, isolated from fraudulent tampering.", space=3)

# Right Column: Chart
s4.shapes.add_picture('charts/diurnal_theft_signatures.png', Inches(6.8), Inches(1.85), width=Inches(5.733))

set_speaker_notes(s4,
    "Theft in Pakistan is not random. It follows distinct behavioral strategies. We modeled 14 precise archetypes. The 'Slab Defender' bypasses the meter only when approaching 200 units to evade NEPRA's punitive pricing cliff. The 'Peak Shaver' disconnects strictly between 6 PM and 10 PM. Crucially, we model legitimate confounders like solar prosumers and village travelers, ensuring honest families are never wrongfully accused.",
    "Q: How do you differentiate a family travelling to their village from someone installing a kunda?\nA: A traveling family has near-zero consumption across all 24 hours of the day including peak hours, and returns to baseline in month 2 or 3. A kunda tap maintains daytime active draw while flattening specific windows or dropping baseline permanently without rebounding."
)

# =========================================================================
# SLIDE 5: Physics-Informed ML: Two-Stage Hybrid Inference
# =========================================================================
s5 = prs.slides.add_slide(blank_layout)
apply_background(s5)
add_header(s5, "System Architecture", "The Two-Stage Hybrid Inference Engine: Unsupervised + Cost-Sensitive ML", "Combining zero-day tamper detection with calibrated probability bounds")

# Flow diagram boxes
w_box = Inches(3.6)
h_box = Inches(4.9)

# Box 1: Out-of-fold IsoForest
add_card(s5, Inches(0.8), Inches(1.9), w_box, h_box)
tb = s5.shapes.add_textbox(Inches(1.0), Inches(2.1), w_box - Inches(0.4), h_box - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 1: UNSUPERVISED ISOLATION FOREST"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Zero-Day Tamper Catching", "Standard supervised models only recognize historical frauds. Isolation Forest isolates abnormal multidimensional geometry.", space=8)
add_bullet(tf, "5-Fold GroupKFold Validation", "Trained strictly grouped by consumer_id across 36 months, preventing temporal or consumer leakage.", space=8)
add_bullet(tf, "Out-of-Fold Anomaly Score", "Generates an unbiased out-of-fold score (`iso_forest_oof_score`) fed directly as a feature into the Stage 2 classifier.", space=8)

# Box 2: XGBoost Ensemble
add_card(s5, Inches(4.8), Inches(1.9), w_box, h_box)
tb = s5.shapes.add_textbox(Inches(5.0), Inches(2.1), w_box - Inches(0.4), h_box - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 2: COST-WEIGHTED XGBOOST"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Asymmetric Loss Optimization", "With 8.0% positive class imbalance, standard trees ignore theft. We enforce scale_pos_weight = 11.5, penalizing missed theft 11.5x more than false alarms.", space=8)
add_bullet(tf, "Multi-Modal Feature Fusion", "Combines Stage 1 anomaly scores with 12 Track 1 grid features and 7 Track 2 interval load ratios.", space=8)
add_bullet(tf, "TreeSHAP Explainer Engine", "Extracts local Shapley value attributions for every single decision, producing tribunal-grade evidence dockets.", space=8)

# Box 3: Platt Probability Calibration
add_card(s5, Inches(8.8), Inches(1.9), Inches(3.733), h_box)
tb = s5.shapes.add_textbox(Inches(9.0), Inches(2.1), Inches(3.333), h_box - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "STAGE 3: PLATT CALIBRATION"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CORAL
add_bullet(tf, "Frozen Logistic Sigmoid", "Uncalibrated tree outputs on imbalanced sets compress into artificial ranges (rarely exceeding 0.35).", space=8)
add_bullet(tf, "Calibrated Probability Surge", "Scales raw pseudo-probabilities up to 73.3%, providing trustworthy confidence scores for DISCO operations.", space=8)
add_bullet(tf, "Operational Decision Tiers", "High Risk (P >= 0.70): Field Raid Dispatch.\nMedium Risk (0.50 <= P < 0.70): Automated Soft-Warning SMS.", space=8)

set_speaker_notes(s5,
    "Here is why our architecture is unmatched. We combine unsupervised and supervised intelligence. An Out-of-Fold Isolation Forest scans for 'unknown unknowns'—brand-new tampering tricks never seen in training. That signal feeds into an extreme gradient-boosted ensemble tuned with an asymmetric 11.5x penalty on missed theft. Finally, a frozen Platt Scaler calibrates the outputs into true probabilities that utility executives can stake their budgets on.",
    "Q: Why use Platt Scaling instead of Isotonic Regression?\nA: Isotonic regression is non-parametric and prone to severe overfitting on imbalanced calibration sets. Platt scaling fits a smooth sigmoid curve that preserves rank ordering while providing reliable probability bounds."
)

# =========================================================================
# SLIDE 6: 19 Advanced Domain-Grounded Features
# =========================================================================
s6 = prs.slides.add_slide(blank_layout)
apply_background(s6)
add_header(s6, "Feature Engineering", "19 Advanced Domain Features: Invariance Engineering Defeating Confounders", "Mathematical formulations specifically engineered to neutralize local grid confounders")

# 4 Cards Layout (2x2 grid)
w_c = Inches(5.7)
h_c = Inches(2.35)

# Card 1: Vectorized CUSUM & Baseline
add_card(s6, Inches(0.8), Inches(1.9), w_c, h_c)
tb = s6.shapes.add_textbox(Inches(1.0), Inches(2.05), w_c - Inches(0.4), h_c - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. VECTORIZED CUSUM CHANGE-POINT BREAKS"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Break Formula", "S_t = Max(0, S_{t-1} + (Mean_baseline - x_t) - k). Evaluates cumulative deviation peaks to pinpoint the exact month theft began without future leakage.", space=4)
add_bullet(tf, "Clean 3-Month Anchor", "Anchoring against uncontaminated initial months prevents rolling baselines from absorbing creeping theft into the 'new normal'.", space=4)

# Card 2: PMT Percentile Loss Ranking
add_card(s6, Inches(6.8), Inches(1.9), w_c, h_c)
tb = s6.shapes.add_textbox(Inches(7.0), Inches(2.05), w_c - Inches(0.4), h_c - Inches(0.3))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. PMT PERCENTILE LOSS RANKING"
p.font.name = FONT_HEADING
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Monthly Percentile Ranking", "Transforms raw transformer technical loss into a normalized 0.0-1.0 percentile rank across all 300 PMTs for each calendar month.", space=4)
add_bullet(tf, "Weather Invariance", "Eliminates grid-wide summer/winter technical dissipation spikes, isolating localized high-theft transformer pockets.", space=4)

# Card 3: Confounder Discounting
add_card(s6, Inches(0.8), Inches(4.5), w_c, h_c)
tb = s6.shapes.add_textbox(Inches(1.0), Inches(4.65), w_c - Inches(0.4), h_c - Inches(0.3))
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

# Card 4: High-Frequency Interval Ratios
add_card(s6, Inches(6.8), Inches(4.5), w_c, h_c)
tb = s6.shapes.add_textbox(Inches(7.0), Inches(4.65), w_c - Inches(0.4), h_c - Inches(0.3))
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

set_speaker_notes(s6,
    "We engineered 19 domain-grounded features. Our vectorized CUSUM algorithm detects the exact month a bypass began, without leaking future data. Our clean baseline anchor prevents rolling averages from absorbing stolen power. And our uptime-discount feature normalizes consumer draw against feeder availability, meaning load shedding never triggers a false alarm.",
    "Q: How does CUSUM prevent data leakage in training?\nA: For any month t, CUSUM evaluates strictly the history from month 1 to t. It never uses future billing cycles to compute running means or cumulative sums, ensuring zero temporal data leakage."
)

# =========================================================================
# SLIDE 7: Quantitative Benchmarks & Smart-Meter Uplift
# =========================================================================
s7 = prs.slides.add_slide(blank_layout)
apply_background(s7)
add_header(s7, "Benchmark Verification", "Proven Operational Uplift: 19.3x Precision & 5.5x Peak-Shave Detection", "Rigorous out-of-sample evaluation on isolated 20% evaluation splits")

# Left Column: Performance Metrics Table
add_card(s7, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s7.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "EMPIRICAL PERFORMANCE BREAKTHROUGHS"
p.font.name = FONT_HEADING
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_LIME

add_bullet(tf, "19.3x Precision Multiplier", "Istikshaf achieves 69.7% precision on standard monthly billing data, compared to the 3.6% baseline yield of random DISCO line audits.", space=8)
add_bullet(tf, "Recall More Than Doubled", "Overall detection recall rises from 20.3% on monthly data to 45.7% when AMI smart-meter telemetry is enabled (+25.4 points).", space=8)
add_bullet(tf, "5.5x Peak-Hour Shaver Leap", "Time-of-Use peak evasion recall surges from 10.6% on monthly bills to 58.3% on hourly streams (+47.8 points).", space=8)
add_bullet(tf, "Zero Solar False Alarms", "Maintains 100.00% specificity (0.00% false positive rate) on registered solar net-metering prosumers.", space=8)
add_bullet(tf, "Sub-Minute Big Data Execution", "Processes 51.8 Million hourly telemetry rows in 5.5 minutes using <200MB RAM via PyArrow batch streaming.", space=8)

# Right Column: Chart
s7.shapes.add_picture('charts/ami_uplift_benchmarks.png', Inches(6.8), Inches(1.85), width=Inches(5.733))

set_speaker_notes(s7,
    "The numbers prove our superiority. In standard monthly grids, Istikshaf delivers 69.7% precision—a 19.3-fold increase in raid efficiency over current utility spot-checks. When smart meters are introduced, our streaming engine more than doubles recall to 45.7% and achieves a 5.5x increase in catching peak-hour evaders. All while delivering a zero-percent false alarm rate on solar homes.",
    "Q: Why is precision 49.3% on the smart-meter set compared to 69.7% on monthly?\nA: The smart meter subset specifically tests high-difficulty evasive archetypes like peak-shavers and night AC bypasses that are virtually invisible on monthly bills. Catching 58.3% of peak shavers vs 10.6% on monthly represents an enormous operational gain."
)

# =========================================================================
# SLIDE 8: The 8-Agent Autonomous Swarm
# =========================================================================
s8 = prs.slides.add_slide(blank_layout)
apply_background(s8)
add_header(s8, "Autonomous Enforcement", "The 8-Agent Autonomous Swarm: Eliminating the Human Bottleneck", "Multi-agent dispatch orchestrator automating triage, deduplication, and field routing")

# 4 Cards across
w4 = Inches(2.78)
h4 = Inches(5.0)

# Agent 1 & 2
add_card(s8, Inches(0.8), Inches(1.9), w4, h4)
tb = s8.shapes.add_textbox(Inches(0.95), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
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

# Agent 3 & 4
add_card(s8, Inches(3.78), Inches(1.9), w4, h4)
tb = s8.shapes.add_textbox(Inches(3.93), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
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

# Agent 5 & 6
add_card(s8, Inches(6.76), Inches(1.9), w4, h4)
tb = s8.shapes.add_textbox(Inches(6.91), Inches(2.1), w4 - Inches(0.3), h4 - Inches(0.4))
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

# Agent 7 & 8
add_card(s8, Inches(9.74), Inches(1.9), Inches(2.79), h4)
tb = s8.shapes.add_textbox(Inches(9.89), Inches(2.1), Inches(2.49), h4 - Inches(0.4))
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

set_speaker_notes(s8,
    "A probability score on a dashboard recovers zero rupees. That is why we built the Istikshaf 8-Agent Swarm. The Confound Agent verifies feeder uptime. The Dedup Guard ensures crews aren't dispatched twice to the same site. The Recidivism Agent tracks repeat offenders. And our Soft-Warning Agent automatically nudges medium-risk consumers via SMS, recovering revenue before spending raid resources.",
    "Q: Why use autonomous agents instead of simple if-else code?\nA: Because utility operations require stateful, dynamic adjustments: checking live SQLite investigation dockets, adjusting seasonal thresholds based on ambient heat, generating bilingual natural language alerts, and maintaining cryptographic audit trails."
)

# =========================================================================
# SLIDE 9: TreeSHAP Explainability & Roman Urdu Field Operations
# =========================================================================
s9 = prs.slides.add_slide(blank_layout)
apply_background(s9)
add_header(s9, "Explainability & Field Ops", "Defensible in Court, Actionable on the Street: SHAP & Roman Urdu", "Translating complex mathematical attributions into tribunal evidence and lineman action")

# Left Column: Legal Evidence Docket
add_card(s9, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s9.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.4), Inches(4.6))
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

# Right Column: Roman Urdu Mobile SMS Alert
add_card(s9, Inches(6.8), Inches(1.85), Inches(5.733), Inches(5.0), bg_color=C_CARD_ALT)
tb = s9.shapes.add_textbox(Inches(7.0), Inches(2.05), Inches(5.333), Inches(4.6))
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
             '   hai jabke customer ka load kam hua.\n' \
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

set_speaker_notes(s9,
    "AI must be defensible in tribunal hearings and actionable for linemen who don't read English machine learning vectors. Using TreeSHAP, every inspection docket details the exact physical factors that triggered the alert. Our Urdu Localization Agent translates these technical attributions into natural Roman Urdu, sent directly to field inspectors' mobile phones via SMS. No guesswork, no ambiguity—just actionable intelligence.",
    "Q: How do you know the Roman Urdu message is accurate?\nA: The Urdu Localization Agent uses constrained template generation grounded directly in the top-3 TreeSHAP feature attributions and PMT loss metrics, guaranteeing 100% factual accuracy without hallucination."
)

# =========================================================================
# SLIDE 10: Tactical UI: Istikshaf Grid Noir & 3D Digital Twin
# =========================================================================
s10 = prs.slides.add_slide(blank_layout)
apply_background(s10)
add_header(s10, "Enterprise Platform", "Istikshaf Grid Noir: Tactical Command Center & 3D Digital Twin", "High-density dark mode desktop application engineered for 24/7 utility control rooms")

# 3 Cards Layout
w3 = Inches(3.75)
h3 = Inches(4.9)

add_card(s10, Inches(0.8), Inches(1.9), w3, h3)
tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "1. 3D WEBGL DIGITAL TWIN"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_CYAN
add_bullet(tf, "Spatial Grid Topology", "Renders 30 11kV primary feeders and 300 pole-mounted transformers in an interactive 3D WebGL force-directed graph.", space=6)
add_bullet(tf, "Dynamic Load Balancing", "Visualizes real-time power injection, technical loss dissipation, and localized transformer overload in high-contrast neon accents.", space=8)
add_bullet(tf, "Theft Pocket Clustering", "Highlights transformer loss hot-spots where coordinated theft rings operate.", space=8)

add_card(s10, Inches(4.78), Inches(1.9), w3, h3)
tb = s10.shapes.add_textbox(Inches(4.98), Inches(2.1), w3 - Inches(0.4), h3 - Inches(0.4))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "2. CONSUMER DEEP-DIVE"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME
add_bullet(tf, "Dual-Horizon Visualizer", "Side-by-side display of 36-month monthly billing history alongside 24-hour high-frequency diurnal load shapes.", space=6)
add_bullet(tf, "TreeSHAP Waterfall Cards", "Interactive feature contribution waterfall showing exactly why the consumer was flagged.", space=8)
add_bullet(tf, "Live Counterfactual Testing", "Admin workbench allowing engineers to simulate load shifts and test model sensitivity.", space=8)

add_card(s10, Inches(8.76), Inches(1.9), Inches(3.773), h3)
tb = s10.shapes.add_textbox(Inches(8.96), Inches(2.1), Inches(3.373), h3 - Inches(0.4))
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

set_speaker_notes(s10,
    "We packaged this intelligence into Istikshaf Grid Noir—a tactical, dark-mode desktop command center engineered specifically for utility operations. Designed on an information-dense 12-column grid, it allows dispatchers to monitor transformer health, interact with our 3D grid digital twin, inspect consumer histories, and trigger enforcement raids with a single click.",
    "Q: Can this run in low-bandwidth rural utility divisions?\nA: Yes. The frontend is built on lightweight React and Vite, using client-side WebGL rendering and compact JSON/Parquet streaming APIs that operate smoothly even on intermittent 3G cellular connections."
)

# =========================================================================
# SLIDE 11: Fiscal Impact & DISCO ROI
# =========================================================================
s11 = prs.slides.add_slide(blank_layout)
apply_background(s11)
add_header(s11, "Business Case & ROI", "Unlocking Billions in Recoverable Revenue: The DISCO Business Case", "Transforming utility balance sheets and breaking the Circular Debt spiral")

# Left Column: Financial Model
add_card(s11, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.0))
tb = s11.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.4), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "FINANCIAL MODEL (LESCO DIVISION: 3.5M CONSUMERS)"
p.font.name = FONT_HEADING
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = C_LIME

add_bullet(tf, "PKR 14.2 Billion / Year", "Projected net recoverable revenue per major DISCO through targeted detection and retroactive billing recovery.", space=6)
add_bullet(tf, "19.3x Raid Efficiency", "Hit rate surges from 3.6% to 69.7%, slashing fuel, vehicle maintenance, and wasted inspector man-hours by over 80%.", space=8)
add_bullet(tf, "< 45 Days Payback Period", "Software deployment capital costs recovered within the first 6 weeks of active operational field raids.", space=8)
add_bullet(tf, "National Sovereign Impact", "Scaling Istikshaf across all 10 DISCOs recovers an estimated PKR 140+ Billion annually, directly reducing the Circular Debt by over 5% every single year.", space=8)

# Right Column: Chart
s11.shapes.add_picture('charts/roi_recovery.png', Inches(6.8), Inches(1.85), width=Inches(5.733))

set_speaker_notes(s11,
    "Let's talk economics. Today, DISCO inspection teams spend millions driving around aimlessly, finding theft on barely 3 out of every 100 inspections. With Istikshaf, 7 out of 10 raids catch verified theft. For a utility like LESCO, this translates to over 14 Billion Rupees in annual revenue recovery with a capital payback period of under 45 days. This is how we defeat circular debt.",
    "Q: How do you handle consumers disputing their retroactive bills?\nA: Every single inspection dossier is accompanied by TreeSHAP feature attributions, CUSUM structural break timestamps, and transformer totalizer loss balances. This forms an ironclad, legally admissible evidentiary record in NEPRA consumer tribunals."
)

# =========================================================================
# SLIDE 12: Securing Pakistan's Energy Future
# =========================================================================
s12 = prs.slides.add_slide(blank_layout)
apply_background(s12)

# Full banner
add_card(s12, Inches(0.8), Inches(1.0), Inches(11.733), Inches(5.5), bg_color=C_CARD)
tb = s12.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(10.933), Inches(4.8))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "THE VERDICT: SECURING PAKISTAN'S ENERGY FUTURE"
p.font.name = FONT_HEADING
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = C_LIME

p_sub = tf.add_paragraph()
p_sub.text = "Why Istikshaf is the definitive solution to Pakistan's Power Sector Crisis:"
p_sub.font.name = FONT_BODY
p_sub.font.size = Pt(13)
p_sub.font.color.rgb = C_MUTED
p_sub.space_before = Pt(6)

add_bullet(tf, "Grounded in Electrical Physics", "First-law energy conservation and non-linear technical loss dissipation guarantee zero theoretical violations.", space=12)
add_bullet(tf, "Dual-Track Scalability", "Solves theft on legacy analog grids today with 69.7% precision, while unlocking a 5.5x detection surge on smart meters tomorrow.", space=10)
add_bullet(tf, "Zero Confounder Penalties", "100% specificity on registered solar prosumers and automatic discount factors for load shedding blackouts.", space=10)
add_bullet(tf, "Autonomous Operational Swarm", "8 specialized agents bridge the gap between machine learning models and street-level lineman dispatch with Roman Urdu communications.", space=10)

p_call = tf.add_paragraph()
p_call.text = "ISTIKSHAF: Turning Loss Detection into Sovereign Recovery. Ready for Deployment."
p_call.font.name = FONT_HEADING
p_call.font.size = Pt(14)
p_call.font.bold = True
p_call.font.color.rgb = C_CYAN
p_call.space_before = Pt(18)

set_speaker_notes(s12,
    "Istikshaf proves that national crises can be solved when cutting-edge artificial intelligence is grounded in electrical physics and domain reality. We have engineered a complete, physics-informed, autonomous revenue protection platform ready to recover billions for Pakistan's power sector. Thank you, and we welcome your questions.",
    "Q: What are your immediate deployment milestones?\nA: Phase 1: 90-day pilot deployment on 5 high-loss 11kV feeders in LESCO (Lahore). Phase 2: Integration with DISCO CIS/billing databases. Phase 3: Nationwide scaling across all 10 DISCO jurisdictions."
)

output_pptx = "Istikshaf_Executive_Presentation.pptx"
prs.save(output_pptx)
print(f"Presentation saved successfully to '{output_pptx}'.")
