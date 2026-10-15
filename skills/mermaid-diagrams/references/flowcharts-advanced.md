# Flowcharts - Advanced

## Contents

1. [Styling](#styling)
2. [Comprehensive Example: User Registration Flow](#comprehensive-example-user-registration-flow)
3. [Algorithm Example: Binary Search](#algorithm-example-binary-search)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [E-Commerce Checkout Flow](#e-commerce-checkout-flow)
6. [Decision Matrix Example](#decision-matrix-example)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)

Styling, comprehensive examples, and common patterns for flowcharts. The comprehensive examples run past the 15-node default in SKILL.md Step 2 to show more syntax at once; they are not target sizes.

## Styling

<example name="Individual Styling">

### Individual Node Styling
```mermaid
flowchart LR
    A[Normal]
    B[Styled]

    style B fill:#ff6b6b,stroke:#333,stroke-width:4px,color:#1a1a1a
```

</example>

<example name="Class-based Styling">

### Class-based Styling
```mermaid
flowchart LR
    A[Node 1]:::className
    B[Node 2]:::className
    C[Node 3]

    classDef className fill:#f9f,stroke:#333,stroke-width:2px
```

</example>

<example name="Link Styling">

### Link Styling
```mermaid
flowchart LR
    A --> B
    linkStyle 0 stroke:#ff3,stroke-width:4px,color:#b30000
```

</example>

<example name="User Registration">

## Comprehensive Example: User Registration Flow

```mermaid
flowchart TD
    Start([User visits registration page]) --> Form[Show registration form]
    Form --> Input[User enters details]
    Input --> Validate{Valid input?}

    Validate -->|No| ShowError[Show validation errors]
    ShowError --> Form

    Validate -->|Yes| CheckEmail{Email exists?}

    CheckEmail -->|Yes| EmailError[Show 'Email already registered']
    EmailError --> Form

    CheckEmail -->|No| CreateAccount[Create user account]
    CreateAccount --> Hash[Hash password]
    Hash --> SaveDB[(Save to database)]
    SaveDB --> GenerateToken[Generate verification token]
    GenerateToken --> SendEmail[Send verification email]
    SendEmail --> ShowSuccess[Show success message]
    ShowSuccess --> End([Redirect to login])

    style Start fill:#90EE90,stroke:#333,stroke-width:2px
    style End fill:#90EE90,stroke:#333,stroke-width:2px
    style CreateAccount fill:#87CEEB,stroke:#333,stroke-width:2px
    style SaveDB fill:#FFD700,stroke:#333,stroke-width:2px
```

</example>

<example name="Binary Search">

## Algorithm Example: Binary Search

```mermaid
flowchart TD
    %% Labels with brackets, parentheses, or < are quoted
    Start([Start Binary Search]) --> Init["Set low = 0, high = array.length - 1"]
    Init --> Check{"low <= high?"}

    Check -->|No| NotFound[Return -1: Not found]
    NotFound --> End([End])

    Check -->|Yes| CalcMid["mid = low + (high - low) / 2"]
    CalcMid --> Compare{"array[mid] == target?"}

    Compare -->|Yes| Found[Return mid: Found]
    Found --> End

    Compare -->|No| CheckLess{"array[mid] < target?"}

    CheckLess -->|Yes| MoveLow[low = mid + 1]
    MoveLow --> Check

    CheckLess -->|No| MoveHigh[high = mid - 1]
    MoveHigh --> Check

    style Start fill:#90EE90
    style End fill:#90EE90
    style Found fill:#FFD700
    style NotFound fill:#FF6B6B
```

</example>

<example name="CI/CD Pipeline">

## CI/CD Pipeline

```mermaid
flowchart LR
    subgraph Development
        Commit([Developer commits code]) --> Push[Push to repository]
    end

    subgraph CI
        Push --> Trigger[Trigger CI pipeline]
        Trigger --> Checkout[Checkout code]
        Checkout --> Install[Install dependencies]
        Install --> Lint[Run linters]
        Lint --> Test[Run tests]
        Test --> TestsPass{Tests passed?}
        TestsPass -->|Yes| Build[Build application]
    end

    subgraph QA
        Build --> DeployStaging[Deploy to staging]
        DeployStaging --> E2E[Run E2E tests]
        E2E --> ManualQA{Manual QA approval?}
    end

    subgraph Production
        ManualQA -->|Approved| DeployProd[Deploy to production]
        DeployProd --> HealthCheck{Health check passed?}
        HealthCheck -->|Yes| Success([Deployment successful])
        HealthCheck -->|No| Rollback[Rollback deployment]
        Rollback --> Alert([Alert team])
    end

    ManualQA -->|Rejected| FixIssues[Fix issues]
    FixIssues --> Development

    TestsPass -->|No| NotifyDev[Notify developer]
    NotifyDev --> FixIssues
```

</example>

<example name="E-Commerce Checkout">

## E-Commerce Checkout Flow

```mermaid
flowchart TD
    Start([User clicks Checkout]) --> Auth{Authenticated?}

    Auth -->|No| Login[Redirect to login]
    Login --> Auth

    Auth -->|Yes| Cart{Cart empty?}
    Cart -->|Yes| EmptyCart[Show empty cart message]
    EmptyCart --> Browse([Redirect to products])

    Cart -->|No| Address[Show shipping address form]
    Address --> ValidateAddr{Valid address?}
    ValidateAddr -->|No| Address
    ValidateAddr -->|Yes| Shipping[Select shipping method]

    Shipping --> Payment[Enter payment details]
    Payment --> ValidatePayment{Valid payment info?}
    ValidatePayment -->|No| Payment

    ValidatePayment -->|Yes| Review[Show order review]
    Review --> Confirm{Confirm order?}

    Confirm -->|No| Edit{Edit what?}
    Edit -->|Address| Address
    Edit -->|Shipping| Shipping
    Edit -->|Payment| Payment

    Confirm -->|Yes| ProcessPayment[Process payment]
    ProcessPayment --> PaymentResult{Payment successful?}

    PaymentResult -->|No| PaymentError[Show payment error]
    PaymentError --> RetryPayment{Retry?}
    RetryPayment -->|Yes| Payment
    RetryPayment -->|No| Cancel([Order cancelled])

    PaymentResult -->|Yes| CreateOrder[(Create order record)]
    CreateOrder --> ReduceStock[Reduce inventory]
    ReduceStock --> SendConfirmation[Send confirmation email]
    SendConfirmation --> Success([Order complete - Show confirmation])

    style Start fill:#90EE90
    style Success fill:#90EE90
    style Cancel fill:#FF6B6B
    style CreateOrder fill:#FFD700
```

</example>

<example name="Decision Matrix">

## Decision Matrix Example

```mermaid
flowchart TD
    Start([Select deployment strategy]) --> Env{Environment?}

    Env -->|Development| DevDecision{Automated tests?}
    DevDecision -->|Pass| DevDeploy[Auto-deploy to dev]
    DevDecision -->|Fail| Block[Block deployment]

    Env -->|Staging| StageDecision{All checks pass?}
    StageDecision -->|Yes| StageDeploy[Deploy to staging]
    StageDecision -->|No| Block

    Env -->|Production| ProdDecision{Change type?}

    ProdDecision -->|Hotfix| Urgent{Critical bug?}
    Urgent -->|Yes| FastTrack[Emergency approval + deploy]
    Urgent -->|No| NormalProcess

    ProdDecision -->|Feature| NormalProcess{Approval status?}
    NormalProcess -->|Approved| Schedule{Deploy window?}
    NormalProcess -->|Pending| Wait[Wait for approval]
    NormalProcess -->|Rejected| Block

    Schedule -->|Now| ImmediateDeploy[Deploy immediately]
    Schedule -->|Scheduled| QueueDeploy[Queue for deploy window]

    DevDeploy --> Monitor[Monitor metrics]
    StageDeploy --> Monitor
    FastTrack --> Monitor
    ImmediateDeploy --> Monitor
    QueueDeploy --> Monitor

    Monitor --> End([Deployment complete])
    Block --> End
    Wait --> End
```

</example>

## Best Practices

1. **Write action-oriented labels** - "Validate input" not "Validation". Every process node should read as a step someone performs; decisions are questions, and end nodes may state the outcome.
2. **Use the same shape for the same type of action** - Rectangles for process steps, diamonds for decisions, cylinders `[(...)]` for database writes, stadiums `([...])` for start/end.
3. **Default to `TD` (top-down) or `LR` (left-right)** - These match natural reading direction. Use `BT` or `RL` only when the flow requires it.
4. **Mark start and end nodes in a full process flow** with stadium/pill shapes `([Start])` and `([Done])`. The short pattern fragments below leave them out.
5. **Group each phase in a `subgraph` when a flow has distinct phases** - Name the subgraph after the phase (e.g., "Validation", "Deployment"), as the CI/CD example does.
6. **Use `classDef` when 3 or more nodes share a style** - Define reusable classes (`success`, `error`, `warning`). A `style` line is fine for one or two nodes.
7. **Limit to one process per diagram** - If you need to show two processes, create two diagrams and link them with a parent overview.

## Common Patterns

<example name="Linear Flow">

### Simple Linear Flow
```mermaid
flowchart LR
    A[Step 1] --> B[Step 2] --> C[Step 3] --> D[Step 4]
```

</example>

<example name="Branching Decision">

### Branching Decision
```mermaid
flowchart TD
    A[Input] --> B{Condition?}
    B -->|True| C[Path 1]
    B -->|False| D[Path 2]
    C --> E[Merge]
    D --> E
```

</example>

<example name="Loop Pattern">

### Loop Pattern
```mermaid
flowchart TD
    A[Initialize] --> B[Process]
    B --> C{Continue?}
    C -->|Yes| B
    C -->|No| D[Exit]
```

</example>

<example name="Error Handling">

### Error Handling
```mermaid
flowchart TD
    A[Try operation] --> B{Success?}
    B -->|Yes| C[Continue]
    B -->|No| D[Handle error]
    D --> E{Retry?}
    E -->|Yes| A
    E -->|No| F[Abort]
```

</example>
