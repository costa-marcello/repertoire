# Pre-Delivery Checklist

Walk this list against the source code in step 3 of Pre-Delivery Verification. Every item can be checked without a display; headless screenshots are extra evidence, not a requirement.

## Visual Quality

- [ ] No emojis used as icons; icons come from one SVG set (the project's own, otherwise Lucide)
- [ ] Brand logos come from the brand's official assets or Simple Icons, never redrawn from memory
- [ ] Hover rules change only colour, shadow, transform, or opacity, so nothing shifts layout
- [ ] Colours come from tokens, with no hex outside the token definitions; in Tailwind, tokens are registered in the theme and used as `bg-primary`, not `bg-[var(--primary)]`
- [ ] The display and body fonts are actually loaded, and each font stack ends with a fallback

## Interaction

- [ ] Clickable elements show `cursor: pointer` (Tailwind `cursor-pointer`)
- [ ] Hover gives clear visual feedback; decorative hover effects sit inside `@media (hover: hover)`
- [ ] Hover, focus, and press transitions last 150-300ms
- [ ] Every interactive element has a visible `:focus-visible` style
- [ ] Touch targets are at least 44x44px

## Light and Dark Mode (when the design ships both)

- [ ] Every colour token has a light and a dark value
- [ ] The contrast check passes in both modes
- [ ] Glass and translucent surfaces stay readable in light mode
- [ ] Borders are visible in both modes

## Layout

- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px (media or container queries cover each width)
- [ ] No horizontal scroll on mobile (no fixed width above 375px, no `100vw` that ignores the scrollbar)

## Accessibility

- [ ] Every text/background pair passes `scripts/contrast.py`: 4.5:1 for body text, 3:1 for large text, focus rings, and input borders
- [ ] Meaningful images have descriptive alt text; decorative ones use `alt=""`
- [ ] Form inputs have labels
- [ ] Colour is not the only indicator
- [ ] Animations stop or shrink under `prefers-reduced-motion: reduce`, and every loop has an off switch

## Performance

- [ ] Images optimised (WebP or AVIF, `srcset`, `loading="lazy"` below the fold)
- [ ] No animation or transition changes layout properties (`width`, `height`, `margin`, `top`)
- [ ] Content doesn't jump during loading (images and embeds reserve space with width/height or `aspect-ratio`)
- [ ] Skeleton screens for async content
