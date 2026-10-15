# Theming and Styling

## Contents

1. [Frontmatter Configuration](#frontmatter-configuration)
2. [Themes](#themes)
3. [Custom Theme Variables](#custom-theme-variables)
4. [Diagram-Specific Styling](#diagram-specific-styling)
5. [Subgraph Styling](#subgraph-styling)
6. [Complex Styling Example](#complex-styling-example)
7. [Accessibility Considerations](#accessibility-considerations)
8. [Best Practices for Theming](#best-practices-for-theming)

Visual customization for Mermaid diagrams including themes, colors, and styling options.

<example name="Frontmatter Configuration">

## Frontmatter Configuration

Add YAML configuration at the top of diagrams:

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#1a1a1a"
    primaryBorderColor: "#333"
    lineColor: "#666"
    secondaryColor: "#4ecdc4"
    tertiaryColor: "#ffe66d"
---
flowchart TD
    A --> B
```

</example>

## Themes

### Built-in Themes

Set `theme:` under `config:` in the frontmatter, as in the examples below. Default to `default`; use `base` when you need custom colors.
- `default` - Standard blue theme
- `forest` - Green earth tones
- `dark` - Dark mode friendly
- `neutral` - Grayscale, good for print
- `base` - Minimal base theme, the only one `themeVariables` can change

Newer Mermaid releases add more themes. Verify the list against the Mermaid theming docs before using a theme not listed here.

<example name="Default Theme">

### Theme Examples

**Default Theme:**
```mermaid
---
config:
  theme: default
---
flowchart LR
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
```

</example>

<example name="Dark Theme">

**Dark Theme:**
```mermaid
---
config:
  theme: dark
---
flowchart LR
    A[Start] --> B[Process]
    B --> C{Decision}
```

</example>

<example name="Forest Theme">

**Forest Theme:**
```mermaid
---
config:
  theme: forest
---
flowchart LR
    A[Start] --> B[Process]
```

</example>

<example name="Custom Theme Variables">

## Custom Theme Variables

Override specific colors. Two rules decide whether an override shows up: it works only with `theme: base`, and only hex colors are recognized (`#ff6b6b` works, `red` does not).

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#ff6b6b"
    primaryTextColor: "#1a1a1a"
    primaryBorderColor: "#d63031"
    lineColor: "#74b9ff"
    secondaryColor: "#00b894"
    tertiaryColor: "#fdcb6e"
    background: "#f0f0f0"
    mainBkg: "#ffffff"
    textColor: "#333333"
    nodeBorder: "#333333"
    clusterBkg: "#f9f9f9"
    clusterBorder: "#666666"
---
flowchart TD
    A --> B --> C
```

</example>

<example name="Class-based Styling">

## Diagram-Specific Styling

### Flowchart Styling

**Class-based styling:**
```mermaid
flowchart TD
    A[Normal]:::success
    B[Warning]:::warning
    C[Error]:::error

    classDef success fill:#00b894,stroke:#00a383,color:#1a1a1a
    classDef warning fill:#fdcb6e,stroke:#e8b923,color:#333
    classDef error fill:#ff6b6b,stroke:#ee5253,color:#1a1a1a

    A --> B --> C
```

</example>

<example name="Node-specific Styling">

**Node-specific styling:**
```mermaid
flowchart LR
    A[Node A]
    B[Node B]
    C[Node C]

    style A fill:#ff6b6b,stroke:#333,stroke-width:4px
    style B fill:#4ecdc4,stroke:#333,stroke-width:2px
    style C fill:#ffe66d,stroke:#333,stroke-width:2px

    A --> B --> C
```

</example>

<example name="Link Styling">

**Link styling:**
```mermaid
flowchart LR
    A --> B
    B --> C
    C --> D

    linkStyle 0 stroke:#ff6b6b,stroke-width:4px
    linkStyle 1 stroke:#4ecdc4,stroke-width:2px
    linkStyle 2 stroke:#ffe66d,stroke-width:2px
```

</example>

<example name="Sequence Diagram Styling">

### Sequence Diagram Styling

```mermaid
---
config:
  theme: forest
---
sequenceDiagram
    participant A
    participant B
    participant C

    A->>B: Message 1
    B->>C: Message 2

    Note over A,C: Styled note
```

</example>

<example name="Class Diagram Styling">

### Class Diagram Styling

```mermaid
---
config:
  theme: dark
---
classDiagram
    class User {
        +String name
        +login()
    }

    class Admin {
        +manageUsers()
    }

    User <|-- Admin
```

</example>

<example name="Subgraph Styling">

## Subgraph Styling

```mermaid
flowchart TB
    subgraph Frontend
        A[Web App]
        B[Mobile App]
    end

    subgraph Backend
        C[API]
        D[Database]
    end

    A & B --> C
    C --> D

    style Frontend fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style Backend fill:#fff3e0,stroke:#ff9800,stroke-width:2px
```

</example>

<example name="Complex Styling">

## Complex Styling Example

```mermaid
flowchart TB
    subgraph production[Production Environment]
        direction LR
        lb[Load Balancer]

        subgraph servers[Application Servers]
            app1[Server 1]
            app2[Server 2]
            app3[Server 3]
        end

        cache[(Redis Cache)]
        db[(PostgreSQL)]
    end

    subgraph monitoring[Monitoring]
        logs[Log Aggregator]
        metrics[Metrics Dashboard]
    end

    users[Users] --> lb
    lb --> app1 & app2 & app3
    app1 & app2 & app3 --> cache
    app1 & app2 & app3 --> db
    app1 & app2 & app3 --> logs
    logs --> metrics

    style production fill:#e8f5e9,stroke:#4caf50,stroke-width:3px
    style servers fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style monitoring fill:#e3f2fd,stroke:#2196f3,stroke-width:2px

    classDef serverClass fill:#81c784,stroke:#4caf50,stroke-width:2px,color:#000
    class app1,app2,app3 serverClass

    linkStyle 0,1,2,3 stroke:#4caf50,stroke-width:2px
    linkStyle 4,5,6,7,8,9 stroke:#ff9800,stroke-width:1px
```

</example>

<example name="Accessible Styling">

## Accessibility Considerations

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#0066cc"
    primaryTextColor: "#ffffff"
    primaryBorderColor: "#003d7a"
    lineColor: "#333333"
    background: "#ffffff"
---
flowchart TD
    A[High Contrast Text] --> B[Clear Labels]
    B --> C[Meaningful Colors]
```

**Accessibility tips:**
- Use high contrast color combinations
- Don't rely solely on color to convey meaning
- Include descriptive text labels
- Test with color blindness simulators
- Provide a dark mode alternative when the target page supports it

</example>

## Best Practices for Theming

1. **Pick one theme per document** - All diagrams in the same page or README should share the same theme for visual consistency.
2. **Limit custom fill colors to 3-4 per diagram** - More than that creates visual noise. Use `classDef` to apply them consistently.
3. **Try `look: handDrawn` for informal docs** and `look: classic` for technical specifications. Match the tone to the audience.
4. **Check text contrast** (the ratio is in SKILL.md's Best Practices) for every `primaryTextColor`/`primaryColor` pair and every `classDef` fill and text color.
5. **Put config frontmatter in the diagram** rather than global CSS so each diagram is self-contained and portable.
