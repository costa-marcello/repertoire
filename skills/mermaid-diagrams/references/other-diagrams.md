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
        Done --> [*]
    }

    Active --> Cancelled : cancel
    Active --> [*] : complete
    Cancelled --> [*]
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

    note right of PaymentPending : Awaiting payment confirmation
    note right of Processing
        Items being
        picked and packed
    end note
```

</example>

<example name="Concurrent States">

### Concurrent States (Fork/Join)
```mermaid
stateDiagram-v2
    [*] --> Checkout

    state Checkout {
        %% Declare fork and join states before the transitions that use them
        state fork_state <<fork>>
        state join_state <<join>>
        [*] --> fork_state
        fork_state --> ValidateCart
        fork_state --> ValidatePayment
        fork_state --> ValidateShipping

        ValidateCart --> join_state
        ValidatePayment --> join_state
        ValidateShipping --> join_state

        join_state --> ProcessOrder
        ProcessOrder --> [*]
    }

    Checkout --> Complete : success
    Checkout --> Failed : validation_error
    Complete --> [*]
    Failed --> [*]
```

</example>

## Git Graphs

<example name="Basic Git Graph">

### Basic Syntax
```mermaid
gitGraph
    commit id: "init"
    commit id: "add readme"
    branch develop
    checkout develop
    commit id: "add api"
    commit id: "add tests"
    checkout main
    merge develop
    commit id: "release notes"
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

    checkout main
    branch hotfix/security
    commit id: "patch CVE"

    checkout main
    merge hotfix/security tag: "v1.1.1"

    checkout develop
    merge hotfix/security
```

</example>

## Gantt Charts

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

The x-axis runs left to right and the y-axis bottom to top. `quadrant-1` is the top right, `quadrant-2` the top left, `quadrant-3` the bottom left, and `quadrant-4` the bottom right. Points are `Name: [x, y]`, with both values from 0 to 1.

<example name="Basic Quadrant">

### Priority Matrix
```mermaid
quadrantChart
    title Feature Prioritization
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact

    quadrant-1 Schedule
    quadrant-2 Do First
    quadrant-3 Fill In
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
    quadrant-2 Defer
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
- Begin every diagram with `[*] --> InitialState` and end every terminal state with `FinalState --> [*]`.
- Label every transition with the trigger event name (e.g., `: submit`, `: cancel`). `[*]` and fork/join edges need none.
- When several states share an exit (such as `cancel`), wrap them in a `state` composite block named after the phase, so one transition covers them all.
- Add `note right of StateName` to explain non-obvious transition guards.

### Git Graphs
- Set `id:` on every `commit` line to a short descriptive label (e.g., `id: "add auth"`).
- Tag release commits on main with `tag: "v1.0.0"`.
- Name short-lived branches with the `type/name` convention (e.g., `feature/auth`, `hotfix/security`); long-lived ones keep plain names such as `develop`.

### Gantt Charts
- Add `excludes weekends` when durations count working days, as in the Sprint Planning example; leave it out when they count calendar days.
- Mark key dates with `milestone`, and mark the critical path with `crit` when it matters to the reader.
- Group tasks into `section` blocks named after project phases.
- Use `after taskId` for dependencies rather than hardcoded dates where possible.

### Pie/Quadrant Charts
- Cap pie charts at 5-7 segments. Merge small slices into "Other".
- Add `showData` to every pie chart so values are visible.
- Label all four quadrants with actionable names (e.g., "Do First", "Eliminate"), and check each label against its corner: the high-x, high-y corner is `quadrant-1`, top right.
