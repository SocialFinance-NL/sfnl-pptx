# SFNL Visual-First Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the SFNL PowerPoint plugin generate visual-first decks instead of white text pages.

**Architecture:** Keep the spec-first Python pipeline, but make visual exhibits the default contract for content slides. Extend the component catalogue and renderer with parameterized visual primitives so each slide can control card size, location, icon choice, color, highlight, and layout variant.

**Tech Stack:** Python 3.13, python-pptx, pytest, bundled SFNL PowerPoint template.

---

## File Structure

- `sfnl-pptx/engine/assets/components/index.json`: add visual-first component metadata, control schemas, and new components.
- `sfnl-pptx/engine/scripts/build_from_spec.py`: render visual components with configurable geometry, icons, colors, and variants.
- `sfnl-pptx/engine/reference/deck-spec.md`: document slide-level `visual` controls and the new components.
- `sfnl-pptx/skills/sfnl-deck/SKILL.md`: make visual-first selection mandatory and text-only slides exceptional.
- `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`: require visual exhibit review.
- `sfnl-pptx/tests/test_visual_components.py`: regression tests for visual richness and per-slide controls.
- `sfnl-pptx/tests/fixtures/sample_visual_spec.json`: reusable sample deck with cards, KPI/status bar, timeline, and org/schema visuals.

## Tasks

### Task 1: Visual Regression Tests

- [x] Write tests that prove the current renderer is too sparse:
  - `content-cards` must create background/card shapes and icon glyphs.
  - `kpi-trio` must create KPI panels and an optional progress/status bar.
  - `process-timeline` must render arrow/process shapes with per-step colors.
  - `schema-grid` must render grouped boxes and connector lines.
  - Per-slide `visual` controls must change position and size.
- [x] Run the tests and verify they fail before implementation.

### Task 2: Parameterized Visual Rendering

- [x] Add reusable helper functions for:
  - theme fills/lines,
  - text boxes,
  - icon bubbles,
  - configurable geometry,
  - component-level default values with slide-level overrides.
- [x] Upgrade `content-cards`, `kpi-trio`, and `chart-static`.
- [x] Add `process-timeline`, `schema-grid`, and `image-icon-trio` component entries and renderers.

### Task 3: Contract and Skill Updates

- [x] Document the `visual` control object.
- [x] Update the generate skill so the model chooses a visual component for every content slide unless the user explicitly asks for plain text.
- [x] Update the review skill so text-only body slides are treated as blocked unless explicitly justified.

### Task 4: Verification

- [x] Run the focused visual tests.
- [x] Run the full pytest suite.
- [x] Build a sample visual deck and, if PowerPoint COM is available, render it for inspection.
