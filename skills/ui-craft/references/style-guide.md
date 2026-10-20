# Style Guide Quick Reference

Quick lookups for tone, styles, colours, typography, and layouts by product type and industry. These are starting points: commit to one direction, then push it past the obvious.

## Tone Selection Framework

| Audience / context | Recommended tones | When to use |
|--------------------|-------------------|-------------|
| Luxury/high-end product | Refined, editorial, art deco | Premium pricing, exclusivity |
| Developer tools/SaaS | Industrial, brutalist, minimal | Technical users, clarity matters |
| Consumer app/social | Playful, organic, soft/pastel | Broad appeal, approachability |
| Portfolio/creative | Maximalist, retro-futuristic | Standing out, showcasing range |
| E-commerce/retail | Editorial, luxury, organic | Trust, aspiration, conversion |
| Dashboard/admin | Industrial, utilitarian, minimal | Information density, efficiency |

## Style Recommendations by Product Type

| Product type | Recommended styles | Why |
|--------------|-------------------|-----|
| SaaS/Dashboard | Minimal, flat, dark mode | Clean data presentation, reduces eye strain |
| E-commerce | Clean, card-based, soft shadows | Product focus, easy scanning |
| Portfolio | Bento grid, brutalism, editorial | Creative expression, memorable |
| Healthcare | Soft, rounded, light mode | Trust, calm, accessibility |
| Fintech | Minimal, professional, dark or light | Trust, precision, data clarity |
| Beauty/Spa | Elegant, glassmorphism, soft gradients | Luxury feel, sophistication |
| Gaming | Neon, cyberpunk, high contrast | Energy, excitement |
| Education | Friendly, colourful, rounded | Approachable, engaging |

## Colour Palette by Industry

Each industry has hues users expect. Keep the expected hue so the product reads right, but do not ship the framework default for it: Tailwind's `blue-500`, `indigo-500`, and `purple-500` read as a template. The examples below shift depth and pair the hue with an unexpected accent.

| Industry | Expected hues | A less generic take (example) | Mood |
|----------|---------------|-------------------------------|------|
| SaaS | Blue, indigo | Ink navy #14213D with signal coral #FF6B4A | Trust with energy |
| E-commerce | Orange, rose | Terracotta #B04A35 on warm cream #F6EFE6 | Warm, tactile |
| Healthcare | Teal, cyan | Deep spruce #1F4E4A with soft mint #DDF2EA | Calm, trustworthy |
| Fintech | Navy, emerald | Midnight #0B1F33 with brass #B08D57 | Secure, premium |
| Beauty | Rose, lavender | Aubergine #4A2C40 with blush clay #D8A39D | Soft luxury |
| Gaming | Purple, cyan | Acid lime #C6FF3D and hot magenta #FF2E88 on near-black #0A0A0F | Loud, kinetic |
| Education | Yellow, green | Deep teal #12464F with sunflower #F2B33D | Friendly, focused |

Each two-colour pair above measures at least 4.5:1; in the Gaming row, lime and magenta each pass on the near-black, but not on each other (2.96:1). Derive the full token set (background, surface, text, muted text, accent) from it, then check every new text pair with `scripts/contrast.py`.

## Typography Pairing Guide

| Style | Heading font | Body font | Use case |
|-------|--------------|-----------|----------|
| Elegant luxury | Playfair Display | Lato | Beauty, fashion |
| Editorial sophisticated | Fraunces | Source Sans 3 | Magazines, blogs |
| Friendly approachable | Nunito | Open Sans | Education, consumer |
| Technical precision | JetBrains Mono | IBM Plex Sans | Developer tools |
| Playful creative | Pacifico | Quicksand | Kids, gaming |
| Data-dense dashboard | Inter, tabular figures | Inter | Dashboards and admin tables only (the one Inter exception) |

## Layout Patterns

| Pattern | Structure | Best for |
|---------|-----------|----------|
| Hero-centric | Large hero + stacked sections | Landing pages |
| Dashboard grid | Sidebar + main content grid | Admin panels |
| Bento grid | Asymmetric card grid | Portfolios, features |
| Card gallery | Uniform card grid | E-commerce, listings |
| Single column | Centred narrow content | Blogs, documentation |
| Split screen | 50/50 content sections | Comparisons, sign-up |

## Edge Case Adaptations

| Context | Adaptation |
|---------|------------|
| Mobile-first | Replace hover effects with tap feedback and focus states |
| Performance-critical | Fewer animations, and no animated `blur()` over a large area (`animation-patterns.md`, Performance Rules) |
| Existing design systems | Adapt patterns to their tokens rather than inventing new ones |
| RTL languages | Use logical CSS properties (`margin-inline-start`, `inset-inline-end`) instead of left/right |
