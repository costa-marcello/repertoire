# Advanced Mermaid Features

## Contents

1. [Layout Options](#layout-options)
2. [Look Options](#look-options)
3. [Complete Configuration Example](#complete-configuration-example)
4. [Click Events and Links](#click-events-and-links)
5. [Tooltips](#tooltips)
6. [Comments and Documentation](#comments-and-documentation)
7. [Directional Hints](#directional-hints)
8. [Responsive Sizing](#responsive-sizing)
9. [SVG Export Options](#svg-export-options)
10. [Performance Considerations](#performance-considerations)
11. [Integration Examples](#integration-examples)
12. [Best Practices for Advanced Features](#best-practices-for-advanced-features)

Configuration, layout options, and integration patterns for creating professional diagrams.

<example name="Layout: Dagre Default">

## Layout Options

### Dagre Layout (Default)

```mermaid
---
config:
  layout: dagre
---
flowchart TD
    A --> B
```

</example>

<example name="Layout: ELK Advanced">

### ELK Layout (Advanced)

For complex diagrams with better automatic layout:

```mermaid
---
config:
  layout: elk
  elk:
    mergeEdges: true
    nodePlacementStrategy: BRANDES_KOEPF
---
flowchart TD
    A --> B
```

**ELK node placement strategies:**
- `SIMPLE` - Basic placement
- `NETWORK_SIMPLEX` - Network optimization
- `LINEAR_SEGMENTS` - Linear arrangement
- `BRANDES_KOEPF` - Balanced (default)

</example>

<example name="Look: Classic">

## Look Options

### Classic Look

Traditional Mermaid appearance:

```mermaid
---
config:
  look: classic
---
flowchart LR
    A --> B --> C
```

</example>

<example name="Look: Hand-Drawn">

### Hand-Drawn Look

Sketch-like, informal style:

```mermaid
---
config:
  look: handDrawn
---
flowchart LR
    A --> B --> C
```

</example>

<example name="Complete Configuration">

## Complete Configuration Example

```mermaid
---
config:
  theme: base
  look: handDrawn
  layout: dagre
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#fff"
    primaryBorderColor: "#d63031"
    lineColor: "#74b9ff"
    secondaryColor: "#00b894"
    tertiaryColor: "#fdcb6e"
---
flowchart TD
    Start([Begin Process]) --> Input[Gather Data]
    Input --> Process{Valid?}
    Process -->|Yes| Store[(Save to DB)]
    Process -->|No| Error[Show Error]
    Store --> Notify[Send Notification]
    Error --> Input
    Notify --> End([Complete])
```

</example>

<example name="Click Events">

## Click Events and Links

Add interactive elements:

```mermaid
flowchart LR
    A[GitHub]
    B[Documentation]
    C[Live Demo]

    click A "https://github.com" "Go to GitHub"
    click B "https://mermaid.js.org" "View Docs"
    click C "https://mermaid.live" "Try Live Editor"

    A --> B --> C
```

</example>

<example name="Tooltips">

## Tooltips

Add hover text to nodes using the `click` callback syntax:

```mermaid
flowchart LR
    A[Service A]
    B[Service B]

    A -.->|REST API| B

    click A href "https://api.example.com" "API Documentation" _blank
    click B href "https://dashboard.example.com" "Service Dashboard" _blank
```

</example>

<example name="Comments">

## Comments and Documentation

```mermaid
flowchart TD
    %% This is a single-line comment

    %% Multi-line comments can be created
    %% by using multiple comment lines

    A[Start]
    B[Process]
    C[End]

    %% Define relationships
    A --> B
    B --> C

    %% Add styling
    style A fill:#90EE90
    style C fill:#FFB6C1
```

</example>

<example name="Directional Hints">

## Directional Hints

Override layout direction within subgraphs to mix horizontal and vertical flows:

```mermaid
flowchart LR
    subgraph Frontend
        direction TB
        A[React App] --> B[State Manager]
        B --> C[API Client]
    end

    subgraph Backend
        direction TB
        D[Router] --> E[Controller]
        E --> F[Service]
    end

    C --> D
```

</example>

## Responsive Sizing

Use CSS to make diagrams responsive:

```html
<div style="max-width: 100%; overflow: auto;">
    <pre class="mermaid">
        flowchart LR
            A --> B --> C
    </pre>
</div>
```

## SVG Export Options

When exporting to SVG:

```bash
# Export with custom dimensions
mmdc -i diagram.mmd -o output.svg -w 1920 -H 1080

# Export with background color
mmdc -i diagram.mmd -o output.svg -b "#ffffff"

# Export with transparent background
mmdc -i diagram.mmd -o output.svg -b "transparent"
```

<example name="Performance: Large Diagrams">

## Performance Considerations

For large diagrams:

```mermaid
---
config:
  layout: elk
  elk:
    mergeEdges: true
---
flowchart TD
    %% ELK handles complex layouts better
    %% Merge edges reduces visual clutter
```

**Performance tips:**
- Use ELK layout for diagrams with >20 nodes
- Enable edge merging for simplified connections
- Split very large diagrams into multiple focused views
- Group related nodes in subgraphs to reduce visual complexity
- Limit styling to essential elements

</example>

<example name="Integration: Markdown">

## Integration Examples

### Markdown Files

````markdown
# System Architecture

```mermaid
flowchart LR
    A --> B
```
````

</example>

<example name="Integration: HTML">

### HTML Files

```html
<!DOCTYPE html>
<html>
<head>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs';
        mermaid.initialize({
            startOnLoad: true,
            theme: 'dark',
            look: 'handDrawn'
        });
    </script>
</head>
<body>
    <pre class="mermaid">
        flowchart LR
            A --> B
    </pre>
</body>
</html>
```

</example>

<example name="Integration: React">

### React Components

```jsx
import React from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
    startOnLoad: true,
    theme: 'forest'
});

function DiagramComponent() {
    React.useEffect(() => {
        mermaid.contentLoaded();
    }, []);

    return (
        <div className="mermaid">
            flowchart LR
                A --> B
        </div>
    );
}
```

</example>

## Best Practices for Advanced Features

1. **Switch to ELK when dagre produces crossed lines** - Add `layout: elk` to the config frontmatter. ELK handles 20+ node diagrams better.
2. **Add a `%%` comment above every `themeVariables` block** explaining the colour rationale.
3. **Render to PNG or SVG with mermaid-cli and check the result** before committing -- renderer differences between platforms are common. No display is needed: a PNG can be read as an image file.
4. **Group related nodes in subgraphs** when a diagram has more than 8 nodes. Name each subgraph after the bounded context it represents.
5. **Commit config frontmatter alongside the diagram** so theme changes appear in code review diffs.
