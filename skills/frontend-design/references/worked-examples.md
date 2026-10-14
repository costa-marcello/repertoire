# Worked Examples

Full code for the four examples in SKILL.md. Each one follows the Gotchas there: overlays sit on a positioned parent with `pointer-events: none`, meaningful images keep their alt text, hover feedback lasts 300ms or less, and every animation is reduced under `prefers-reduced-motion`. Contrast ratios were measured with `scripts/contrast.py`.

## Contents

1. [Luxury watch pricing card (before and after)](#1-luxury-watch-pricing-card-before-and-after)
2. [Developer tool file upload](#2-developer-tool-file-upload)
3. [Meditation app testimonial carousel](#3-meditation-app-testimonial-carousel)
4. [Fintech KPI dashboard](#4-fintech-kpi-dashboard)

## 1. Luxury watch pricing card (before and after)

**Before (generic):** system fonts, raw palette classes, no theming, no focus style.

```jsx
<div className="bg-white rounded-lg shadow-md p-6">
  <img src={watch.image} alt={watch.name} className="w-full rounded" />
  <h3 className="text-xl font-semibold mt-4">{watch.name}</h3>
  <p className="text-gray-600">{watch.description}</p>
  <span className="text-2xl font-bold">{formatPrice(watch.price)}</span>
  <button className="bg-blue-500 text-white px-4 py-2 rounded">Add to Cart</button>
</div>
```

**After (editorial luxury):** semantic structure, tokens, distinctive type, one deliberate hover moment.

```jsx
<article className="pricing-card">
  <div className="card-image">
    <img src={watch.image} alt={watch.name} />
  </div>
  <header className="card-content">
    <h3 className="card-title">{watch.name}</h3>
    <p className="card-description">{watch.description}</p>
  </header>
  <footer className="card-footer">
    <span className="price">{formatPrice(watch.price)}</span>
    <button type="button" className="cta-button">View Timepiece</button>
  </footer>
  <div className="gold-border-accent" aria-hidden="true" />
</article>
```

```css
.pricing-card {
  --charcoal: #1a1a1a;
  --gold: #c9a962;   /* 7.74:1 on charcoal */
  --cream: #f5f0e8;  /* 15.34:1 on charcoal; 8.04:1 at 70% */
  position: relative; /* anchors the grain and the border overlay */
  overflow: hidden;
  background: var(--charcoal);
  color: var(--cream);
}

.card-title { font-family: "Playfair Display", Georgia, serif; letter-spacing: -0.01em; }
.card-description { font-family: "Cormorant Garamond", Garamond, serif; color: rgb(245 240 232 / 0.7); }
.price { font-family: "Playfair Display", Georgia, serif; color: var(--gold); }

.pricing-card::before,
.gold-border-accent {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none; /* never swallow clicks on the CTA */
}

.pricing-card::before {
  background: url("/noise.svg");
  opacity: 0.03;
}

.gold-border-accent {
  border: 1px solid var(--gold);
  opacity: 0;
  transition: opacity 300ms ease-out;
}

.card-image img {
  transition: transform 300ms ease-out;
}

@media (hover: hover) {
  .pricing-card:hover .gold-border-accent { opacity: 1; }
  .pricing-card:hover .card-image img { transform: translateY(-6px) scale(1.03); }
}

.cta-button {
  padding: 0.75rem 1.5rem;
  border: 1px solid var(--gold);
  background: transparent;
  color: var(--gold);
  font-family: "Cormorant Garamond", Garamond, serif;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: background-color 200ms ease-out, color 200ms ease-out;
}

@media (hover: hover) {
  .cta-button:hover { background: var(--gold); color: var(--charcoal); } /* 7.74:1 */
}

.cta-button:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  .gold-border-accent,
  .card-image img { transition: none; }
}
```

Load both fonts (a Google Fonts `<link>` or `next/font`); without them the card falls back to Georgia and loses its character.

## 2. Developer tool file upload

The drop zone is a `<label>` for a real file input, so keyboard and screen reader users can open the picker without dragging.

```html
<div class="upload">
  <label class="upload-zone" for="config-file" data-state="idle">
    <input id="config-file" class="visually-hidden" type="file" accept=".json,.yaml,.yml,.toml" />
    <span class="prompt">&gt; drop config here or press Enter to browse_</span>
  </label>
  <div class="progress" role="progressbar" aria-label="Upload progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
    <div class="progress-bar"></div>
  </div>
  <output class="log" for="config-file" aria-live="polite"></output>
</div>
```

```css
:root {
  --near-black: #0d0d0d;
  --electric-green: #00ff88; /* 14.49:1 on near-black */
  --amber: #ffaa00;          /* 10.18:1 on near-black */
}

.upload-zone {
  position: relative; /* anchors the scanline overlay */
  display: block;
  padding: 3rem 2rem;
  font-family: "JetBrains Mono", ui-monospace, monospace;
  color: var(--electric-green);
  background: var(--near-black);
  border: 2px dashed var(--electric-green);
  cursor: pointer;
}

.upload-zone[data-state="dragover"] {
  border-color: var(--amber);
}

@media (hover: hover) {
  .upload-zone:hover { border-color: var(--amber); }
}

.upload-zone:has(:focus-visible) {
  outline: 2px solid var(--amber);
  outline-offset: 4px;
}

.upload-zone[data-state="error"]::after {
  content: "";
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgb(255 0 0 / 0.03) 2px,
    rgb(255 0 0 / 0.03) 4px
  );
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .upload-zone[data-state="error"] { animation: glitch 300ms steps(2) 1; }
}

@keyframes glitch {
  50% { transform: translateX(2px); }
}

/* Each validation message types itself out; clip-path avoids animating width. */
.log-line {
  display: block;
  white-space: nowrap;
}

@media (prefers-reduced-motion: no-preference) {
  .log-line { animation: type 600ms steps(30, end) 1 both; }
}

@keyframes type {
  from { clip-path: inset(0 100% 0 0); }
  to { clip-path: inset(0 0 0 0); }
}

/* Script sets --progress from 0 to 1 and mirrors it in aria-valuenow. */
.progress {
  height: 4px;
  margin-top: 1rem;
  background: color-mix(in srgb, var(--electric-green) 20%, transparent);
}

.progress-bar {
  height: 100%;
  background: var(--electric-green);
  transform: scaleX(var(--progress, 0));
  transform-origin: left;
  transition: transform 200ms linear;
}

@media (prefers-reduced-motion: reduce) {
  .progress-bar { transition: none; }
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
```

The focus ring sits on the label through `:has(:focus-visible)`, because the input itself is visually hidden. The validation log stays outside the label, so it is not read out as part of the input's name.

## 3. Meditation app testimonial carousel

```css
:root {
  --sand: #e8e0d5;
  --moss: #2f3a2c; /* text: 9.11:1 on sand */
  --sage: #9caa8e; /* decoration only: 1.88:1 on sand */
  --clay: #c4a882; /* decoration only: 1.73:1 on sand */
}

.testimonials {
  background: linear-gradient(160deg, var(--sand), color-mix(in srgb, var(--clay) 35%, var(--sand)));
  color: var(--moss);
  font-family: "Source Serif 4", Georgia, serif;
}

.testimonial-card blockquote {
  font-family: "Fraunces", Georgia, serif;
}

.avatar-frame {
  border-radius: 60% 40% 50% 50% / 50% 60% 40% 50%; /* organic, hand-drawn feel */
  outline: 2px solid var(--sage);
}

/* The breathing cycle runs only for users who have not asked for less motion. */
@media (prefers-reduced-motion: no-preference) {
  .testimonial-card { animation: breathe 8s ease-in-out infinite; }
  .carousel[data-paused] .testimonial-card { animation-play-state: paused; }
}

@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.95; }
  50% { transform: scale(1.02); opacity: 1; }
}
```

Give the carousel visible previous, next, and pause buttons. Auto-advance must stop on hover, on focus, and under reduced motion, so nobody has to chase moving text.

## 4. Fintech KPI dashboard

Five tokens per theme; dark is the default, and the toggle sets `data-theme="light"` on `<html>`.

```css
:root {
  --bg: #0b1622;
  --surface: #11202f;
  --text: #e6edf3;   /* 13.98:1 on surface */
  --muted: #8fa3b8;  /* 6.37:1 on surface */
  --accent: #3ee6a8; /* sparklines and pulse: 10.29:1 on surface */
}

:root[data-theme="light"] {
  --bg: #f4f7fa;
  --surface: #ffffff;
  --text: #0b1622;   /* 18.23:1 on surface */
  --muted: #4a5b6e;  /* 6.97:1 on surface */
  --accent: #0f8a5f; /* 4.36:1 on surface, above the 3:1 needed for graphics */
}

body { background: var(--bg); }

.stat-card {
  position: relative; /* anchors the pulse overlay */
  padding: 1.5rem;
  border: 1px solid color-mix(in srgb, var(--muted) 30%, transparent);
  border-radius: 12px;
  background: var(--surface);
  color: var(--text);
  font-family: "Inter", system-ui, sans-serif;
  font-variant-numeric: tabular-nums; /* figures keep their width on update */
}

.stat-card .label { color: var(--muted); }
.stat-card .sparkline { stroke: var(--accent); fill: none; }

.stat-card::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: 0 0 0 2px var(--accent);
  opacity: 0;
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .stat-card .value { transition: opacity 200ms ease-out; }
  .stat-card.is-updated::after { animation: pulse 1s ease-out 1; }
}

@keyframes pulse {
  40% { opacity: 0.5; }
}
```

```js
// One pulse per change: restart the animation by removing and re-adding the class.
function markUpdated(card) {
  card.classList.remove("is-updated");
  void card.offsetWidth; // force a reflow so the animation restarts
  card.classList.add("is-updated");
}
```
