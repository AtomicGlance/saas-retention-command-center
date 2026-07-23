---
name: Retention Command Center
description: A restrained operating dashboard for revenue and retention decisions
colors:
  decision-blue: "#1473E6"
  signal-gold: "#D99A18"
  ink: "#1F1F1F"
  secondary-ink: "#5F6368"
  canvas: "#F7F8FA"
  surface: "#FFFFFF"
  divider: "#DADCE0"
typography:
  display:
    fontFamily: "Arial, Helvetica, sans-serif"
    fontSize: "clamp(2rem, 4vw, 3.5rem)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Arial, Helvetica, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Arial, Helvetica, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
rounded:
  card: "14px"
  control: "10px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
---

# Design System: Retention Command Center

## Overview

**Creative North Star: "The Monthly Operating Review"**

The interface should feel like the one calm page an analytics lead opens before
a decision meeting: factual, dense enough to be useful, and free of theatrical
dashboard chrome. The visual system is inherited from the canonical Data
Analytics artifact reader and uses a restrained light operating surface.

**Key Characteristics:**

- Summary first, evidence second, detail last.
- Blue carries the primary analytical signal; gold is reserved for attention.
- Exact definitions and sources remain one interaction away.
- Synthetic status is visible without dominating the page.

## Colors

The palette is restrained: decision blue for primary marks, signal gold for one
focal risk state, and neutral surfaces for everything else.

**The Evidence Color Rule.** Color distinguishes analytical roles, never merely
decorates categories already named by an axis.

## Typography

The system uses a workhorse sans-serif stack for fast scanning and consistent
portable rendering. Numerical values receive weight and scale rather than a
costume-like monospace treatment.

**The One-Read Rule.** A heading states what is measured; interpretation lives
in a subtitle or adjacent decision note.

## Layout

The page follows one operating sequence: KPI context, twelve-month movement,
diagnostic breakdowns, cohort behavior, then an exact lookup table. Standard
charts use at least six columns and stack vertically on narrow screens.

## Elevation & Depth

Depth is tonal and structural. Cards use either a quiet divider or the shared
reader's ambient elevation, never both as competing outlines.

## Shapes

Cards use gently curved 14px corners; controls use 10px corners; compact filter
states may use pills. Charts themselves remain flat and unboxed inside their
container.

## Components

### Metric cards

Each card contains one headline KPI and only directly comparable context. The
definition and SQL provenance remain available through the source affordance.

### Charts

Chart titles are neutral and descriptive. Subtitles carry the date range,
population, denominator, or supported interpretation. Marks use direct labels,
ordering, and shape in addition to color.

### Tables

Tables are dense, full-width lookup surfaces with explicit default sorting and
movement formatting.

## Do's and Don'ts

### Do:

- **Do** state the population and denominator for every rate.
- **Do** show at least twelve periods for trend charts.
- **Do** keep the synthetic-data caveat visible near the dashboard title.

### Don't:

- **Don't** imply that descriptive segment differences prove causality.
- **Don't** use green/red as the only encoding of good and bad movement.
- **Don't** add decorative gradients, glass panels, or redundant legends.
