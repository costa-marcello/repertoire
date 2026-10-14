# Class Diagrams

## Contents

- [Basic Syntax](#basic-syntax)
- [Defining Classes with Members](#defining-classes-with-members)
- [Relationships](#relationships) (Association and Link, Composition, Aggregation, Inheritance, Dependency, Realization)
- [Multiplicity](#multiplicity)
- [Relationship Labels](#relationship-labels)
- [Class Stereotypes](#class-stereotypes)
- [Abstract Classes and Methods](#abstract-classes-and-methods)
- [Generic Classes](#generic-classes)
- [Comprehensive Example: E-Commerce Domain](#comprehensive-example-e-commerce-domain)
- [Domain-Driven Design Patterns](#domain-driven-design-patterns)
- [Tips for Effective Class Diagrams](#tips-for-effective-class-diagrams)
- [Common Patterns](#common-patterns) (Repository, Factory, Strategy)

<example name="Basic Syntax">

## Basic Syntax

```mermaid
classDiagram
    ClassName
```

</example>

<example name="Class with Members">

## Defining Classes with Members

```mermaid
classDiagram
    class BankAccount {
        +String owner
        +Decimal balance
        -String accountNumber
        +deposit(amount)
        +withdraw(amount)
        +getBalance() Decimal
    }
```

**Visibility modifiers:**
- `+` Public
- `-` Private
- `#` Protected
- `~` Package/Internal

**Member syntax:**
- `+type attribute` - Attribute with type
- `+method(params) ReturnType` - Method with parameters and return type

</example>

## Relationships

<example name="Association">

### Association (`-->`) and Link (`--`)
Loose relationship where entities use each other but exist independently. `-->` points from the class that holds the reference; `--` is a plain solid link with no direction.

```mermaid
classDiagram
    Customer --> Order : places
    Title -- Genre : categorized as
```

</example>

<example name="Composition">

### Composition (`*--`)
Strong ownership - child cannot exist without parent. When parent is deleted, children are deleted.

```mermaid
classDiagram
    Order *-- LineItem : contains
    House *-- Room : has
```

</example>

<example name="Aggregation">

### Aggregation (`o--`)
Weaker ownership - child can exist independently. Represents "has-a" relationship.

```mermaid
classDiagram
    Department o-- Employee : employs
    Playlist o-- Song : lists
```

</example>

<example name="Inheritance">

### Inheritance (`<|--`)
"Is-a" relationship. Child class inherits from parent class.

```mermaid
classDiagram
    Animal <|-- Dog
    Animal <|-- Cat

    class Animal {
        +String name
        +makeSound()
    }

    class Dog {
        +bark()
    }
```

</example>

<example name="Dependency">

### Dependency (`..>`)
One class depends on another, often as a parameter or local variable. The arrow points at the class being depended on.

```mermaid
classDiagram
    OrderProcessor ..> PaymentGateway : uses
```

</example>

<example name="Realization">

### Realization/Implementation (`<|..`)
Class implements an interface.

```mermaid
classDiagram
    class Drawable {
        <<interface>>
        +draw()
    }
    Drawable <|.. Circle
    Drawable <|.. Rectangle
```

</example>

<example name="Multiplicity">

## Multiplicity

Show how many instances participate in a relationship:

```mermaid
classDiagram
    Customer "1" --> "0..*" Order : places
    Order "1" *-- "1..*" LineItem : contains
    Author "1..*" -- "1..*" Book : writes
```

**Common multiplicities:**
- `1` - Exactly one
- `0..1` - Zero or one
- `0..*` or `*` - Zero or many
- `1..*` - One or many
- `m..n` - Between m and n

</example>

<example name="Relationship Labels">

## Relationship Labels

```mermaid
classDiagram
    Customer --> Order : places
    Order --> Product : contains
    Driver --> Vehicle : drives
```

</example>

<example name="Stereotypes">

## Class Stereotypes

Mark special class types:

```mermaid
classDiagram
    class IRepository {
        <<interface>>
        +save(entity)
        +findById(id)
    }

    class UserService {
        <<service>>
        +createUser()
    }

    class UserDTO {
        <<dataclass>>
        +String name
        +String email
    }
```

</example>

<example name="Abstract Classes">

## Abstract Classes and Methods

```mermaid
classDiagram
    class Shape {
        <<abstract>>
        +int x
        +int y
        +draw()*
        +move(x, y)
    }

    Shape <|-- Circle
    Shape <|-- Rectangle
```

</example>

<example name="Generics">

## Generic Classes

Put the type parameter on the class definition (`class List~T~`) and in member types (`List~Order~`). A relationship line that names the class drops the `~T~` part. Generics with a comma (`Map~K, V~`) are not supported.

```mermaid
classDiagram
    class List~T~ {
        +add(item: T)
        +get(index: int) T
    }

    StringProcessor --> List : uses
```

</example>

<example name="E-Commerce Domain">

## Comprehensive Example: E-Commerce Domain

```mermaid
classDiagram
    %% Core entities
    class Customer {
        +UUID id
        +String email
        +String name
        +Address shippingAddress
        +placeOrder(cart: Cart) Order
        +getOrderHistory() List~Order~
    }

    class Order {
        +UUID id
        +DateTime orderDate
        +OrderStatus status
        +Decimal total
        +calculateTotal() Decimal
        +ship()
        +cancel()
    }

    class LineItem {
        +int quantity
        +Decimal pricePerUnit
        +getSubtotal() Decimal
    }

    class Product {
        +UUID id
        +String name
        +String description
        +Decimal price
        +int stockQuantity
        +reduceStock(quantity: int)
        +isAvailable() bool
    }

    class Category {
        +String name
        +String description
    }

    class Cart {
        +addItem(product: Product, quantity: int)
        +removeItem(product: Product)
        +getTotal() Decimal
        +clear()
    }

    %% Relationships
    Customer "1" --> "0..*" Order : places
    Customer "1" --> "1" Cart : has
    Order "1" *-- "1..*" LineItem : contains
    LineItem "1" --> "1" Product : references
    Product "0..*" --> "1" Category : belongs to
    Cart "1" o-- "0..*" Product : contains

    %% Enums
    class OrderStatus {
        <<enumeration>>
        PENDING
        PAID
        SHIPPED
        DELIVERED
        CANCELLED
    }

    Order --> OrderStatus : has status
```

</example>

## Domain-Driven Design Patterns

<example name="DDD Entity">

### Entities
```mermaid
classDiagram
    class User {
        <<entity>>
        -UUID id
        +String email
        +String name
    }
```

</example>

<example name="DDD Value Objects">

### Value Objects
```mermaid
classDiagram
    class Money {
        <<value object>>
        +Decimal amount
        +String currency
        +add(other: Money) Money
    }

    class Address {
        <<value object>>
        +String street
        +String city
        +String postalCode
    }
```

</example>

<example name="DDD Aggregates">

### Aggregates
```mermaid
classDiagram
    class Order {
        <<aggregate root>>
        -UUID id
        +addLineItem(item)
        +removeLineItem(item)
    }

    Order *-- LineItem : contains
```

</example>

## Tips for Effective Class Diagrams

1. **Draft 3-5 core entities first** - Add attributes and methods in a second pass after relationships are clear.
2. **Omit getters/setters** - Only show methods that represent domain behavior (e.g., `placeOrder()`, not `getName()`).
3. **Pick the right relationship arrow** - Composition (`*--`) when the child dies with the parent, aggregation (`o--`) when it survives, association (`-->`) or link (`--`) for loose links.
4. **Add multiplicity where cardinality matters** - `"1" --> "0..*"` removes ambiguity on associations, compositions, and aggregations. Inheritance and realization lines take none.
5. **Place related classes near each other** - Visual proximity signals cohesion.
6. **Add notes for business invariants** - e.g., `note for Order "Needs at least one line item"`.

## Common Patterns

<example name="Repository Pattern">

### Repository Pattern
```mermaid
classDiagram
    class IRepository~T~ {
        <<interface>>
        +save(entity: T)
        +findById(id: UUID) T
        +delete(entity: T)
    }

    class UserRepository {
        +findByEmail(email: String) User
    }

    IRepository <|.. UserRepository
```

</example>

<example name="Factory Pattern">

### Factory Pattern
```mermaid
classDiagram
    class ShapeFactory {
        +createShape(type: String) Shape
    }

    class Shape {
        <<abstract>>
        +draw()*
    }

    ShapeFactory ..> Shape : creates
    Shape <|-- Circle
    Shape <|-- Rectangle
```

</example>

<example name="Strategy Pattern">

### Strategy Pattern
```mermaid
classDiagram
    class PaymentProcessor {
        -PaymentStrategy strategy
        +setStrategy(strategy: PaymentStrategy)
        +processPayment(amount: Decimal)
    }

    class PaymentStrategy {
        <<interface>>
        +pay(amount: Decimal)*
    }

    PaymentStrategy <|.. CreditCardPayment
    PaymentStrategy <|.. PayPalPayment
    PaymentProcessor --> PaymentStrategy : delegates to
```

</example>
