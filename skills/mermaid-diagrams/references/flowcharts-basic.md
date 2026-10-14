# Flowcharts - Basics

## Contents

1. [Basic Syntax](#basic-syntax)
2. [Node Shapes](#node-shapes)
3. [Connections](#connections)
4. [Subgraphs](#subgraphs)

Flowcharts visualize processes, algorithms, decision trees, and user journeys. They show step-by-step progression through a system or workflow.

<example name="Basic Syntax">

## Basic Syntax

```mermaid
flowchart TD
    A --> B
```

**Directions:**
- `TD` or `TB` - Top to Bottom (default)
- `BT` - Bottom to Top
- `LR` - Left to Right
- `RL` - Right to Left

</example>

## Node Shapes

<example name="Rectangle">

### Rectangle (default)
```mermaid
flowchart LR
    A[Process step]
```

</example>

<example name="Stadium">

### Stadium/Pill Shape
```mermaid
flowchart LR
    B([Stadium process])
```

</example>

<example name="Rounded Rectangle">

### Rounded Rectangle
```mermaid
flowchart LR
    C(Start or End)
```

</example>

<example name="Subroutine">

### Subroutine (Double Border)
```mermaid
flowchart LR
    D[[Subroutine]]
```

</example>

<example name="Database">

### Cylindrical (Database)
```mermaid
flowchart LR
    E[(Database)]
```

</example>

<example name="Circle">

### Circle
```mermaid
flowchart LR
    F((Circle node))
```

</example>

<example name="Flag">

### Asymmetric/Flag
```mermaid
flowchart LR
    G>Flag node]
```

</example>

<example name="Decision">

### Rhombus (Decision)
```mermaid
flowchart LR
    H{Decision?}
```

</example>

<example name="Hexagon">

### Hexagon
```mermaid
flowchart LR
    I{{Hexagon}}
```

</example>

<example name="Parallelogram">

### Parallelogram (Input/Output)
```mermaid
flowchart LR
    J[/Input or Output/]
    K[\Alternative IO\]
```

</example>

<example name="Trapezoid">

### Trapezoid
```mermaid
flowchart LR
    L[/Trapezoid\]
    M[\Alt trapezoid/]
```

</example>

## Connections

<example name="Basic Arrow">

### Basic Arrow
```mermaid
flowchart LR
    A --> B
```

</example>

<example name="Open Link">

### Open Link (No Arrow)
```mermaid
flowchart LR
    A --- B
```

</example>

<example name="Text on Links">

### Text on Links
```mermaid
flowchart LR
    A -->|Label text| B
    C ---|"Text with spaces"| D
```

</example>

<example name="Dotted Links">

### Dotted Links
```mermaid
flowchart LR
    A -.-> B
    C -.- D
    E -.Label.-> F
```

</example>

<example name="Thick Links">

### Thick Links
```mermaid
flowchart LR
    A ==> B
    C === D
    E ==Label==> F
```

</example>

<example name="Chaining">

### Chaining
```mermaid
flowchart LR
    A --> B --> C --> D
    E --> F & G --> H
```

</example>

<example name="Multi-directional">

### Multi-directional
```mermaid
flowchart LR
    A --> B & C & D
    B & C & D --> E
```

</example>

<example name="Subgraphs">

## Subgraphs

Group related nodes:

```mermaid
flowchart TB
    A[Start]

    subgraph Processing
        B[Step 1]
        C[Step 2]
        D[Step 3]
    end

    E[End]

    A --> B
    D --> E
```

</example>

<example name="Nested Subgraphs">

### Nested Subgraphs
```mermaid
flowchart TB
    subgraph Outer
        A[Node A]

        subgraph Inner
            B[Node B]
            C[Node C]
        end
    end
```

</example>

<example name="Subgraph Direction">

### Subgraph Direction
```mermaid
flowchart LR
    subgraph one
        direction TB
        A1 --> A2
    end

    subgraph two
        direction TB
        B1 --> B2
    end

    one --> two
```

</example>
