# Animation Patterns

Durations live in `ui-rules.md`, Priority 6. This file covers where to spend motion, how to keep it smooth, how to switch it off, and which tool to use.

## Priority Hierarchy

Not every element needs animation. Prioritise by impact:

| Priority | Area | Purpose |
|----------|------|---------|
| 1 | Hero intro | First impression, brand personality |
| 2 | Hover interactions | Feedback, discoverability |
| 3 | Content reveal | Guide attention, reduce cognitive load |
| 4 | Background effects | Atmosphere, depth |
| 5 | Navigation transitions | Spatial awareness, continuity |

## Performance Rules

Animate `transform` and `opacity`: the browser composites them without recalculating layout. Never animate layout properties.

```css
/* DO: composited properties */
transform: translateY(20px);
opacity: 0.5;

/* DON'T: layout properties */
margin-top: 20px;
height: 100px;
width: 200px;
```

**Why:** animating `margin`, `height`, or `width` forces a layout recalculation on every frame, which drops frames on lower-end devices. `filter` and colour changes skip layout but still repaint, so keep them to small elements; a `blur()` over a large area is expensive.

## Reduced Motion

Write motion as an enhancement that only runs when the user has not asked for less:

```css
.reveal { opacity: 1; }

@media (prefers-reduced-motion: no-preference) {
  .js .reveal { opacity: 0; transform: translateY(16px); }
  .js .reveal.is-visible {
    opacity: 1;
    transform: none;
    transition: opacity 600ms ease-out, transform 600ms ease-out;
  }
}
```

- The hidden state applies only when a script has added the `js` class to `<html>`, so content stays visible if JavaScript fails or a headless screenshot fires early.
- Under `reduce`, replace movement with an instant change or a short fade; stop every infinite loop.
- In script-driven motion, read `matchMedia('(prefers-reduced-motion: reduce)').matches` (in React with Motion, `useReducedMotion()`).

## Animation Triggers

| Trigger | Implementation |
|---------|----------------|
| Page load | CSS `animation` with `animation-delay` for stagger |
| Scroll into view | `IntersectionObserver` adding a class once, then unobserving |
| Hover | CSS `:hover` (Tailwind `hover:`) inside `@media (hover: hover)` |
| Click / tap | A state change: a class toggle in plain JS, `useState` in React, a `ref` in Vue |

## Tech Stack Ladder

Choose the lightest tool that meets the requirement, and escalate only when it cannot express the interaction.

| Level | Tool | When to use |
|-------|------|-------------|
| 1 (default) | CSS transitions and keyframes (or Tailwind's transition utilities); Vue's `<Transition>` and Svelte's `transition:` in those stacks | Fades, slides, hover states, stagger delays |
| 2 | Motion for React (`motion` package, formerly Framer Motion), when installed | Exit animations, gestures, layout animations, coordinated sequences |
| 3 | GSAP, only when already installed | Timeline-based sequences, scroll-driven narratives |

Most interfaces need nothing beyond Level 1. Adding a library for a single effect costs more in bundle size than it gives back.
