# UX Guidelines

## Contents

1. [Priority 1: Accessibility (CRITICAL)](#priority-1-accessibility-critical)
2. [Priority 2: Touch & Interaction (CRITICAL)](#priority-2-touch--interaction-critical)
3. [Priority 3: Performance (HIGH)](#priority-3-performance-high)
4. [Priority 4: Layout & Responsive (HIGH)](#priority-4-layout--responsive-high)
5. [Priority 5: Typography & Color (MEDIUM)](#priority-5-typography--color-medium)
6. [Priority 6: Animation (MEDIUM)](#priority-6-animation-medium)
7. [Priority 7: Style Selection (MEDIUM)](#priority-7-style-selection-medium)
8. [Priority 8: Charts & Data (LOW)](#priority-8-charts--data-low)
9. [Common Pitfalls (Do/Don't Quick Reference)](#common-pitfalls-dodont-quick-reference)

30+ rules organised by priority. All tables follow Do/Don't/Why format.

## Priority 1: Accessibility (CRITICAL)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Color contrast** | Minimum 4.5:1 ratio for normal text | Use light gray on white | Fails WCAG AA, excludes low-vision users |
| **Focus states** | Visible focus rings on interactive elements | Remove outline with `outline-none` | Keyboard users can't navigate |
| **Alt text** | Descriptive alt text for meaningful images | Empty alt on informative images | Screen readers skip content |
| **Aria labels** | `aria-label` for icon-only buttons | Icon button with no label | Announced as "button" with no context |
| **Keyboard nav** | Tab order matches visual order | Random tabindex values | Confusing navigation flow |
| **Form labels** | Use `<label>` with `for` attribute | Placeholder as only label | Disappears on input, fails a11y |

## Priority 2: Touch & Interaction (CRITICAL)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Touch target** | Minimum 44x44px touch targets | Small 24px tap areas | Frustrating on mobile, accessibility fail |
| **Hover vs tap** | Use click/tap for primary interactions | Hover-only reveals on mobile | Touch devices have no hover state |
| **Loading buttons** | Disable button during async operations | Allow multiple clicks | Duplicate submissions, race conditions |
| **Error feedback** | Clear error messages near the problem | Generic "Error" at page top | User can't find what went wrong |
| **Cursor pointer** | Add `cursor-pointer` to all clickable cards | Default cursor on interactive elements | No indication element is clickable |

## Priority 3: Performance (HIGH)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Image optimization** | Use WebP, srcset, lazy loading | Uncompressed PNG, eager load all | Slow page load, wasted bandwidth |
| **Content jumping** | Reserve space for async content | Let layout shift on load | Poor CLS score, jarring UX |

## Priority 4: Layout & Responsive (HIGH)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Viewport meta** | `width=device-width, initial-scale=1` | Fixed width viewport | Broken on mobile devices |
| **Readable font** | Minimum 16px body text on mobile | 12px body text | Unreadable, users pinch-zoom |
| **No horizontal scroll** | Ensure content fits viewport width | 100vw without accounting for scrollbar | Horizontal scroll breaks mobile UX |
| **Z-index scale** | Define scale (10, 20, 30, 50) | Random z-index: 9999 | Z-index wars, unpredictable stacking |

## Priority 5: Typography & Color (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Line height** | Use 1.5-1.75 for body text | Line-height: 1 or 1.2 | Text feels cramped, hard to read |
| **Line length** | Limit to 65-75 characters per line | Full-width paragraphs | Eye tracking fatigue |
| **Font pairing** | Match heading/body font personalities | Playful heading + formal body | Visual discord, unprofessional |

## Priority 6: Animation (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Duration** | Use 150-300ms for micro-interactions | 50ms (too fast) or 800ms (sluggish) | Sweet spot for perceived responsiveness |
| **Transform perf** | Use `transform`/`opacity` only | Animate `width`, `height`, `top` | Triggers layout/paint, janky animation |
| **Loading states** | Skeleton screens or spinners | Blank screen during load | User thinks page is broken |

## Priority 7: Style Selection (MEDIUM)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Style match** | Match style to product type | Playful style for banking app | Undermines trust and credibility |
| **Consistency** | Same style across all pages | Different styles per page | Feels like different products |
| **No emoji icons** | Use SVG icons (Heroicons, Lucide) | Emojis as UI icons | Inconsistent rendering, unprofessional |

## Priority 8: Charts & Data (LOW)

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Chart type** | Match chart type to data type | Pie chart for 20 categories | Wrong chart obscures insights |
| **Color guidance** | Use accessible color palettes | Red/green only distinction | Color blind users can't differentiate |
| **Data table** | Provide table alternative | Chart-only data presentation | Screen readers can't parse charts |

---

## Common Pitfalls (Do/Don't Quick Reference)

### Icons & Visual Elements

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **No emoji icons** | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🏠 or 🔥 as UI icons | Inconsistent cross-platform, unprofessional |
| **Stable hover states** | Use color/opacity transitions on hover | Use scale transforms that shift layout | Layout shift is jarring |
| **Correct brand logos** | Research official SVG from Simple Icons | Guess or use incorrect logo paths | Wrong logos damage credibility |
| **Consistent icon sizing** | Use fixed viewBox (24x24) with w-6 h-6 | Mix different icon sizes randomly | Visual chaos, unprofessional |

### Interaction & Cursor

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Cursor pointer** | Add `cursor-pointer` to all clickable/hoverable cards | Leave default cursor on interactive elements | User doesn't know it's clickable |
| **Hover feedback** | Provide visual feedback (color, shadow, border) | No indication element is interactive | Missed interactions |
| **Smooth transitions** | Use `transition-colors duration-200` | Instant state changes or too slow (>500ms) | Feels broken or sluggish |

### Light/Dark Mode Contrast

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Glass card light mode** | Use `bg-white/80` or higher opacity | Use `bg-white/10` (too transparent) | Content unreadable in light mode |
| **Text contrast light** | Use `#0F172A` (slate-900) for text | Use `#94A3B8` (slate-400) for body text | Fails contrast requirements |
| **Muted text light** | Use `#475569` (slate-600) minimum | Use gray-400 or lighter | Too light to read |
| **Border visibility** | Use `border-gray-200` in light mode | Use `border-white/10` (invisible) | Borders disappear |

### Layout & Spacing

| Rule | Do | Don't | Why |
|------|----|----- |-----|
| **Floating navbar** | Add `top-4 left-4 right-4` spacing | Stick navbar to `top-0 left-0 right-0` | Looks dated, less modern |
| **Content padding** | Account for fixed navbar height | Let content hide behind fixed elements | Content obscured |
| **Consistent max-width** | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths | Inconsistent alignment |
