# Pre-Delivery Checklist

Before delivering UI code, verify these items. Each one can be checked in the code, so the list works without a display; headless screenshots (SKILL.md, Pre-Delivery Verification) are extra evidence, not a requirement.

## Visual Quality

- [ ] No emojis used as icons (use SVG instead)
- [ ] All icons from consistent icon set (Heroicons/Lucide)
- [ ] Brand logos are correct (verified from Simple Icons)
- [ ] Hover states don't cause layout shift (hover rules change only colour, shadow, transform, or opacity)
- [ ] Use theme colors directly (bg-primary) not var() wrapper

## Interaction

- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

## Light/Dark Mode

- [ ] Light mode text has sufficient contrast (4.5:1 minimum)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes
- [ ] Both modes checked: every colour token has a light and a dark value, and each text pair meets 4.5:1 in both

## Layout

- [ ] Floating elements have proper spacing from edges
- [ ] No content hidden behind fixed navbars
- [ ] Responsive at 375px, 768px, 1024px, 1440px (media or container queries cover each width)
- [ ] No horizontal scroll on mobile (no fixed width above 375px, no `100vw` that ignores the scrollbar)

## Accessibility

- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator

## Performance

- [ ] Images optimized (WebP, srcset, lazy loading)
- [ ] Animations use transform/opacity only
- [ ] Content doesn't jump during loading (images and embeds reserve space with width/height or `aspect-ratio`)
- [ ] Skeleton screens for async content
