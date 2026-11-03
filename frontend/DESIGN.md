---
version: alpha
name: Acme HR Assistant
description: "An internal HR workspace for the Dhaka office: a calm, flat app screen on a faintly green-grey canvas (#f6f7f5 light, #0f1312 dark) with white panels split by 1px borders, near-black green ink, and one deep bottle-green accent (#0b6b4f) taken from the national flag. The accent goes only on the commit actions (Send, Submit request, Approve), focus rings, source chips and the used part of a balance meter. Type is the platform's own sans at four sizes (12/14/16/20), with tabular figures for every number. Status reads as a pale tint with a dark label of the same hue. No shadows at rest, no gradients, no glass, no emoji."
colors:
  canvas: "#f6f7f5"
  surface: "#ffffff"
  raised: "#eef1ef"
  ink: "#17201c"
  muted: "#56615c"
  border: "#dde2df"
  control: "#858f8a"
  track: "#e3e7e5"
  accent: "#0b6b4f"
  accent-hover: "#09583f"
  on-accent: "#ffffff"
  accent-ink: "#0a6148"
  accent-subtle: "#e4f1ea"
  draft-bg: "#fbf0d4"
  draft-ink: "#6e4400"
  draft-border: "#b07d1c"
  pending-bg: "#e3edf9"
  pending-ink: "#1b4b85"
  pending-solid: "#4a82c9"
  approved-bg: "#dcf1e4"
  approved-ink: "#0b5139"
  rejected-bg: "#fbe6e4"
  rejected-ink: "#962019"
  cancelled-bg: "#eceeed"
  cancelled-ink: "#4b544f"
  danger: "#b42318"
  danger-bg: "#fdecea"
  danger-border: "#efb7b0"
typography:
  title:   { fontFamily: "system sans", fontSize: "20px", fontWeight: 600, lineHeight: 1.4, letterSpacing: "-0.01em" }
  reading: { fontFamily: "system sans", fontSize: "16px", fontWeight: 400, lineHeight: 1.625 }
  ui:      { fontFamily: "system sans", fontSize: "14px", fontWeight: 400, lineHeight: 1.43 }
  label:   { fontFamily: "system sans", fontSize: "14px", fontWeight: 500, lineHeight: 1.43 }
  meta:    { fontFamily: "system sans", fontSize: "12px", fontWeight: 500, lineHeight: 1.33 }
  code:    { fontFamily: "system mono", fontSize: "12px", fontWeight: 400, lineHeight: 1.5 }
rounded: { tag: "4px", control: "6px", panel: "8px", full: "9999px" }
spacing: { 1: "4px", 2: "8px", 3: "12px", 4: "16px", 6: "24px", 8: "32px" }
components:
  panel:              { backgroundColor: "{colors.surface}", rounded: "{rounded.panel}", padding: "16px" }
  button-primary:     { backgroundColor: "{colors.accent}", textColor: "{colors.on-accent}", typography: "{typography.label}", rounded: "{rounded.control}", height: "36px", padding: "0 12px" }
  button-primary-hover: { backgroundColor: "{colors.accent-hover}" }
  button-disabled:    { backgroundColor: "{colors.raised}", textColor: "{colors.muted}" }
  button-secondary:   { backgroundColor: "{colors.surface}", textColor: "{colors.ink}", typography: "{typography.label}", rounded: "{rounded.control}", height: "36px", padding: "0 12px" }
  button-destructive: { backgroundColor: "{colors.surface}", textColor: "{colors.danger}", typography: "{typography.label}", rounded: "{rounded.control}", height: "36px", padding: "0 12px" }
  button-ghost:       { textColor: "{colors.muted}", typography: "{typography.label}", rounded: "{rounded.control}", height: "36px", padding: "0 8px" }
  bubble-user:        { backgroundColor: "{colors.raised}", textColor: "{colors.ink}", typography: "{typography.reading}", rounded: "{rounded.panel}", padding: "10px 14px" }
  citation-chip:      { backgroundColor: "{colors.accent-subtle}", textColor: "{colors.accent-ink}", typography: "{typography.meta}", rounded: "{rounded.tag}", padding: "2px 8px" }
  badge-draft:        { backgroundColor: "{colors.draft-bg}", textColor: "{colors.draft-ink}", typography: "{typography.meta}", rounded: "{rounded.tag}", height: "20px", padding: "0 6px" }
  draft-card:         { backgroundColor: "{colors.surface}", textColor: "{colors.ink}", rounded: "{rounded.panel}", padding: "12px 16px" }
---

# Design System: Acme HR Assistant

## Overview

An app screen people work in, not a page they are sold on. Someone in the Dhaka office opens it to ask "how many days can I carry forward?", reads a cited answer, and confirms a leave draft. It should feel like a well-kept ledger: calm, exact, nothing shouting. Mode is **Operate** (Impeccable) / **app screen** (Taste): scanability and known patterns beat novelty.

North star: **a signed register.** Every answer shows its source, every action is a deliberate human signature, and the assistant never acts on its own. The design makes that visible: the commit buttons are the only filled colour; a draft is boxed and labelled until you sign it.

Where the face comes from (Taste's "one face from the brief"): the accent is the deep bottle green of the Bangladesh flag, the font stack carries Bengali fallbacks so Bangla names render, and dates follow the office's `en-GB` format. The one element only this product has: the **draft card**, the agent's proposal waiting for a human signature.

Anti-references: indigo SaaS default (what it uses today), chat apps with gradient bubbles, KPI dashboards with icon tiles, cream-and-terracotta "warm AI" pages.

## Colors

Every component uses these role tokens and nothing else. Tailwind's default palette is removed (`--color-*: initial`), so `bg-zinc-50` or `text-indigo-600` will not compile. That is deliberate. Light and dark are composed separately, not inverted. Theme follows the OS (`prefers-color-scheme`); no toggle.

Contrast is WCAG 2.x relative luminance, computed for every pair below (text needs 4.5:1, UI boundaries and meter segments need 3:1).

| Token (`--color-…`) | Role | Light | Dark | Measured ratio (light / dark) |
| --- | --- | --- | --- | --- |
| `canvas` | Page ground, behind panels | `#f6f7f5` | `#0f1312` | ink on it 15.51 / 15.52 |
| `surface` | Panels, header, inputs, draft card | `#ffffff` | `#161b19` | ink 16.67 / 14.45 |
| `raised` | User bubble, code blocks, hover fill, disabled fill | `#eef1ef` | `#1f2523` | ink 14.66 / 12.93 |
| `ink` | All running text and headings | `#17201c` | `#e6ebe8` | above |
| `muted` | Secondary text, labels, placeholders, meta | `#56615c` | `#a1aca7` | on surface 6.44 / 7.45, on raised 5.66 / 6.66, on canvas 5.99 / 8.00 |
| `border` | Panel edges, row rules, header rule | `#dde2df` | `#2a322f` | decorative (structure, not identification) |
| `control` | Input, select and secondary-button outlines | `#858f8a` | `#66726d` | on surface 3.34 / 3.48 (≥3:1, WCAG 1.4.11) |
| `track` | Empty part of the balance meter | `#e3e7e5` | `#2a322f` | — |
| `accent` | Primary fill, focus ring, meter "used" | `#0b6b4f` | `#4bbf8b` | on surface 6.50 / 7.57; on track 5.21 / 5.72 |
| `accent-hover` | Primary hover/active | `#09583f` | `#63cc9c` | — |
| `on-accent` | Label on accent fill | `#ffffff` | `#06140e` | on accent 6.50 / 8.19; on hover 8.47 / 9.56 |
| `accent-ink` | Accent-coloured text (citations, links) | `#0a6148` | `#6fd1a3` | on surface 7.46 / 9.40; on accent-subtle 6.42 / 7.45 |
| `accent-subtle` | Citation chip ground, `::selection` | `#e4f1ea` | `#173226` | ink on it 14.34 / 11.45 |
| `danger` | Error text, destructive button label | `#b42318` | `#f4a29a` | on surface 6.57 / 8.70; on danger-bg 5.75 / 8.45 |
| `danger-bg` / `danger-border` | Inline error box, destructive hover | `#fdecea` / `#efb7b0` | `#2e1614` / `#6e2e28` | — |

**Request status** (pale tint + dark label of the same hue; the word itself is the non-colour signal):

| Status | `-bg` light / dark | `-ink` light / dark | Ratio light / dark | Meaning |
| --- | --- | --- | --- | --- |
| `draft` | `#fbf0d4` / `#33290f` | `#6e4400` / `#f0c46a` | 7.44 / 8.74 | Waiting for *you* to sign |
| `pending` | `#e3edf9` / `#142538` | `#1b4b85` / `#93bdf0` | 7.42 / 7.97 | Waiting for the manager |
| `approved` | `#dcf1e4` / `#12301f` | `#0b5139` / `#74d3a5` | 7.89 / 7.90 | Done, in the accent family |
| `rejected` | `#fbe6e4` / `#3a1816` | `#962019` / `#f4a29a` | 6.97 / 7.93 | Declined |
| `cancelled` | `#eceeed` / `#262c2a` | `#4b544f` / `#b7bfbb` | 6.72 / 7.58 | Neutral, no hue |

Extra: `draft-border` `#b07d1c` / `#8a6a26` (3.62 / 3.46 on surface) outlines the draft card. `pending-solid` `#4a82c9` / `#5f95d8` is the meter's pending segment (3.16 / 4.25 on track).

Named rules:
- **Accent budget.** Accent appears on: the primary button, the focus ring, citation chips, the meter's used segment, and the header mark. Nothing else. Headings are ink.
- **Approved is the accent.** Green means "go/done" everywhere, so there is one green, not two (Taste: when the accent is green, positive is the accent).
- **Amber means "your move".** Only drafts use amber. The demo-mode notice is neutral, so amber never means two things.
- **Grey is for secondary notes.** Chat answers, panel titles and request names are `ink`.

## Typography

**System stack, no web font.** The build must not fetch from Google Fonts, and the platform face renders instantly, offline, with no layout shift. Segoe UI on the office's Windows machines has tabular digits.

```
--font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Noto Sans Bengali", "Nirmala UI", sans-serif;
--font-mono: ui-monospace, "Cascadia Mono", Consolas, "SF Mono", Menlo, monospace;
```
`Nirmala UI` (Windows) and `Noto Sans Bengali` pick up Bangla names glyph by glyph. If a brand face is ever needed, put the `.woff2` in `app/fonts/` and load it with `next/font/local` (no network at build). Never use `next/font/google`.

Four sizes, three weights (400/500/600). These are Tailwind's default steps; don't add sizes.

| Role | Class | Size / line-height | Weight | Used for |
| --- | --- | --- | --- | --- |
| Title | `text-xl` | 20 / 28 | 600, tracking -0.01em | Empty-state heading, balance figure |
| Reading | `text-base leading-relaxed` | 16 / 26 | 400 | Chat messages, composer text, empty-state sentence |
| UI | `text-sm` | 14 / 20 | 400; 500 for labels/buttons; 600 for panel titles | Panels, rows, buttons, select, product name at `text-base font-semibold` |
| Meta | `text-xs` | 12 / 16 | 400–500 | Badges, citation chips, row sublines, tool trace. The floor: nothing below 12px |

- Chat text is 16px because people read paragraphs of policy here. Everything else is 14px app type. One `h1`: the product name in the header.
- Measure: assistant text `max-w-[68ch]`. `text-wrap: pretty` on message text, `balance` on the empty-state heading.
- `tabular-nums` on every number: balances, day counts, request IDs, dates.
- Mono only for real code: tool names and JSON in the tool trace.
- Punctuation: `…` not `...`; en dash in date ranges (`15–17 Nov 2026`); `&nbsp;` between number and unit (`3&nbsp;days`).

## Layout

- **Spacing scale (4px base, Tailwind steps):** 1=4, 2=8, 3=12, 4=16, 6=24, 8=32. No other values.
- **Rhythm:** 8px inside a group (bubble to its citations, label to value), 16px between groups (turn to turn, panel to panel, panel padding). Gutter is one value horizontally and vertically: 16px below 1024px, 24px from 1024px.
- **Shell:** header bar (surface, 1px bottom `border`) over the canvas. Below it a grid: chat panel + 22rem sidebar from `lg`, one column below. Header and content share the same max width (`max-w-7xl`) and side margins.
- **Chat panel** fills the viewport height on `lg` (`h-dvh` shell, `min-h-0` on scrollers); below `lg` it is `h-[70dvh]` with the sidebar after it.
- **Group, don't box.** Panels are the only boxes. Balance items, request rows and team rows inside a panel are separated by space or a 1px `border` row rule, never by an inner bordered card. The one exception is the **draft card**: it is an actionable object inside the transcript and needs its own edge.
- Long content: `break-words` on all user and model text, `min-w-0` on flex children that truncate, `whitespace-pre-wrap` on messages.

## Elevation & Depth

**Flat. One approach: tone step + 1px border, zero shadows.** Canvas → surface is the only lift; `raised` marks things inside a surface (user bubble, code, hover). No `shadow-*` class anywhere: the app has no custom popovers, and the native `<select>` brings its own. If a floating menu is ever added, it alone gets `0 4px 12px rgb(0 0 0 / 0.08)` (light) and a lighter `border` instead of a shadow in dark.

## Shapes

Tight radius, chosen once (Taste/app-screens: tight 4–8px or soft 16–24, never a mix):

| Token | Value | Applies to |
| --- | --- | --- |
| `rounded-panel` | 8px | Panels, draft card, chat bubbles, inline error box |
| `rounded-control` | 6px | Buttons, inputs, select, suggested-prompt buttons |
| `rounded-tag` | 4px | Status badges, citation chips, code blocks, count tag |
| `rounded-full` | — | Meter track only |

Bubbles have no "tail" corner. Borders are always 1px.

## Components

Class strings live in `components/ui.ts`. Each component lists its states; any state not listed is the default.

**Header.** `bg-surface border-b border-border`, `px-4 py-3` (`lg:px-6`). Left: the mark (24px, the same artwork as `app/icon.svg`, recoloured to `#0b6b4f` with a white "A", `rx` 6) + `h1` "Acme HR Assistant" (`text-base font-semibold`). Demo notice: a neutral tag (`bg-raised text-muted text-xs rounded-tag px-1.5`) reading "Demo mode: scripted replies", with the existing `title` explanation also in `sr-only` text (a tooltip alone doesn't reach touch or screen readers). Right: user switcher. Below 640px the notice wraps to its own line under the name.

**User switcher.** Native `<select>` with a visible `<label>` "Signed in as" (`text-sm text-muted`; `sr-only` below 640px). Select: `bg-surface text-ink border border-control rounded-control h-9 px-2`, `text-base sm:text-sm` (16px on phones stops iOS zoom), explicit bg/colour so Windows dark dropdowns stay readable. Options read "Rahim Uddin · Employee". Disabled while a reply is in flight, with `title="Wait for the reply to finish"`; disabled look = `bg-raised text-muted`. Switching clears the chat, which is expected and silent.

**Chat bubbles.**
- *User:* right-aligned, `max-w-[85%] bg-raised text-ink rounded-panel px-3.5 py-2.5 text-base leading-relaxed`. Neutral, not accent: the accent stays scarce and long threads stay calm.
- *Assistant:* no bubble. Plain `text-ink text-base leading-relaxed max-w-[68ch]` on the panel surface, left-aligned, followed by citations, draft cards, then the tool trace, 8px apart. A plain answer reads like a document, which is what a policy answer is.
- Each message starts with `sr-only` "You said:" / "Assistant:" so the `role="log"` region is clear to screen readers.
- Turns are 16px apart.

**Citation chips.** `ul aria-label="Sources"`, wrapping row, `gap-1.5`. Each chip: `bg-accent-subtle text-accent-ink text-xs font-medium rounded-tag px-2 py-0.5`, text `Leave Policy › Annual leave`. Static (not buttons) until there is a document to open. If they become links: same look + `underline` on hover, focus ring. Chips never truncate (`whitespace-nowrap`), and the row wraps instead.

**Tool-trace disclosure.** Native `<details>`. Summary: `text-xs font-medium text-muted hover:text-ink`, a 12px chevron SVG (1.5px stroke, `aria-hidden`) that rotates 90° when open, label "How I got this · 2 tool calls". Hit area ≥24px tall (`py-1`). Body: `ol` with `border-l border-border pl-3 mt-2 space-y-2`. Each step: line 1 `1.` (muted, tabular) + tool name in `font-mono text-ink` + result tag ("ok" = cancelled-pair neutral tag; "error" = rejected pair). Input and result: `pre` in `bg-raised rounded-tag p-2 font-mono text-xs`, result in `text-muted`, `max-h-48 overflow-auto` so a long result scrolls inside its own frame. Collapsed by default.

**Draft card.** The agent's proposal awaiting signature. `bg-surface border border-draft-border rounded-panel px-4 py-3` (no amber fill: a notice tint is never a ground). Top row: `h3` "Draft #4 · Annual leave" (`text-sm font-semibold`) + status badge. Then a `dl` grid (`grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm`): Dates, Working days (tabular), Reason (`—` in muted when empty). Below 375px the `dl` stays two-column (labels are short).
- *Draft:* one line `text-sm text-muted` "Not submitted yet. Check the dates, then submit." then actions: primary "Submit request", secondary "Discard draft".
- *Busy:* the pressed button shows a spinner + "Submitting…" / "Discarding…"; both buttons disabled; `aria-busy` on the card.
- *Success (pending/approved/rejected/cancelled):* border becomes `border-border`, badge updates, actions are replaced by one sentence announced via `role="status"`: "Submitted. Your manager will review it." / "Approved by your manager." / "Rejected by your manager." / "Draft discarded."
- *Error:* inline error (below) under the actions; buttons re-enabled.

**Buttons.** One height per context: 36px (`h-9`), small 32px (`h-8`) in sidebar rows, and `pointer-coarse:h-11` on touch for both. `text-sm font-medium`, `px-3` (small `px-2.5`), `rounded-control`, `inline-flex items-center gap-1.5`, `transition-colors duration-150`. Focus for all: `focus-visible:outline-2 outline-offset-2 outline-accent`.

| Variant | Default | Hover / active | Disabled | Busy |
| --- | --- | --- | --- | --- |
| Primary | `bg-accent text-on-accent` | `bg-accent-hover` | `bg-raised text-muted` + `cursor-not-allowed` (5.66:1, readable) | spinner + "…ing" label, disabled |
| Secondary | `bg-surface text-ink border border-control` | `bg-raised` | `text-muted border-border` | same |
| Destructive | `bg-surface text-danger border border-danger-border` | `bg-danger-bg` | `text-muted border-border` | same |
| Ghost | `text-muted` no border | `bg-raised text-ink` | `text-muted`, no hover fill, `cursor-not-allowed` | same |

- Never lower opacity to show disabled; use the tokens above so the label stays ≥4.5:1.
- One filled primary per object: the composer's Send, the draft card's Submit request. In team-approval rows Approve is **secondary** (a list of filled buttons is louder than the data), Reject is destructive.
- Spinner: 14px authored SVG circle, `stroke-current`, 2px, `aria-hidden`; the label text carries the state.
- Destructive needs a guard: Reject and Cancel (on a pending request) switch the row into an inline confirm: "Reject Karim's request?" + destructive "Reject request" + ghost "Keep". Discard draft needs no confirm (the assistant can draft it again).

**Status badges.** `inline-flex flex-none whitespace-nowrap h-5 items-center px-1.5 rounded-tag text-xs font-medium bg-{status}-bg text-{status}-ink`. Label from a map, not CSS `capitalize`: Draft, Pending, Approved, Rejected, Cancelled. One status mark per row.

**Balance meter.** Per leave type, inside the "Leave balance" panel, items 16px apart, no inner border.
- Line 1: name (`text-sm text-ink`) left; right `14` (`text-xl font-semibold tabular-nums`) + ` left` (`text-sm text-muted`).
- Line 2: track `h-2 rounded-full bg-track overflow-hidden` with segments: used `bg-accent`, pending `bg-pending-solid`, a 2px `bg-surface` gap between segments so they read apart without colour. `role="img"` + `aria-label="6 used, 2 pending, 12 left of 20"`.
- Line 3: `text-xs text-muted tabular-nums` "6 used · 2 pending · 20 a year"; "2 pending" in `text-pending-ink`. Hide "· 0 pending" when zero; print "0 used" when zero (a real zero).
- The segments and the "left" figure must add up to the entitlement exactly as shown. If the API's numbers don't, say so here rather than fudge the bar.
- Loading: the same three lines with flat `bg-raised` bars at their real size (20px tall for the figure), no shimmer.

**Request list item** (My requests, Team approvals). Rows in a `ul` with `divide-y divide-border`, `py-3`, first/last flush.
- Line 1: `#12 Annual leave` (`text-sm font-medium`, ID `tabular-nums`) + badge right-aligned.
- Line 2: `text-xs text-muted` "15–17 Nov 2026 · 3 days", the action (small Cancel, secondary) at the right.
- Team row: name on line 1, ID muted right; line 2 type · dates · days; reason on line 3 in `text-xs text-ink` in curly quotes (not italic); actions row Approve (secondary sm) + Reject (destructive sm).
- Panel title: `h2 text-sm font-semibold` + count as a neutral tag (`bg-raised text-muted text-xs rounded-tag px-1.5 tabular-nums`).
- Empty: keep the panel and its title, one sentence: "No requests yet. Ask the assistant to draft one." / "Nothing waiting for your approval."
- Loading ≠ empty: while the first fetch runs, show two placeholder rows (`bg-raised` bars at row height), not the empty sentence.

**Empty state with suggested prompts.** Shown in the chat panel before the first message. Left-aligned block, vertically centred, `max-w-[60ch]`, 16px from the panel edges.
- `h2` "Ask about HR policy or your leave" (title style).
- One sentence in `text-base text-ink`: "Answers come from Acme's HR policies with sources. I can draft a leave request, but only you can submit it."
- Suggested prompts: a `ul` of full-width buttons, `gap-2`, one column (two from `sm`), each `text-left text-sm text-ink bg-surface border border-border hover:bg-raised rounded-control px-3 py-2.5 min-h-11`. Clicking sends the prompt.

**Thinking state.** In the log, left-aligned where the answer will appear: three 6px `bg-muted` dots pulsing opacity (0.3→1, 1.2s, 150ms stagger) + "Thinking…" `text-sm text-muted`, `role="status"`. The composer stays editable; only Send is disabled ("Wait for the reply…" as `title`).

**Composer.** `border-t border-border p-3` row: textarea (`text-base`, `bg-surface border border-control rounded-control px-3 py-2`, placeholder "Ask about a policy or request leave…" in `placeholder:text-muted`, `name="message"`, `autoComplete="off"`) + primary Send at the textarea's bottom edge. Visible hint under it on `sm+`: `text-xs text-muted` "Enter to send · Shift+Enter for a new line".

**Inline error.** Used in the chat log, in a draft card, in a row, in a panel. `role="alert"`, `bg-danger-bg border border-danger-border rounded-panel px-3 py-2 text-sm text-danger` (in rows: no box, just `text-xs text-danger`). Copy = what failed + what to do: "Couldn't reach the assistant. Check your connection, then try again." In the chat log it carries a ghost "Try again" button that resends the last message. App-level load failure (employees/health) is the only full-width banner, under the header, same tokens, with "Reload".

## Motion

Purpose only: feedback and state. Nothing enters on load.

| What | How | Duration / easing |
| --- | --- | --- |
| Button, row, chip hover | `transition-colors` (never `transition-all`) | 150ms `ease` |
| Disclosure chevron | `transition-transform` rotate 90° | 150ms `cubic-bezier(.22,1,.36,1)` |
| Thinking dots | opacity pulse, staggered 150ms | 1.2s loop |
| Spinner | rotate | 0.8s `linear` loop |
| Scroll to newest | `scrollTo({behavior})` | `smooth`, else `auto` |

Reduced motion (`motion-reduce:` / `matchMedia('(prefers-reduced-motion: reduce)')`): dots static at full opacity, spinner stops (label still says "Submitting…"), chevron swaps without transition, scroll uses `auto`. Keep colour transitions. No global 0.01ms kill. No bounce easing anywhere (replace the current `animate-bounce`).

## Microcopy

- **Sentence case** for everything: headings, buttons, labels, badges, option text.
- Buttons name the action, 1–3 words: "Send", "Submit request", "Discard draft", "Approve", "Reject request", "Cancel request" (row label "Cancel" with `aria-label="Cancel request #12"`), "Try again", "Keep". Never "OK", "Yes", "Get started", "Learn more".
- Busy labels end with `…`: "Submitting…", "Discarding…", "Approving…", "Rejecting…", "Cancelling…", "Thinking…".
- Errors: what failed + how to recover, no blame, no "Oops". Fallback for unknown errors: "Something went wrong on our side. Try again in a moment." (never a bare "Something went wrong.").
- Second person, plain words of the trade: "leave", "working days", "your manager", "draft", "submitted". Numerals for counts ("3 days", "1 tool call").
- Dates `en-GB`, `15 Nov 2026`; ranges `15–17 Nov 2026`. Time zone `Asia/Dhaka` when times appear.
- No emoji, no exclamation marks, no banned genre words (seamless, effortless, empower, streamline, unlock…).
- `translate="no"` on the product name and tool names.

## Do's and Don'ts

**Do**
- Use role tokens only (`bg-surface`, `text-muted`, `border-control`). If a needed colour has no token, add a token, don't inline a hex.
- Keep running text in `ink`; use `muted` only for secondary notes and meta.
- Pair every status colour with its word.
- Use `tabular-nums` on every number and right-align numbers that stack.
- Show focus with a 2px `accent` outline, offset 2px, on every interactive element.
- Test with a 300-character reason, a long Bangla name, and a 5,000-character tool output.

**Don't**
- Don't use indigo/violet, gradients, glass/backdrop blur, glows, or any resting shadow.
- Don't nest bordered cards (draft card excepted), add coloured left borders, or add icons in tinted squares.
- Don't add eyebrows or tiny tracked uppercase labels.
- Don't fill the draft card or any ground with amber; amber is a badge and a 1px edge.
- Don't fake disabled with `opacity-50`; don't use `outline-none` without the ring.
- Don't put a filled primary on every row.
- Don't use mono outside the tool trace.
- Don't add a font download or an icon library; author the few SVGs (chevron, spinner, mark).

## Responsive Behavior

| Width | Change |
| --- | --- |
| 375 (base) | One column: header, chat (`70dvh`), sidebar panels. Gutter 16px. "Signed in as" label `sr-only`, select fills the remaining row width (`min-w-0 flex-1`). Demo notice on its own line. Suggested prompts one column. Bubbles `max-w-[85%]`. |
| 640 `sm` | Switcher label visible; prompts two columns; balance items three across inside their panel; composer hint visible. |
| 1024 `lg` | Two columns: chat + `22rem` sidebar, shell `h-dvh`, each column scrolls on its own. Gutter 24px. |
| 1280+ | Content capped at `max-w-7xl`, centred; nothing else changes. |

- Touch: `pointer-coarse:h-11` on buttons and suggested prompts; inputs ≥44px tall on touch; `touch-action: manipulation` on buttons.
- No horizontal page scroll at 375px: `pre` blocks scroll inside themselves, chips wrap, long words break.
- Never set `maximum-scale` or `user-scalable=no`; layout must hold at 200% zoom.

## Resolved conflicts

| Conflict (DESIGN-GUIDANCE.md) | Decision for this project |
| --- | --- |
| Title Case (Vercel) vs sentence case (Taste) | **Sentence case** everywhere. |
| Hairlines/1px boxes banned (Taste pages) vs allowed (Impeccable, Vercel, Taste app-screens) | **Allowed as structure only**: panel edges, row rules, control outlines, the draft card edge. No decorative rules, grid lines or dividers between unrelated text. |
| Tone step only (Taste) vs shadow depth system (Impeccable) | **Tone step + 1px border, zero shadows.** |
| Square/pill buttons (Taste pages) vs tight 4–8px (Taste app-screens) | **Tight**: 8 panels, 6 controls, 4 tags. No 12–16px soft radius. |
| Body 16–20px (Taste pages) vs 14px (app screens) | **16px for chat reading text and inputs, 14px for app UI.** |
| Near-black primary (app-screens) vs accent primary | **Accent primary**, because the primary *is* the signature act and there are at most two on screen. |
| Display ≥4× body (Taste pages) | Not applicable to an app screen; largest type is 20px. |
| Monospace ban (Taste) vs tool trace showing JSON | **Mono only inside the trace** (real code/data). |
| Centre at most one moment (Taste) | Nothing centred; the empty state is left-aligned. |

## Agent Prompt Guide

For the implementer. Work in this order and keep behaviour, routes, data flow and copy meaning intact.

1. **Tokens.** Replace `app/globals.css` with the block below. Remove every `dark:` class afterwards; tokens switch by themselves.
2. **Layout + viewport.** In `app/layout.tsx`: `body` → `bg-canvas text-ink font-sans antialiased`; add `export const viewport = { themeColor: [{ media: "(prefers-color-scheme: light)", color: "#f6f7f5" }, { media: "(prefers-color-scheme: dark)", color: "#0f1312" }] }`; add a "Skip to chat" link before the header targeting the composer.
3. **`components/ui.ts`.** Rewrite `focus`, `card` (→ `bg-surface border border-border rounded-panel`), the four button variants and two sizes from the Buttons table. Rename `danger` → `destructive`; add `ghost`.
4. **One component at a time**, in this order: Header (mark + switcher), Chat (bubbles, thinking, composer, empty state, error + Try again), AssistantMessage (citations, trace), DraftCard, StatusBadge (label map), Sidebar (meter, rows, loading vs empty, inline confirms). Update `app/icon.svg` fill to `#0b6b4f`.
5. **Check** at 375, 768 and 1440 in light and dark: no horizontal scroll; every button keyboard-reachable with a visible ring; every state above reachable (empty, thinking, error, draft, submitted, loading sidebar); no raw palette class (`grep -E "(zinc|indigo|rose|amber|sky|emerald)-" components app` returns nothing).

```css
@import "tailwindcss";

@theme {
  --color-*: initial;
  --color-canvas: #f6f7f5;   --color-surface: #ffffff;   --color-raised: #eef1ef;
  --color-ink: #17201c;      --color-muted: #56615c;
  --color-border: #dde2df;   --color-control: #858f8a;   --color-track: #e3e7e5;
  --color-accent: #0b6b4f;   --color-accent-hover: #09583f; --color-on-accent: #ffffff;
  --color-accent-ink: #0a6148; --color-accent-subtle: #e4f1ea;
  --color-draft-bg: #fbf0d4; --color-draft-ink: #6e4400; --color-draft-border: #b07d1c;
  --color-pending-bg: #e3edf9; --color-pending-ink: #1b4b85; --color-pending-solid: #4a82c9;
  --color-approved-bg: #dcf1e4; --color-approved-ink: #0b5139;
  --color-rejected-bg: #fbe6e4; --color-rejected-ink: #962019;
  --color-cancelled-bg: #eceeed; --color-cancelled-ink: #4b544f;
  --color-danger: #b42318;   --color-danger-bg: #fdecea; --color-danger-border: #efb7b0;

  --font-sans: system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Noto Sans Bengali", "Nirmala UI", sans-serif;
  --font-mono: ui-monospace, "Cascadia Mono", Consolas, "SF Mono", Menlo, monospace;
  --radius-tag: 4px; --radius-control: 6px; --radius-panel: 8px;
}

/* Unlayered, so it overrides @theme's layered :root values. */
@media (prefers-color-scheme: dark) {
  :root {
    --color-canvas: #0f1312;   --color-surface: #161b19;   --color-raised: #1f2523;
    --color-ink: #e6ebe8;      --color-muted: #a1aca7;
    --color-border: #2a322f;   --color-control: #66726d;   --color-track: #2a322f;
    --color-accent: #4bbf8b;   --color-accent-hover: #63cc9c; --color-on-accent: #06140e;
    --color-accent-ink: #6fd1a3; --color-accent-subtle: #173226;
    --color-draft-bg: #33290f; --color-draft-ink: #f0c46a; --color-draft-border: #8a6a26;
    --color-pending-bg: #142538; --color-pending-ink: #93bdf0; --color-pending-solid: #5f95d8;
    --color-approved-bg: #12301f; --color-approved-ink: #74d3a5;
    --color-rejected-bg: #3a1816; --color-rejected-ink: #f4a29a;
    --color-cancelled-bg: #262c2a; --color-cancelled-ink: #b7bfbb;
    --color-danger: #f4a29a;   --color-danger-bg: #2e1614; --color-danger-border: #6e2e28;
  }
}

:root { color-scheme: light dark; }
::selection { background: var(--color-accent-subtle); color: var(--color-ink); }
html { scrollbar-color: var(--color-control) transparent; }
```

Prompt to reuse: *"Restyle `<component>` per DESIGN.md: role tokens only, the component's listed states, sentence-case copy from Microcopy, no shadows/gradients/raw palette classes. Keep props and behaviour unchanged."*

## Known Gaps

- No custom icon set beyond chevron, spinner and mark; if more icons are needed, pick one outline set at 1.5px stroke and record it here.
- Citation chips are static; a policy document viewer would need a link style and a reading layout.
- The `Try again`, inline-confirm and loading-placeholder states are new behaviour, not just restyling; they need small state additions in `page.tsx`/`useAction`.
- Contrast was computed from the hex values above; antialiasing and the user's display will vary, so check the dark theme by eye once on a real Windows machine.
