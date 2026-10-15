# UI and UX Rules

## Contents

1. [Priority 1: Accessibility (CRITICAL)](#priority-1-accessibility-critical)
2. [Priority 2: Touch and Interaction (CRITICAL)](#priority-2-touch-and-interaction-critical)
3. [Priority 3: Performance (HIGH)](#priority-3-performance-high)
4. [Priority 4: Layout and Responsive (HIGH)](#priority-4-layout-and-responsive-high)
5. [Priority 5: Typography and Colour (MEDIUM)](#priority-5-typography-and-colour-medium)
6. [Priority 6: Animation (MEDIUM)](#priority-6-animation-medium)
7. [Priority 7: Style Selection (MEDIUM)](#priority-7-style-selection-medium)
8. [Priority 8: Charts and Data (LOW)](#priority-8-charts-and-data-low)
9. [Common Pitfalls](#common-pitfalls)

30+ rules, ordered by priority: when auditing an interface, check Priority 1 first and work down. Every table uses the Do/Don't/Why format.

## Priority 1: Accessibility (CRITICAL)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Colour contrast** | 4.5:1 for body text, 3:1 for large text, focus rings, and input borders | Light grey on white | Fails WCAG AA, excludes low-vision users |
| **Focus states** | Visible `:focus-visible` rings on interactive elements | Remove the outline with `outline-none` | Keyboard users can't navigate |
| **Alt text** | Descriptive alt text for meaningful images | Empty alt on informative images | Screen readers skip content |
| **Aria labels** | `aria-label` on icon-only buttons | Icon button with no label | Announced as "button" with no context |
| **Keyboard nav** | Tab order matches visual order | Positive `tabindex` values | Confusing navigation flow |
| **Form labels** | `<label>` with a `for` attribute | Placeholder as the only label | Disappears on input, fails accessibility |
| **Reduced motion** | Reduce or stop animation under `prefers-reduced-motion: reduce` | Endless or large motion with no off switch | Motion can make vestibular-sensitive users ill |

## Priority 2: Touch and Interaction (CRITICAL)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Touch target** | At least 44x44px (48x48dp on Android) | 24px tap areas | Frustrating on mobile, accessibility fail |
| **Hover vs tap** | Click/tap for primary interactions; decorative hover inside `@media (hover: hover)` | Hover-only reveals on mobile | Touch devices have no hover state |
| **Loading buttons** | Disable the button during async operations | Allow repeated clicks | Duplicate submissions, race conditions |
| **Error feedback** | Clear error messages next to the problem | Generic "Error" at the top of the page | User can't find what went wrong |
| **Cursor pointer** | `cursor: pointer` on every clickable or hoverable card | Default cursor on interactive elements | No sign the element is clickable |

## Priority 3: Performance (HIGH)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Image optimisation** | WebP or AVIF, `srcset`, lazy loading below the fold | Uncompressed PNG, every image loaded eagerly | Slow page load, wasted bandwidth |
| **Content jumping** | Reserve space for async content | Let the layout shift on load | Poor CLS score, jarring UX |
| **Font loading** | `font-display: swap` and a metric-close fallback stack | Invisible text while fonts download | Blank text on slow connections |

## Priority 4: Layout and Responsive (HIGH)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Viewport meta** | `width=device-width, initial-scale=1` | Fixed-width viewport | Broken on mobile devices |
| **Readable font** | At least 16px body text on mobile | 12px body text | Unreadable, users pinch-zoom |
| **No horizontal scroll** | Content fits the viewport width | `100vw` without accounting for the scrollbar | Horizontal scroll breaks mobile UX |
| **Z-index scale** | A defined scale (10, 20, 30, 50) | Random `z-index: 9999` | Z-index wars, unpredictable stacking |
| **Fixed-header offset** | Pad content and set `scroll-padding-top` to the header height | Let content and anchor targets hide behind a fixed header | Content obscured |
| **Consistent max-width** | One container width (`max-w-6xl` or `max-w-7xl`) | Mixed container widths | Inconsistent alignment |

## Priority 5: Typography and Colour (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Line height** | 1.5-1.75 for body text | `line-height: 1` or 1.2 on body text | Text feels cramped, hard to read |
| **Line length** | 65-75 characters per line | Full-width paragraphs | Eye-tracking fatigue |
| **Font pairing** | Match heading and body font personalities | Playful heading + formal body | Visual discord |
| **Text contrast, light mode** | A `--text` token at 4.5:1 or more on its surface (for example `#0F172A`, 17.9:1 on white) | `#94A3B8` (slate-400, 2.6:1 on white) for body text | Fails contrast requirements |
| **Muted text, light mode** | A `--muted` token at 4.5:1 or more on every surface it sits on (for example `#475569`, 7.6:1 on white, which leaves margin for tinted surfaces) | slate-400 or lighter | Too light to read |
| **Glass card, light mode** | A surface token at 80% opacity or more: `color-mix(in srgb, var(--surface) 80%, transparent)` | A surface at 10% opacity | Content unreadable in light mode |
| **Border visibility** | Card dividers from a `--border` token that shows in both modes; input borders from a token at 3:1 or more (for example `#6B7280`, 4.8:1 on white) | A white border at 10% opacity in light mode | Borders disappear, and users can't find the input edges |

## Priority 6: Animation (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Duration** | 150-300ms for hover, focus, and press feedback | Under 100ms, or over 500ms for feedback | Too fast reads as a glitch; too slow feels sluggish |
| **Layout-safe properties** | Animate `transform` and `opacity` | Animate `width`, `height`, `margin`, or `top` | Triggers layout on every frame, janky animation |
| **Loading states** | Skeleton screens or spinners | Blank screen during load | User thinks the page is broken |
| **Ambient loops** | Slow decorative loops only, paused under reduced motion | Fast or attention-grabbing loops beside text | Distracts from reading |

## Priority 7: Style Selection (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Style match** | Match the style to the product type | Playful style for a banking app | Undermines trust and credibility |
| **Consistency** | Same style across all pages | Different styles per page | Feels like different products |
| **No emoji icons** | SVG icons from one set (the project's own, otherwise Lucide) | Emojis such as 🏠 or 🔥 as UI icons | Inconsistent rendering across platforms |
| **Consistent icon sizing** | One `viewBox` (24x24) at one size (`w-6 h-6`) | Mixed icon sizes | Visual chaos |
| **Correct brand logos** | Official SVG from the brand or Simple Icons | Logo paths guessed from memory | Wrong logos damage credibility |

## Priority 8: Charts and Data (LOW)

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Chart type** | Match the chart type to the question and data | Pie chart for 20 categories | The wrong chart hides the insight |
| **Colour guidance** | Colour-blind-safe palettes plus labels or patterns | Red/green as the only distinction | Colour-blind users can't tell series apart |
| **Data table** | A table alternative next to the chart | Chart-only data | Screen readers can't parse charts |

---

## Common Pitfalls

| Rule | Do | Don't | Why |
|------|----|-------|-----|
| **Stable hover states** | Change colour, shadow, opacity, or transform on hover | Change border width, padding, or font weight on hover | Those change the box size and shift the layout |
| **Hover feedback** | Visible change in colour, shadow, or border | No sign the element is interactive | Missed interactions |
| **Smooth transitions** | `transition-colors duration-200` | Instant state changes | Feels broken |
| **Outline removal** | Replace the default outline with a styled `:focus-visible` ring | `outline: none` with nothing in its place | Keyboard focus disappears |
| **Overlay clicks** | `pointer-events: none` on decorative overlays | Full-size `::before`/`::after` layers over buttons | Overlays swallow clicks |
