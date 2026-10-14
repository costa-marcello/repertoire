# Search Domains Reference

## Contents

1. [Available Domains](#available-domains)
2. [Available Stacks](#available-stacks)
3. [Rule Categories by Priority](#rule-categories-by-priority)

This reference defines the design knowledge domains and technology stacks available within this skill. When applying the frontend-design workflow:

1. **Domains** categorize design knowledge (styles, colors, typography, etc.) - use them to identify which aspect of design you're working on and find relevant recommendations
2. **Stacks** provide implementation-specific best practices - select based on the user's technology choice (default: `html-tailwind`)
3. **Rule Categories** prioritize which guidelines to check first during the verification step

## Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings, Google Fonts | elegant, playful, professional, modern |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategies | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js performance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | Web interface guidelines | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI prompts, CSS keywords | (style name) |

## Available Stacks

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities, responsive, a11y (DEFAULT) |
| `react` | State, hooks, performance, patterns |
| `nextjs` | SSR, routing, images, API routes |
| `vue` | Composition API, Pinia, Vue Router |
| `svelte` | Runes, stores, SvelteKit |
| `swiftui` | Views, State, Navigation, Animation |
| `react-native` | Components, Navigation, Lists |
| `flutter` | Widgets, State, Layout, Theming |
| `shadcn` | shadcn/ui components, theming, forms, patterns |
| `jetpack-compose` | Composables, Modifiers, State Hoisting, Recomposition |

### Stack Examples

**html-tailwind**
```html
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  Subscribe
</button>
```

**react**
```tsx
const [count, setCount] = useState(0);
<button onClick={() => setCount(c => c + 1)} className="btn-primary">
  Clicked {count} times
</button>
```

**nextjs**
```tsx
import Image from 'next/image';
<Image src="/hero.jpg" alt="Hero" width={800} height={400} priority />
```

**vue**
```vue
<script setup>
const count = ref(0);
</script>
<template>
  <button @click="count++">Count: {{ count }}</button>
</template>
```

**svelte**
```svelte
<script>
  let count = $state(0);
</script>
<button onclick={() => count++}>Count: {count}</button>
```

**swiftui**
```swift
Button(action: { isPressed.toggle() }) {
    Text("Tap me").padding().background(Color.blue).foregroundColor(.white).cornerRadius(8)
}
```

**react-native**
```tsx
<TouchableOpacity style={styles.button} onPress={handlePress}>
  <Text style={styles.buttonText}>Get Started</Text>
</TouchableOpacity>
```

**flutter**
```dart
ElevatedButton(
  onPressed: () => setState(() => _count++),
  child: Text('Count: $_count'),
)
```

**shadcn**
```tsx
<Button variant="default" size="lg" onClick={handleSubmit}>
  <Icons.check className="mr-2 h-4 w-4" /> Confirm
</Button>
```

**jetpack-compose**
```kotlin
Button(onClick = { count++ }, modifier = Modifier.padding(16.dp)) {
    Text("Clicked $count times")
}
```

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |
