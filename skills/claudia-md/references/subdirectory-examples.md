<!-- v1.1 | 2026-10-14 -->

# Subdirectory CLAUDE.md Examples

## Contents

1. [tests/CLAUDE.md](#testsclaudemd)
2. [src/components/CLAUDE.md](#srccomponentsclaudemd)
3. [src/api/CLAUDE.md](#srcapiclaudemd)
4. [When to Hand-Craft Subdirectory Files](#when-to-hand-craft-subdirectory-files)
5. [Auto-Generated Examples](#auto-generated-examples)
6. [Generated vs Hand-Crafted](#generated-vs-hand-crafted)

Real-world examples of subdirectory-specific CLAUDE.md files. None of them imports the parent CLAUDE.md: Claude Code already loads every CLAUDE.md from the working directory up, and loads a subdirectory's file when Claude first touches a file there.

---

## tests/CLAUDE.md

```markdown
# Testing Guidelines

## Context

Test files for the application. Use Vitest with React Testing Library.

## Conventions

### File Naming
- Unit tests: `{component}.test.tsx` — matches component file names
- Integration tests: `{feature}.integration.test.ts` — distinguishes from unit tests

### Test Structure
- Use `describe` blocks for grouping — organizes related tests
- Use `it` for individual tests (not `test`) — reads as specification
- Follow AAA pattern: Arrange, Act, Assert — keeps tests readable

### Mocking
- Mock at module boundaries only — hides bugs if you mock internal functions
- Prefer MSW for API mocking — tests real fetch behavior
- Reset mocks in `beforeEach` — prevents test pollution
```

---

## src/components/CLAUDE.md

```markdown
# Component Guidelines

## Context

React components using Tailwind CSS and shadcn/ui.

## Conventions

### File Structure
- One component per file — easier to find and refactor
- Co-locate styles, tests, and stories — keeps related code together

### Props
- Use TypeScript interfaces, not `type` — interfaces are extendable
- Destructure props in function signature — makes required props visible

### Styling
- Tailwind classes via `cn()` utility — enables conditional styling
- No inline styles — keeps styles in class strings for consistency
```

---

## src/api/CLAUDE.md

```markdown
# API Guidelines

## Context

Backend API routes using Express/Fastify. All routes require authentication.

## Conventions

### Route Structure
- Use RESTful naming conventions — predictable URL patterns
- Group related routes in single file — easier to find handlers

### Validation
- Zod schemas for all request bodies — catches malformed input early
- Validate early, fail fast — don't process invalid requests

### Error Handling
- Use custom error classes — enables typed error handling
- Log errors at boundary, not inline — single place for error logging
```

---

## When to Hand-Craft Subdirectory Files

Generate mode does not use this table. It creates a file only for a directory that scores 4 or more in Phase G2, and skips a directory that holds only tests.

| Directory Pattern | Create If | Purpose |
|-------------------|-----------|---------|
| `tests/` or `__tests__/` | Project has tests | Testing conventions, fixtures, mocking |
| `src/components/` | React/Vue/Svelte project | Component patterns, styling, props |
| `src/api/` or `backend/` | Has backend code | API patterns, validation, error handling |
| `src/` or `frontend/` | Has frontend code | State management, routing, hooks |
| `database/` or `prisma/` | Has DB layer | Schema conventions, migrations, queries |
| `packages/*/` | Monorepo | Package-specific overrides |

**Detection heuristics:**
1. Look for existing directory structure
2. Check for config files (jest.config.*, vitest.config.*, etc.)
3. Identify framework from package.json
4. Only create if directory exists and has substantial code

---

## Auto-Generated Examples

These examples show minimal CLAUDE.md files created by Generate mode. They prioritize brevity over comprehensiveness.

### packages/utils/CLAUDE.md (Generated)

```markdown
# Utils Package

## Context
Shared utility functions used across all packages. Pure functions, no side effects.

## Key Files
- `index.ts` - Package exports
- `string.ts` - String manipulation
- `date.ts` - Date formatting with date-fns

## Patterns
- Named exports only — enables tree-shaking for smaller bundles
```

**Why this works:** ~100 tokens, covers purpose, key files, one pattern with reasoning.

---

### src/services/payments/CLAUDE.md (Generated)

```markdown
# Payments Service

## Context
Stripe integration for subscriptions and one-time payments.

## Key Files
- `stripe.ts` - Stripe client setup
- `webhooks.ts` - Webhook handlers

## Patterns
- Idempotency keys on mutations — prevents duplicate charges

## Gotchas
- Webhooks require `STRIPE_WEBHOOK_SECRET` in env
- Test mode uses separate Stripe account
```

**Why this works:** ~110 tokens, pattern has reasoning, captures non-obvious gotchas.

---

## Generated vs Hand-Crafted

| Aspect | Generated | Hand-Crafted |
|--------|-----------|--------------|
| Length | About 100 (minimal) to 300 (full) tokens | 200-500 tokens |
| Context | One sentence | May include background |
| Key Files | 2-5 files | May list more |
| Patterns | 1-2 essential | May include style preferences |
| Gotchas | Only if found | Comprehensive list |

### When to Expand Generated Files

Keep generated as-is when:
- Directory is straightforward
- Patterns are obvious from code
- No unique gotchas

Expand manually when:
- Complex business logic needs explanation
- Non-obvious ordering dependencies
- Framework-specific quirks discovered later
- Team conventions differ from defaults

### Expansion Example

**Generated:**
```markdown
# Auth Service

## Context
JWT authentication with Redis sessions.

## Key Files
- `jwt.ts` - Token operations
- `middleware.ts` - Auth middleware

## Patterns
- Short-lived access tokens — limits exposure if stolen
```

**After manual expansion:**
```markdown
# Auth Service

## Context
JWT authentication with Redis sessions.

## Key Files
- `jwt.ts` - Token generation/validation
- `middleware.ts` - Express auth middleware
- `refresh.ts` - Token refresh logic

## Patterns
- Access tokens: 15 min expiry — limits exposure window
- Refresh tokens: 7 day expiry in Redis — survives server restarts
- All protected routes use `requireAuth` middleware — consistent enforcement

## Gotchas
- Redis must be running for auth tests
- Token blacklist checked on every request (performance impact)
- Refresh token rotation enabled — old tokens invalidated on use
```

The expanded version adds more patterns and gotchas discovered through usage, not upfront generation.
