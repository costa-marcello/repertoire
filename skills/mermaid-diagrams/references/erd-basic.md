# Entity Relationship Diagrams - Basics

## Contents

1. [Basic Syntax](#basic-syntax)
2. [Defining Entities](#defining-entities)
3. [Entity Attributes](#entity-attributes)
4. [Relationships](#relationships)
5. [Comprehensive Example: E-Commerce Database](#comprehensive-example-e-commerce-database)

<example name="Basic Syntax">

## Basic Syntax

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
```

</example>

<example name="Entities">

## Defining Entities

```mermaid
erDiagram
    CUSTOMER
    ORDER
    PRODUCT
```

</example>

<example name="Entity Attributes">

## Entity Attributes

Define columns with type and constraints:

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string email UK
        string name
        string phone
        datetime created_at
    }
```

**Attribute format:** `type name [keys] ["comment"]`

- **Type:** free text that starts with a letter, so copy it from the user's schema (`varchar(255)` is valid).
- **Keys:** `PK`, `FK`, and `UK`. Combine them with a comma: `PK, FK`.
- **Comment:** a quoted string at the end of the line, such as `"NOT NULL"`. It cannot contain a double quote.

</example>

## Relationships

### Relationship Symbols

**Cardinality** (written on each end; the right end mirrors the left):
- `||` - Exactly one
- `|o` / `o|` - Zero or one
- `}|` / `|{` - One or many
- `}o` / `o{` - Zero or many

**Relationship line:**
- `--` (solid) - The default for every relationship, as in all the examples here.
- `..` (dashed) - Use it only when the user wants identifying and non-identifying relationships told apart. Then `..` marks a non-identifying one (the child has its own key) and `--` an identifying one (the child's key includes the parent's key).

**Label:** every relationship needs one after the colon. Quote a label of more than one word: `: "belongs to"`.

<example name="Common Relationships">

### Common Relationships

```mermaid
erDiagram
    %% One-to-One
    USER ||--|| PROFILE : has

    %% One-to-Many
    CUSTOMER ||--o{ ORDER : places

    %% Many-to-Many, drawn directly
    READER }o--o{ MAGAZINE : "subscribes to"

    %% Many-to-Many through a junction table (use this when the link has columns)
    STUDENT ||--o{ ENROLLMENT : has
    COURSE ||--o{ ENROLLMENT : includes

    %% Optional Relationships
    EMPLOYEE |o--o{ DEPARTMENT : manages
```

</example>

<example name="Relationship Labels">

### Relationship with Labels

```mermaid
erDiagram
    AUTHOR ||--o{ BOOK : writes
    BOOK }o--|| PUBLISHER : "published by"
    READER }o--o{ BOOK : reads
```

</example>

<example name="E-Commerce Database">

## Comprehensive Example: E-Commerce Database

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ REVIEW : writes
    CUSTOMER ||--o{ ADDRESS : has
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"
    PRODUCT }o--|| CATEGORY : "belongs to"
    PRODUCT ||--o{ REVIEW : receives
    PRODUCT ||--o{ INVENTORY : tracks
    ORDER ||--|| PAYMENT : "paid by"
    ORDER ||--o| SHIPMENT : "shipped via"

    CUSTOMER {
        uuid id PK
        varchar email UK "NOT NULL"
        varchar name "NOT NULL"
        varchar phone
        timestamp created_at "DEFAULT NOW()"
        timestamp updated_at
    }

    ADDRESS {
        uuid id PK
        uuid customer_id FK
        varchar street "NOT NULL"
        varchar city "NOT NULL"
        varchar state
        varchar postal_code
        varchar country "NOT NULL"
        boolean is_default
    }

    ORDER {
        uuid id PK
        uuid customer_id FK "NOT NULL"
        decimal total "NOT NULL"
        varchar status "NOT NULL"
        timestamp order_date "DEFAULT NOW()"
        timestamp shipped_date
        timestamp delivered_date
    }

    LINE_ITEM {
        uuid id PK
        uuid order_id FK "NOT NULL"
        uuid product_id FK "NOT NULL"
        int quantity "NOT NULL"
        decimal price_per_unit "NOT NULL"
        decimal subtotal "COMPUTED"
    }

    PRODUCT {
        uuid id PK
        varchar sku UK "NOT NULL"
        varchar name "NOT NULL"
        text description
        decimal price "NOT NULL"
        uuid category_id FK
        boolean is_active "DEFAULT TRUE"
        timestamp created_at "DEFAULT NOW()"
    }

    CATEGORY {
        uuid id PK
        varchar name UK "NOT NULL"
        text description
        uuid parent_category_id FK
    }

    INVENTORY {
        uuid id PK
        uuid product_id FK "NOT NULL"
        int quantity "DEFAULT 0"
        varchar warehouse_location
        timestamp last_updated
    }

    REVIEW {
        uuid id PK
        uuid customer_id FK "NOT NULL"
        uuid product_id FK "NOT NULL"
        int rating "CHECK 1-5"
        text comment
        timestamp created_at "DEFAULT NOW()"
    }

    PAYMENT {
        uuid id PK
        uuid order_id FK "NOT NULL"
        varchar payment_method "NOT NULL"
        decimal amount "NOT NULL"
        varchar status "NOT NULL"
        varchar transaction_id UK
        timestamp processed_at
    }

    SHIPMENT {
        uuid id PK
        uuid order_id FK "NOT NULL"
        varchar carrier
        varchar tracking_number
        timestamp shipped_date
        timestamp estimated_delivery
        timestamp actual_delivery
    }
```

</example>
