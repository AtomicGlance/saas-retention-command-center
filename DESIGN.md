---
name: Retention Command Center
description: A metropolitan operations briefing for recurring-revenue decisions.
colors:
  midnight-ink: "#10243f"
  control-room-navy: "#0b2948"
  route-blue: "#1e61d2"
  signal-coral: "#ef5b4c"
  healthy-mint: "#1ba784"
  watch-amber: "#e4a937"
  cool-paper: "#f4f7fb"
  white: "#ffffff"
  slate: "#5f7188"
  divider: "#d8e0eb"
typography:
  display:
    fontFamily: "Bahnschrift, Arial Narrow, Segoe UI, sans-serif"
    fontSize: "clamp(2.75rem, 7vw, 6.5rem)"
    fontWeight: 600
    lineHeight: 0.92
    letterSpacing: "-0.045em"
  headline:
    fontFamily: "Bahnschrift, Arial Narrow, Segoe UI, sans-serif"
    fontSize: "clamp(1.5rem, 3vw, 2.5rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Aptos, Segoe UI Variable, Helvetica Neue, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Aptos, Segoe UI Variable, Helvetica Neue, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.12em"
rounded:
  data: "2px"
  surface: "12px"
spacing:
  xs: "6px"
  sm: "12px"
  md: "20px"
  lg: "32px"
  xl: "56px"
components:
  metric-card:
    backgroundColor: "{colors.white}"
    textColor: "{colors.midnight-ink}"
    rounded: "{rounded.surface}"
    padding: "{spacing.md}"
  status-rail:
    backgroundColor: "{colors.control-room-navy}"
    textColor: "{colors.white}"
    rounded: "{rounded.surface}"
    padding: "{spacing.md}"
  risk-chip:
    backgroundColor: "{colors.signal-coral}"
    textColor: "{colors.white}"
    rounded: "{rounded.data}"
    padding: "5px 8px"
---

# Design System: Retention Command Center

## Overview

**Creative North Star: "Metropolitan Operations Briefing"**

The interface should feel like a premium operating review designed with the
clarity of transit information: decisive routes, explicit states, legible
numbers, and just enough civic confidence to make the work memorable. It is
light because the real usage scene is a hiring manager or analyst reviewing the
portfolio during the day, often on an ordinary laptop under bright ambient
light.

This world replaces generic dark SaaS chrome with an authored briefing surface.
Business performance is the map; the viewer should immediately see the revenue
trajectory, the operating status, and the next intervention.

**Key Characteristics:**

- One dominant analytical story per viewport.
- Route blue for primary analytical movement, not decorative accents.
- Coral, mint, and amber communicate operational state with text redundancy.
- Tight transport-signage labels paired with large tabular figures.
- Thin dividers and tonal regions create structure; shadows remain rare.

## Colors

The palette uses cool institutional neutrals with three unambiguous signal
colors.

### Primary

- **Route Blue:** Owns revenue movement, selected states, links, and the primary
  analytical trace.
- **Control-Room Navy:** Carries the operating-status rail and other rare
  high-contrast regions.

### Secondary

- **Signal Coral:** Flags underperformance, negative deltas, and the first risk
  priority.
- **Healthy Mint:** Marks healthy performance and positive movement.
- **Watch Amber:** Marks results that need attention but are not failures.

### Neutral

- **Cool Paper:** Default canvas.
- **White:** Analytical surfaces.
- **Midnight Ink:** Primary text.
- **Slate:** Supporting text.
- **Divider:** Grids and quiet boundaries.

**The Signal Integrity Rule.** Signal colors always communicate a state and are
never used merely to make the page more colorful.

## Typography

**Display Font:** Bahnschrift with condensed sans-serif fallbacks  
**Body Font:** Aptos with modern system sans-serif fallbacks  
**Label Font:** Aptos, uppercase only for short wayfinding labels

**Character:** Display type borrows the compact authority of station signage.
Body copy stays plain, modern, and easy to scan. All financial values use
tabular numerals.

### Hierarchy

- **Display:** Revenue-scale numbers and the primary decision statement only.
- **Headline:** Dashboard title and major section framing.
- **Title:** Card and chart titles.
- **Body:** Explanations, annotations, and table content; keep paragraphs below
  70 characters per line where practical.
- **Label:** Compact uppercase metadata and axis-like wayfinding.

**The Numeric Priority Rule.** Important numbers are larger than their
containers' labels; labels never compete with the value.

## Layout

Desktop uses a twelve-column briefing grid. The first viewport is asymmetric:
the revenue trajectory occupies eight columns and the operating-status rail
occupies four. Supporting diagnostics then use balanced two-column and
full-width passages.

The container is fluid to 1480px with 24–40px edge padding. At 960px, the
status rail becomes a horizontal strip. At 720px, every major region becomes a
single column, charts retain horizontal breathing room, and the table scrolls
inside its own framed region.

**The Briefing Sequence Rule.** Always order content as pulse, movement,
drivers, cohort durability, then action queue.

## Elevation & Depth

The system is flat by default. Depth comes from white surfaces against cool
paper, controlled borders, color fields, and chart layering. A single soft
ambient shadow may be used on the dominant first-viewport panel; routine cards
do not float.

**The Flat-by-Default Rule.** Shadows identify hierarchy, not card boundaries.

## Shapes

Large analytical surfaces use gently engineered 12px corners. Dense data cells,
chart annotations, and signal chips use 2px corners. Circular dots are reserved
for route markers and legend keys. Avoid pill-shaped containers except for
compact status text where the semantics justify them.

## Components

### Metric Cards

- White field, quiet divider, 12px outer radius.
- Large tabular value with a short definition and an explicit status.
- Hover raises border contrast only; it does not lift or glow.

### Operating-Status Rail

- Control-room navy field with high-contrast white type.
- Metrics are separated by translucent rules and tiny route markers.
- The rail becomes a horizontal grid before stacking on mobile.

### Charts

- Use semantic SVG with direct labels where feasible.
- Gridlines are sparse and quiet.
- Primary traces use Route Blue; Coral appears only at the risk endpoint or
  negative comparison.
- Tooltips or focus states must expose exact values to keyboard users.

### Cohort Matrix

- Cells use a restrained mint-to-paper-to-coral state scale.
- The left label column and month header remain legible while the matrix
  horizontally scrolls on narrow screens.

### Risk Queue

- Ranked rows use a route-number marker and a single stated intervention.
- The highest-priority row receives Coral; later rows remain neutral.

## Do's and Don'ts

### Do:

- **Do** give the revenue trajectory the strongest visual weight.
- **Do** annotate the slight December decline directly on the chart.
- **Do** keep metric definitions close to the values they explain.
- **Do** preserve source-backed numbers and the synthetic-data disclosure.

### Don't:

- **Don't** use generic dark SaaS card grids as the main composition.
- **Don't** add neon glows, glassmorphism, gradients, or ornamental dashboard
  icons.
- **Don't** hide underperformance behind color alone.
- **Don't** round every small element into a pill.
