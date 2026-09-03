---
name: Istikshaf Grid Noir
colors:
  surface: '#11150a'
  surface-dim: '#11150a'
  surface-bright: '#373b2e'
  surface-container-lowest: '#0c0f06'
  surface-container-low: '#191d12'
  surface-container: '#1d2115'
  surface-container-high: '#272b1f'
  surface-container-highest: '#32362a'
  on-surface: '#e1e4d2'
  on-surface-variant: '#c2cab0'
  inverse-surface: '#e1e4d2'
  inverse-on-surface: '#2e3225'
  outline: '#8c947c'
  outline-variant: '#434935'
  surface-tint: '#9cd924'
  primary: '#fffff3'
  on-primary: '#233600'
  primary-container: '#b6f542'
  on-primary-container: '#4c6e00'
  inverse-primary: '#476800'
  secondary: '#45dceb'
  on-secondary: '#00363b'
  secondary-container: '#00c0cf'
  on-secondary-container: '#00494f'
  tertiary: '#fffeff'
  on-tertiary: '#422d00'
  tertiary-container: '#ffdda5'
  on-tertiary-container: '#835d00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b7f643'
  primary-fixed-dim: '#9cd924'
  on-primary-fixed: '#131f00'
  on-primary-fixed-variant: '#354e00'
  secondary-fixed: '#88f3ff'
  secondary-fixed-dim: '#40d9e8'
  on-secondary-fixed: '#001f23'
  on-secondary-fixed-variant: '#004f55'
  tertiary-fixed: '#ffdea8'
  tertiary-fixed-dim: '#f9bc45'
  on-tertiary-fixed: '#271900'
  on-tertiary-fixed-variant: '#5e4200'
  background: '#11150a'
  on-background: '#e1e4d2'
  surface-variant: '#32362a'
typography:
  display-lg:
    fontFamily: Archivo Narrow
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Archivo Narrow
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Archivo Narrow
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-sm:
    fontFamily: Archivo Narrow
    fontSize: 18px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.5'
  data-lg:
    fontFamily: IBM Plex Mono
    fontSize: 18px
    fontWeight: '500'
    lineHeight: '1'
  data-md:
    fontFamily: IBM Plex Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
  label-caps:
    fontFamily: Public Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  grid_columns: '12'
  gutter: 16px
  margin: 24px
  unit: 4px
  stack-xs: 4px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
  stack-xl: 40px
---

## Brand & Style
The design system is engineered for high-stakes utility monitoring, specifically for the Istikshaf desktop application. The brand personality is **Precise, Industrial, and Vigilant**. It balances the raw technicality of electrical engineering with the sophisticated data density of modern SaaS.

The visual style is a refined **Corporate Modern** approach with a **Technical Noir** influence. It prioritizes "Information First" hierarchy, utilizing a dark-mode-only foundation to reduce eye strain for operators during long shifts. The aesthetic avoids decorative fluff—no glassmorphism or heavy gradients—favoring solid dark surfaces, hairline borders, and tactical color hits to signal anomalies in the grid.

## Colors
The palette is built on a "Deep Green-Black" foundation to provide a richer, more professional atmosphere than pure grayscale dark modes. 

- **Primary (Electric Lime):** Reserved exclusively for active states, primary actions, and confirmed grid-loss detections. 
- **Functional Accents:** Smart-meter Cyan and Monthly Amber distinguish data streams without creating visual noise.
- **Priority Logic:** Coral and Orange are used sparingly for alerts. The "Normal Status Green" is desaturated compared to the Brand Lime to ensure alerts don't compete with brand identity.
- **Surface Hierarchy:** Depth is created by lightening the green-black tint as elements move closer to the user.

## Typography
The typographic system utilizes a tri-font strategy to separate intent:
1. **Archivo Narrow:** Used for structural headings and dashboard titles. Its condensed nature allows for longer titles in dense layouts without sacrificing impact.
2. **Public Sans:** The workhorse for all interface labels, paragraphs, and descriptions. It provides neutral, high-legibility clarity.
3. **IBM Plex Mono:** Strictly for technical values, Meter IDs, coordinates, and timestamps. This ensures that numerical data is easily scannable and columns align perfectly in data tables.

## Layout & Spacing
This design system employs a **12-column fluid grid** for desktop, optimized for a 1440px wide viewport. Content is housed within "Operational Zones."

- **Density:** High information density is required. Use a 4px baseline grid.
- **Margins:** A 24px outer margin ensures the UI feels contained on widescreen monitors.
- **Gaps:** Gutters are fixed at 16px to maintain a tight, industrial feel. 
- **Reflow:** On smaller desktop widths (1024px), the 12-column grid persists, but sidebars transition to icon-only "rail" states to preserve the workspace for maps and data tables.

## Elevation & Depth
Depth in the system is represented by **Tonal Layers** rather than shadows. 
- **Level 0 (Background):** `#070A09` (Main canvas).
- **Level 1 (Sub-panels):** `#0C110E` (Sidebar and footer).
- **Level 2 (Cards/Containers):** `#101512` (Main widget background) with a 1px solid border of `#263129`.
- **Level 3 (Popovers/Modals):** `#161D19` with a subtle 16px blur shadow (Black, 40% opacity) to create separation from the primary surface.

Avoid heavy drop shadows. Interaction depth (e.g., a pressed button) should be communicated through color shifts (darkening the Electric Lime) rather than physical "sinking" effects.

## Shapes
The shape language is strictly **Rectilinear**. 
- **Standard Radius:** 8px for main UI containers (cards, data tables).
- **Small Radius:** 4px for small components like input fields, checkboxes, and tags.
- **Large Radius:** 12px for global containers or primary modal windows.

This "Softened Brutalist" approach maintains an industrial look while feeling modern and professional. Full-pill shapes are reserved only for "Status Badges" to distinguish them from actionable buttons.

## Components
- **Buttons:** Primary buttons use a solid `#B6F542` fill with black text. Secondary buttons use a `#263129` border with white text. Ghost buttons use `text_secondary` and no border.
- **Data Tables:** Use `surface_primary` for rows. The header row should be `background_secondary` with `label-caps` typography. Row separators are 1px `#263129`.
- **Status Chips:** High-priority alerts use a coral background at 10% opacity with solid coral text. This "tinted" style ensures color coding is readable without being overwhelming.
- **Input Fields:** Dark background (`background_main`), 1px border (`border_subtle`). On focus, the border changes to the Electric Lime primary color.
- **Grid Widgets:** Every widget must have a clear title in `headline-sm` and a technical ID in `data-md` in the top right corner. 
- **Key Metrics:** Large numerical displays should use `data-lg` to ensure they are the first thing an operator sees when scanning the dashboard.