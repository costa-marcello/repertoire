# README Style Guide

## Common Mistakes

- **No install steps** - Never assume setup is obvious
- **No examples** - Show, don't just tell
- **Wall of text** - Use headers, tables, lists
- **Stale content** - Add a "Last reviewed" date to config READMEs, and to internal ones that drift (see `section-checklist.md`)
- **Generic tone** - Write for YOUR audience

## Prose Mistakes with Examples

### 1. Vague Descriptions

| Before | After | Why |
|--------|-------|-----|
| "A powerful tool for developers" | "Converts Markdown to PDF with syntax highlighting" | Says what it actually does |
| "Makes things easier" | "Reduces deploy time from 10 minutes to 30 seconds" | Concrete benefit |
| "Handles various file types" | "Supports CSV, JSON, XML, and Parquet" | Specific, scannable |

### 2. Missing the "Why"

| Before | After | Why |
|--------|-------|-----|
| "Uses Redis for caching" | "Uses Redis for caching — reduces API calls by 90% on repeat queries" | Explains the benefit |
| "Written in Rust" | "Written in Rust for memory safety and 10x faster parsing than Python equivalent" | Justifies the choice |

### 3. Assuming Context

| Before | After | Why |
|--------|-------|-----|
| "Run the usual setup" | "Run `npm install && npm run build`" | Explicit commands |
| "Configure the environment" | "Copy `.env.example` to `.env` and set `DATABASE_URL`" | Step-by-step |
| "Works like other CLI tools" | "Uses standard flags: `-v` for verbose, `-h` for help" | Don't assume familiarity |

### 4. Burying Important Info

| Before | After | Why |
|--------|-------|-----|
| "Note: requires Node 18+" (at the bottom) | **Prerequisites** section at the top | Critical info upfront |
| "By the way, this deletes your data" (mid-paragraph) | **Warning** callout with icon | Dangerous actions highlighted |

### 5. Over-Explaining Simple Things

| Before | After | Why |
|--------|-------|-----|
| "To install the package, you'll want to open your terminal application and type the following command..." | `npm install mytool` | Let the code speak |
| "The next step in the process is to..." | (just show the next step) | Remove filler |
