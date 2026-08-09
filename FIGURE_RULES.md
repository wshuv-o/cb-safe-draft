# Figure Ruleset

A checklist for producing publication figures. Give this to Claude before any
plotting task, or paste the audit prompt at the bottom to have an existing
figure checked against it.

Applies to any tool — matplotlib, pgfplots, ggplot2, Illustrator.

---

## 0. The governing principle

**A figure should look like it was made by someone who cared about the
result.** Almost every rule below is a specific consequence of that. A reader
cannot see your effort directly; they infer it from whether the defaults were
touched. Untouched defaults read as indifference, and indifference is what
makes a reader start doubting everything else on the page.

---

## 1. Typography — the loudest signal

- [ ] **The figure's font matches the document's body font.** Serif document
      (LaTeX, IEEE, Elsevier) means serif figures. This single rule does more
      than the rest combined. A default sans-serif axis label under a serif
      paragraph announces that the figure was made elsewhere and pasted in.
- [ ] **Math is typeset, not spelled out.** `$f$`, `$\gamma$`, `$n_{\mathrm{m}}$`,
      `$10^{-2}$` — never `f`, `gamma`, `n_m`, `1e-2`. Variables are italic;
      units and function names are upright.
- [ ] **Font sizes are 7–9 pt at final printed size**, and never smaller than
      the caption text. Check by measuring the rendered figure, not the code.
- [ ] **One typeface across every figure in the document.** No mixing.

---

## 2. No titles inside the axes

- [ ] **Delete every `title=` / `plt.title()`.** The caption does that job.
      A title inside the axes is redundant with the caption, steals plot area,
      and is the most common tell of a plot that was never adapted for print.
- [ ] Panel identifiers in multi-panel figures are `(a)`, `(b)` in the corner
      or below the panel — not sentences.

---

## 3. Frame and ink

- [ ] **Top and right spines removed** unless the data genuinely needs a closed
      box (heatmaps, images, matrices do).
- [ ] **Grid is recessive or absent.** Light grey, thin, behind the data. If
      the reader notices the grid before the curves, it is too strong.
- [ ] **No shadows, no 3-D effects on 2-D data, no gradient fills, no
      background tint** unless the tint encodes something (a failure region,
      a confidence band).
- [ ] Every element left in the figure earns its place. If deleting it loses
      no information, delete it.

---

## 4. Encoding — survive greyscale and colour blindness

- [ ] **Each series differs in at least two channels:** colour *and* marker
      shape, or colour *and* dash pattern. Colour alone fails in print and for
      ~8% of male readers.
- [ ] **Colour-blind-safe palette** (Okabe–Ito, viridis, cividis). Never
      red-vs-green as the only distinction.
- [ ] **Your own method is visually privileged** — heavier line, solid where
      others are dashed, filled markers where others are hollow — but not by
      colour saturation alone.
- [ ] **Print the page in black and white and check it.** If two curves become
      the same curve, the encoding failed.

---

## 5. Legend

- [ ] **The legend never covers data.** Especially not the region containing
      the result you are arguing for. This is a real and common self-inflicted
      wound.
- [ ] Prefer legend **outside the axes** (above, in 2–3 columns) or **direct
      labels on the curves**. Direct labelling is the strongest option when
      there are ≤4 series.
- [ ] Multi-panel figures get **one shared legend**, not one per panel.
- [ ] Legend order matches the visual order of the curves where possible, and
      the frame is off.

---

## 6. Axes and ranges

- [ ] **No large dead space.** If data spans 10–55, the axis does not run 0–100.
- [ ] **But do not truncate to exaggerate.** If a zero baseline is meaningful
      (counts, rates, accuracy), either include it or make the truncation
      visually explicit with an axis break.
- [ ] **Ticks are round numbers** at sensible intervals. Not 7 ticks with
      three decimals.
- [ ] **Axis labels carry units and symbols**: "malicious fraction $f$ (%)",
      not "f".
- [ ] **Log scale when the data spans orders of magnitude** — and say so in the
      axis label or caption.
- [ ] Shared axes across panels use **identical ranges** so panels are
      comparable at a glance.

---

## 7. Sampling density

- [ ] **Enough points that a line looks like a function, not a sketch.**
      Three x-values joined by two straight segments is a table pretending to
      be a plot. If you only have three conditions, consider a grouped bar
      chart or dot plot instead of a line.
- [ ] If the sweep is genuinely sparse, say so, and use markers prominently so
      the reader sees where measurement actually happened.

---

## 8. Uncertainty

- [ ] **If you ran multiple seeds or trials, show the spread** — error bars,
      shaded ±1 SD band, or individual runs behind the mean. Hiding it wastes
      real evidence and invites the reviewer to ask for it.
- [ ] **State in the caption what the interval is**: SD, SEM, 95% CI, min–max,
      and over how many runs. An unlabelled error bar is worse than none.
- [ ] Single-seed results are marked as single-seed.

---

## 9. Annotation — direct the reader

- [ ] **The figure names its own finding.** One or two short annotations —
      an arrow to the crossover, a labelled threshold line, a shaded regime —
      pointing at what the reader is supposed to notice.
- [ ] **Reference lines for the values that define success or failure**:
      baseline, chance level, theoretical bound, a predicted breakdown point.
      If your paper predicts a boundary, mark it on the figure.
- [ ] Annotations do not collide with curves, markers, error bars, or each
      other. Check the rendered output, not the code.
- [ ] Annotation text is small (~6–7 pt) and grey, so it reads as commentary
      rather than competing with the data.

---

## 10. Caption

- [ ] **Self-contained.** A reader who skips the body text can still tell what
      is plotted, on what data, under what conditions.
- [ ] Structure: *what is shown* → *conditions/parameters* → *what to notice*.
- [ ] **Does not repeat an in-axes title** (there isn't one — see §2).
- [ ] States n, seeds, and error-bar meaning.
- [ ] **No status notes in a submitted caption.** "still computing", "pending",
      "TODO", "results to be updated" — any of these is a desk-reject trigger.
      Either finish the run or cut the series.

---

## 11. Consistency across the whole document

- [ ] **One series = one colour + one marker, everywhere in the paper.** If
      your method is a solid heavy line in Fig. 4, it is a solid heavy line in
      Fig. 9.
- [ ] Same font, same sizes, same spine treatment, same grid across all
      figures. Enforce this with **one shared style file imported by every
      plotting script**, never by editing each script separately.
- [ ] Figure widths match the column measure exactly (e.g. 3.5 in single
      column, 7.16 in double for IEEE two-column).

---

## 12. Export

- [ ] **Vector output** (PDF, EPS, SVG) for plots. Raster (PNG, ≥600 dpi) only
      for images, heatmaps with many cells, or photographs.
- [ ] **Fonts embedded** (`pdf.fonttype = 42` in matplotlib, or equivalent).
- [ ] **Generated at final size.** Never draw large and scale down in LaTeX —
      that shrinks the text and breaks the size relationship with the body
      font. Set `figsize` to the real column width and set font sizes in
      points.
- [ ] Whitespace trimmed (`bbox_inches='tight'`), but padding not zero.

---

## 13. Honesty

- [ ] **The figure does not oversell.** If everything fails, the figure shows
      everything failing, deliberately and legibly.
- [ ] Axis truncation, outlier removal, smoothing, and clipping are disclosed
      in the caption.
- [ ] Nothing is drawn that was not measured. No interpolated points presented
      as data, no illustrative curves in a results figure without saying they
      are schematic.

---

## Quick tells that a figure was never customised

The seven that get spotted first, in order:

1. Default sans-serif font in a serif document
2. A title sitting inside the axes
3. Legend box parked on top of the data
4. Every series the same marker, distinguished only by hue
5. Wide empty margins because the axis range was never set
6. Plain-text `gamma`, `f`, `n_m` where the paper uses math
7. Three data points connected by straight lines across a wide axis

---

## Audit prompt

Paste this with any figure, script, or image:

> Audit this figure against FIGURE_RULES.md, section by section. For each
> section, say PASS, FAIL, or N/A with a one-line reason. Then give me the
> ordered fix list, most damaging first, and the code changes to make them.
> Render the result and look at the rendered image before telling me it is
> fixed — do not judge the figure from the code alone.

That last sentence matters. Collisions between annotations, legends, and
curves are invisible in source and obvious in the render.
