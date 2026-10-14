---
name: frontend-design
description: "Creates and improves distinctive, production-grade frontend interfaces that avoid generic AI aesthetics. Includes style/color/typography guides by industry, 30+ UX rules, 25+ chart types, and 10 tech stacks. Use when designing components, building pages, choosing palettes, implementing UI patterns, or improving existing interfaces."
license: MIT
---

# Frontend Design Intelligence

Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

## When to Apply

Use when the user works on UI/UX design, components, layouts, landing pages, dashboards, colour palettes, typography, design tokens, accessibility visuals, charts, responsive design, animations, visual effects, form styling, or theme switching. Also use when auditing or refactoring existing interfaces.

Skip for backend logic, database work, auth flows, DevOps, algorithms, or CLI tools.

---

<instructions>

## Design Thinking

Before coding, understand the context and commit to a **BOLD** aesthetic direction.

**Conflicting requirements?** When tones clash (e.g., "playful but professional"), pick one as primary driver and use the other as accent. A professional base with playful micro-interactions differs from a playful base with professional typography. Identify which audience need is primary.

| Question | Purpose |
|----------|---------|
| **Purpose** | What problem does this interface solve? Who uses it? |
| **The "Why" Factor** | Before placing any element, calculate its purpose. If it has no purpose, delete it. Every pixel must earn its place. |
| **Tone** | Pick from `references/style-guide.md` — Tone Selection Framework |
| **Constraints** | Technical requirements (framework, performance, accessibility) |
| **Differentiation** | What makes this UNFORGETTABLE? What's the one thing someone will remember? |

**Stack Adaptation:** Adapt to the user's stack — if React, write JSX; if Vue, write Vue; if vanilla HTML/CSS, use that. **Unfamiliar stack?** Run a live search (context7, web) to learn its conventions before implementing. Fallback: vanilla HTML/CSS patterns.

**Library Discipline:** When a UI library (Shadcn, Radix, MUI, Headless UI) is detected in the project, use it instead of building custom components. Do not pollute the codebase with redundant CSS. *Exception:* You may wrap/style library components for distinctive aesthetics, but the underlying primitive must come from the library.

**When in doubt, reduce:** Reduction is the ultimate sophistication. Remove until it breaks, then add back the last thing.

---

## Quick Workflow Checklist

Copy this before starting:

```text
Frontend Design Progress:
- [ ] Purpose identified: _____
- [ ] Tone chosen: _____
- [ ] Key differentiator: _____
- [ ] Typography: display + body font selected (not Inter/Roboto/system)
- [ ] Color: 3-5 CSS custom properties defined (no hardcoded hex outside vars)
- [ ] Motion: entry animation + 1-2 hover/scroll interactions
- [ ] Layout: grid/flexbox structure with intentional spacing
- [ ] Code complete: renders without console errors
- [ ] Polish: all interactive elements have :hover + :focus-visible states
```

Then build working front-end code that is:
- **Production-ready**: robust, secure, built to ship
- **Fully functional**: no stubs, no broken states, no "todo later" gaps
- **Visually standout**: bold, memorable, instantly recognisable
- **Design-led**: one clear aesthetic, consistent patterns, no visual drift
- **Detail-perfect**: spacing, typography, motion, states, responsiveness polished

## Pre-Delivery Verification

Before delivering, verify every item in the workflow checklist above is checked. Then run through `references/checklist.md` (visual quality, interaction, light/dark mode, layout, accessibility, performance). Fix any failures before presenting the final code.

---

## Frontend Aesthetics Guidelines

### Typography

Choose fonts that are beautiful, unique, and interesting. **Avoid defaulting to generic fonts like Arial and Inter** — they signal template-level work. Opt for distinctive choices that elevate aesthetics. Pair a distinctive display font with a refined body font. Exception: Inter is acceptable for data-focused dashboards where neutral typography aids readability (see `references/style-guide.md`).

**Default if uncertain:** Serif display (Playfair Display, Fraunces) + humanist sans body (Source Sans 3, Work Sans).

See `references/style-guide.md` for full Typography Pairing Guide.

### Color & Theme

Commit to a cohesive aesthetic. Use CSS variables for consistency. **Dominant colors with sharp accents outperform timid, evenly-distributed palettes.**

See `references/style-guide.md` for Color Palette by Industry.

### Motion

Use animations for effects and micro-interactions. Prioritise CSS-only solutions for HTML. Use Motion library for React when available.

**Focus on high-impact moments:** One well-orchestrated page load with staggered reveals (`animation-delay`) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.

**Animate compositor properties** (`transform`, `opacity`, `filter`). Never animate layout properties (`margin`, `height`, `width`).

See `references/animation-patterns.md` for priority hierarchy, performance rules, trigger patterns, and tech stack selection.

### Spatial Composition

Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.

For data-dense interfaces (dashboards, tables), prioritize clarity over surprise. **Perfect spacing is invisible** — users feel it without noticing.

### "Invisible" UX

The best interactions feel effortless:
- Micro-interactions that guide without demanding attention
- Smooth transitions that never interrupt flow
- Feedback that confirms without congratulating

Friction should be zero unless intentionally designed (e.g., confirmation dialogs for destructive actions).

### Backgrounds & Visual Details

Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures:
- Gradient meshes, noise textures, geometric patterns
- Layered transparencies, dramatic shadows
- Decorative borders, custom cursors, grain overlays

### Accessibility

| Rule | Do | Don't |
|------|----|----- |
| Color contrast | 4.5:1 minimum for text | Light gray on white |
| Focus states | Visible `:focus-visible` on all interactive | Remove outline with `outline-none` |
| Semantic HTML | Use `<article>`, `<section>`, `<nav>`, `<main>` | `<div>` soup everywhere |
| ARIA | Use only when semantic HTML is insufficient | ARIA as first choice |

---

## What to NEVER Do

**NEVER use generic AI-generated aesthetics:**

| Anti-Pattern | Why It Fails |
|--------------|--------------|
| Overused fonts (Inter, Roboto, Arial, system) | Instantly recognizable as template |
| Purple gradients on white backgrounds | Cliché, seen everywhere |
| Predictable layouts and component patterns | Template-like, not designed |
| Cookie-cutter design lacking context | No character, forgettable |
| Converging on common choices across generations | Every output looks the same — the opposite of design |

**If it looks like a template, it is wrong.** Templates are starting points to escape from, not destinations.

**Match implementation complexity to aesthetic vision:**
- Maximalist designs need elaborate code with extensive animations
- Minimalist designs need restraint, precision, careful spacing

**No two designs should look the same.** Vary between light and dark themes, different fonts, different aesthetics. Interpret creatively and make unexpected choices that feel genuinely designed for the context.

</instructions>

---

## Examples

<example name="Luxury Watch Pricing Card">

**Request:** "Build a pricing card component for a luxury watch e-commerce site"

**Checklist:**
```text
- [x] Purpose: Convert browsers to buyers for $5k+ watches
- [x] Tone: Editorial/magazine with art deco accents
- [x] Differentiator: Cinematic hover reveal with gold foil texture
- [x] Typography: Playfair Display (display) + Cormorant Garamond (body)
- [x] Color: Deep charcoal (#1a1a1a), warm gold (#c9a962), cream (#f5f0e8)
- [x] Motion: Slow 0.8s ease-out transitions, parallax depth on hover
- [x] Layout: Asymmetric with product image bleeding edge
```

**Before (generic):**
```jsx
// BAD: system fonts, no theming, basic structure
<div className="bg-white rounded-lg shadow-md p-6">
  <img src={watch.image} alt={watch.name} className="w-full rounded" />
  <h3 className="text-xl font-semibold mt-4">{watch.name}</h3>
  <p className="text-gray-600">{watch.description}</p>
  <span className="text-2xl font-bold">${watch.price}</span>
  <button className="bg-blue-500 text-white px-4 py-2 rounded">Add to Cart</button>
</div>
```

**After (distinctive):**
```jsx
// GOOD: editorial luxury — CSS custom properties, distinctive typography, intentional motion
<article className="pricing-card" style={{
  '--gold': '#c9a962',
  '--charcoal': '#1a1a1a',
  '--cream': '#f5f0e8',
}}>
  <div className="card-image">
    <img src={watch.image} alt="" />
    <div className="gold-border-accent" aria-hidden="true" />
  </div>
  <header className="card-content">
    <h3 className="font-playfair tracking-tight text-cream">{watch.name}</h3>
    <p className="font-cormorant text-cream/70">{watch.description}</p>
  </header>
  <footer className="card-footer">
    <span className="price font-playfair">
      <span className="currency">$</span>
      {watch.price.toLocaleString()}
    </span>
    <button className="cta-button">View Timepiece</button>
  </footer>
</article>
```

```css
.pricing-card {
  background: var(--charcoal);
  position: relative;
  overflow: hidden;
}

.pricing-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url('/noise.svg');
  opacity: 0.03;
  pointer-events: none;
}

.gold-border-accent {
  position: absolute;
  inset: 0;
  border: 1px solid var(--gold);
  opacity: 0;
  transition: opacity 0.8s ease-out;
}

.pricing-card:hover .gold-border-accent {
  opacity: 1;
}

.cta-button:focus-visible {
  outline: 2px solid var(--gold);
  outline-offset: 3px;
}
```

</example>

<example name="Developer CLI File Upload">

**Request:** "Create a file upload component for a developer CLI tool dashboard"

**Checklist:**
```text
- [x] Purpose: Drag-drop config files, show validation status
- [x] Tone: Industrial/utilitarian with brutalist accents
- [x] Differentiator: Terminal-style feedback with typing animation
- [x] Typography: JetBrains Mono (monospace throughout)
- [x] Color: Near-black (#0d0d0d), electric green (#00ff88), amber warnings (#ffaa00)
- [x] Motion: Glitch effect on error, smooth progress bar
- [x] Layout: Centered card with generous padding, sharp corners
```

**Key implementation:**
- Monospace everything — even labels feel like code
- Drop zone has dashed border with ASCII-art corners
- File validation shows as terminal output with typing effect
- Error states use red scanlines overlay

```css
.upload-zone {
  font-family: 'JetBrains Mono', monospace;
  background: var(--near-black);
  border: 2px dashed var(--electric-green);
}

.upload-zone.error::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(255, 0, 0, 0.03) 2px,
    rgba(255, 0, 0, 0.03) 4px
  );
  pointer-events: none;
}
```

</example>

<example name="Meditation App Testimonials">

**Request:** "Design a testimonial carousel for a meditation app landing page"

**Checklist:**
```text
- [x] Purpose: Build trust, show transformation stories
- [x] Tone: Organic/natural with soft/pastel warmth
- [x] Differentiator: Breathing animation synced to testimonial transitions
- [x] Typography: Fraunces (display) + Source Serif 4 (body)
- [x] Color: Warm sand (#e8e0d5), sage green (#9caa8e), soft clay (#c4a882)
- [x] Motion: 4-second breathing pulse, gentle parallax on quotes
- [x] Layout: Full-width with organic blob shapes framing content
```

**Key implementation:**
- Background gradient shifts slowly like a sunset
- Testimonial cards have organic border-radius (varied corners)
- Avatar photos have hand-drawn circle borders (SVG filter)
- Transitions match breathing rhythm (4s inhale, 4s exhale)

```css
.testimonial-card {
  animation: breathe 8s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 0.95; }
  50% { transform: scale(1.02); opacity: 1; }
}

.avatar-frame {
  border-radius: 60% 40% 50% 50% / 50% 60% 40% 50%;
  /* Organic, hand-drawn feel */
}
```

</example>

<example name="SaaS Analytics Dashboard">

**Request:** "Build a KPI dashboard for a fintech analytics platform"

**Checklist:**
```text
- [x] Purpose: Display real-time financial metrics for portfolio managers
- [x] Tone: Minimal/professional with precise data hierarchy
- [x] Differentiator: Sparkline-integrated stat cards with subtle pulse on live updates
- [x] Typography: Inter (body, exception: data-focused dashboard) + Tabular Nums for figures
- [x] Color: Deep navy (#0f172a), emerald accent (#10b981), neutral slate (#94a3b8)
- [x] Motion: 200ms fade for data updates, smooth chart transitions
- [x] Layout: Sidebar + responsive grid with consistent 24px gap
```

**Key implementation:**
- Stat cards use CSS `font-variant-numeric: tabular-nums` so numbers do not shift width on update
- Sparklines rendered inline within cards (no separate chart library needed for micro-trends)
- Live-update pulse uses a brief `box-shadow` animation on the card border, not layout-shifting scale
- Dark mode default with a light mode toggle that swaps CSS custom properties

```css
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  font-variant-numeric: tabular-nums;
}

.stat-card[data-live]::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: 0 0 0 2px var(--emerald);
  opacity: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0; }
  50% { opacity: 0.4; }
}
```

</example>

---

## Reference Files

For quick lookups and detailed guidelines:

| Reference | Content |
|-----------|---------|
| `references/style-guide.md` | Styles, colors, typography, layouts by product type |
| `references/ui-rules.md` | 30+ UX guidelines (Do/Don't/Why tables) |
| `references/checklist.md` | Pre-delivery verification checklist |
| `references/animation-patterns.md` | Animation priorities, performance rules, triggers, tech stack ladder |
| `references/chart-types.md` | 25+ chart types with selection guidelines |
| `references/search-domains.md` | Technology stacks with code snippets |

---

Every interface must look intentionally designed for its specific context. Commit fully to the chosen aesthetic and deliver code that ships without further polish.
