# Other Diagram Types

## Contents

1. [State Diagrams](#state-diagrams)
2. [Git Graphs](#git-graphs)
3. [Gantt Charts](#gantt-charts)
4. [Pie Charts](#pie-charts)
5. [Quadrant Charts](#quadrant-charts)
6. [Best Practices by Diagram Type](#best-practices-by-diagram-type)

State diagrams, git graphs, gantt charts, and pie/quadrant charts for specialized visualization needs.

## State Diagrams

State diagrams model state machines, showing states and transitions. Ideal for modeling object lifecycles, UI states, or workflow status.

<example name="Basic State">

### Basic Syntax
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Complete : success
    Processing --> Failed : error
    Complete --> [*]
    Failed --> Idle : retry
```

</example>

<example name="Composite States">

### Composite States
```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Pending
        Pending --> InProgress : assign
        InProgress --> Review : submit
        Review --> InProgress : request_changes
        Review --> Done : approve
    }

    Active --> Cancelled : cancel
    Active --> [*] : complete
```

</example>

<example name="Order Lifecycle">

### Order Lifecycle Example
```mermaid
stateDiagram-v2
    [*] --> Draft

    Draft --> Submitted : submit
    Draft --> Cancelled : cancel

    Submitted --> PaymentPending : process
    PaymentPending --> PaymentFailed : payment_error
    PaymentPending --> Confirmed : payment_success

    PaymentFailed --> PaymentPending : retry_payment
    PaymentFailed --> Cancelled : abandon

    Confirmed --> Processing : start_fulfillment
    Processing --> Shipped : ship
    Shipped --> Delivered : confirm_delivery
    Delivered --> [*]

    Cancelled --> [*]

    note right of PaymentPending : Awaiting payment\nconfirmation
    note right of Processing : Items being\npicked & packed
```

</example>

<example name="Concurrent States">

### Concurrent States (Fork/Join)
```mermaid
stateDiagram-v2
    [*] --> Checkout

    state Checkout {
        [*] --> fork_state
        state fork_state <<fork>>
        fork_state --> ValidateCart
        fork_state --> ValidatePayment
        fork_state --> ValidateShipping

        ValidateCart --> join_state
        ValidatePayment --> join_state
        ValidateShipping --> join_state
        state join_state <<join>>

        join_state --> ProcessOrder
    }

    Checkout --> Complete : success
    Checkout --> Failed : validation_error
```

</example>

## Git Graphs

Git graphs visualize branching strategies and commit history. Useful for documenting Git workflows.

<example name="Basic Git Graph">

### Basic Syntax
```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

</example>

<example name="Feature Branch">

### Feature Branch Workflow
```mermaid
gitGraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "setup"

    branch feature/auth
    checkout feature/auth
    commit id: "add login"
    commit id: "add logout"

    checkout develop
    branch feature/dashboard
    checkout feature/dashboard
    commit id: "dashboard UI"

    checkout develop
    merge feature/auth id: "merge auth"

    checkout feature/dashboard
    commit id: "dashboard API"

    checkout develop
    merge feature/dashboard id: "merge dashboard"

    checkout main
    merge develop tag: "v1.0.0"
```

</example>

<example name="GitFlow">

### GitFlow Workflow
```mermaid
gitGraph
    commit id: "v1.0.0" tag: "v1.0.0"

    branch develop
    checkout develop
    commit id: "dev setup"

    branch feature/user-profile
    commit id: "profile page"
    commit id: "profile API"

    checkout develop
    merge feature/user-profile

    branch release/1.1
    commit id: "bump version"
    commit id: "fix bug"

    checkout main
    merge release/1.1 tag: "v1.1.0"

    checkout develop
    merge release/1.1

    branch hotfix/security
    commit id: "patch CVE"

    checkout main
    merge hotfix/security tag: "v1.1.1"

    checkout develop
    merge hotfix/security
```

</example>

## Gantt Charts

Gantt charts visualize project timelines, task dependencies, and milestones. Essential for project planning.

<example name="Basic Gantt">

### Basic Syntax
```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD

    section Planning
    Requirements gathering    :a1, 2024-01-01, 7d
    Technical design          :a2, after a1, 5d

    section Development
    Backend API               :b1, after a2, 14d
    Frontend UI               :b2, after a2, 14d
    Integration               :b3, after b1, 7d

    section Testing
    QA Testing                :c1, after b3, 7d
    Bug fixes                 :c2, after c1, 5d

    section Deployment
    Production release        :milestone, after c2, 0d
```

</example>

<example name="Sprint Planning">

### Sprint Planning
```mermaid
gantt
    title Sprint 23 - User Authentication
    dateFormat YYYY-MM-DD
    excludes weekends

    section Backend
    JWT implementation        :crit, jwt, 2024-03-04, 3d
    OAuth integration         :oauth, after jwt, 4d
    Session management        :session, after oauth, 2d

    section Frontend
    Login page                :login, 2024-03-04, 2d
    Registration form         :reg, after login, 2d
    Password reset            :reset, after reg, 2d

    section Testing
    Unit tests                :unit, after session, 2d
    E2E tests                 :e2e, after unit, 2d

    section Milestones
    Code freeze               :milestone, crit, 2024-03-15, 0d
    Sprint review             :milestone, 2024-03-18, 0d
```

</example>

<example name="Product Roadmap">

### Product Roadmap
```mermaid
gantt
    title Q1 2024 Product Roadmap
    dateFormat YYYY-MM-DD

    section Core Platform
    Performance optimization  :done, perf, 2024-01-01, 21d
    Database migration        :active, db, after perf, 14d
    API v2 release            :api, after db, 14d

    section New Features
    Real-time notifications   :notif, 2024-02-01, 28d
    Advanced search           :search, after notif, 21d

    section Mobile App
    iOS beta                  :ios, 2024-01-15, 45d
    Android beta              :android, 2024-02-01, 45d
    Public launch             :milestone, crit, 2024-03-31, 0d

    section Infrastructure
    CDN setup                 :cdn, 2024-01-08, 7d
    Monitoring dashboard      :mon, after cdn, 14d
```

</example>

## Pie Charts

Pie charts show proportional data distribution. Use for simple percentage breakdowns.

<example name="Basic Pie">

### Basic Syntax
```mermaid
pie showData
    title Browser Market Share
    "Chrome" : 65
    "Safari" : 19
    "Firefox" : 8
    "Edge" : 5
    "Other" : 3
```

</example>

<example name="Sprint Breakdown">

### Sprint Work Breakdown
```mermaid
pie showData
    title Sprint 23 Effort Distribution
    "Feature Development" : 45
    "Bug Fixes" : 20
    "Code Review" : 15
    "Testing" : 12
    "Documentation" : 8
```

</example>

## Quadrant Charts

Quadrant charts plot items on two axes for prioritization and analysis.

<example name="Basic Quadrant">

### Priority Matrix
```mermaid
quadrantChart
    title Feature Prioritization
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact

    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate

    User Authentication: [0.2, 0.9]
    Dark Mode: [0.3, 0.4]
    API Refactor: [0.8, 0.7]
    Legacy Migration: [0.9, 0.3]
    Search Feature: [0.5, 0.8]
    Tooltip Updates: [0.1, 0.2]
```

</example>

<example name="Tech Debt">

### Technical Debt Assessment
```mermaid
quadrantChart
    title Tech Debt Priority
    x-axis Low Risk --> High Risk
    y-axis Low Cost to Fix --> High Cost to Fix

    quadrant-1 Plan Carefully
    quadrant-2 Fix When Possible
    quadrant-3 Quick Wins
    quadrant-4 Address Immediately

    Outdated Dependencies: [0.7, 0.3]
    SQL Injection Risk: [0.9, 0.4]
    Missing Tests: [0.4, 0.6]
    Poor Error Handling: [0.6, 0.5]
    Code Duplication: [0.2, 0.4]
    Memory Leaks: [0.8, 0.7]
```

</example>

## Best Practices by Diagram Type

### State Diagrams
- Begin every diagram with `[*] --> InitialState` and end with `FinalState --> [*]`.
- Label every transition with the trigger event name (e.g., `: submit`, `: cancel`).
- Wrap 3+ related states in a `state` composite block and name it after the lifecycle phase.
- Add `note right of StateName` to explain non-obvious transition guards.

### Git Graphs
- Set `id:` on every commit to a short descriptive label (e.g., `id: "add auth"`).
- Tag release commits on main with `tag: "v1.0.0"`.
- Name branches with the `type/name` convention (e.g., `feature/auth`, `hotfix/security`).

### Gantt Charts
- Add `excludes weekends` for realistic timelines.
- Mark critical path tasks with `crit` and key dates with `milestone`.
- Group tasks into `section` blocks named after project phases.
- Use `after taskId` for dependencies rather than hardcoded dates where possible.

### Pie/Quadrant Charts
- Cap pie charts at 5-7 segments. Merge small slices into "Other".
- Add `showData` to every pie chart so values are visible.
- Label all four quadrants with actionable names (e.g., "Do First", "Eliminate").
