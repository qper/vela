# Vela
**Version 0.0.1** (prototype)

> Diagrams as elegant code.

> A minimal, readable, declarative language for describing modern diagrams as code.  
> Designed to be easy to write, easy to read, and produce visually stylish results when rendered by the Vela Engine.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Design Goals](#2-design-goals)
3. [Quick Start](#3-quick-start)
4. [Language Overview](#4-language-overview)
5. [Lexical Structure](#5-lexical-structure)
6. [Statements](#6-statements)
   - 6.1 Theme Declaration
   - 6.2 Node Declaration
   - 6.3 Edge Declaration
7. [Attributes & Styles](#7-attributes--styles)
8. [Order of Declarations](#8-order-of-declarations)
9. [Required vs Optional](#9-required-vs-optional)
10. [Comments](#10-comments)
11. [Examples](#11-examples)
    - 11.1 Minimal
    - 11.2 Simple Architecture
    - 11.3 Medium Complexity
    - 11.4 Advanced Example
12. [Rendering & Themes](#12-rendering--themes)
13. [Export Formats](#13-export-formats)
14. [Limitations (v0.0.1)](#14-limitations-v001)
15. [Future Roadmap](#15-future-roadmap)
16. [Best Practices](#16-best-practices)
17. [Grammar (Informal)](#17-grammar-informal)
18. [Changelog](#18-changelog)

---

## 1. Introduction

**Vela** is a small domain-specific language (DSL) created for describing diagrams in a human-readable text form. The text is then rendered into a modern, stylish SVG (or PNG) image by the companion engine.

It is intentionally simple. The goal of version 0.0.1 is to provide a solid, usable foundation that already produces attractive results while remaining easy to learn in a few minutes.

This document is the official language reference for **v0.0.1**.

---

## 2. Design Goals

Following established best practices for external textual DSLs:

- **Readability first** — the language should be understandable even by people who do not write code every day.
- **Minimal cognitive load** — few constructs, consistent syntax.
- **Declarative** — you describe *what* the diagram contains, not *how* to draw it.
- **Progressive complexity** — simple diagrams require almost no syntax; advanced features are optional.
- **Visual quality** — the language exists to produce modern, stylish diagrams, not just functional ones.
- **Tool-friendly** — easy to parse, version-control, and embed in documentation.

---

## 3. Quick Start

```text
Frontend: React App
API: NestJS
DB: PostgreSQL

Frontend --> API
API --> DB
```

This is a complete, valid diagram.

---

## 4. Language Overview

A Vela document consists of zero or more **statements**, each on its own line:

| Statement          | Purpose                          | Required? |
|--------------------|----------------------------------|---------|
| `theme: ...`       | Choose visual theme              | No      |
| `NodeID: Label`    | Declare a node                   | Yes*    |
| `A --> B`          | Declare a connection (edge)      | No      |
| `// comment`       | Comment                          | No      |

\* At least one node is required to produce a non-empty diagram.

Nodes can be declared explicitly or created implicitly when they appear in an edge.

---

## 5. Lexical Structure

- **Encoding**: UTF-8
- **Line-based**: each statement occupies one logical line
- **Whitespace**: leading/trailing whitespace is ignored; indentation is currently not significant
- **Identifiers** (`NodeID`): start with a letter or underscore, followed by letters, digits or underscores  
  Examples: `Frontend`, `user_service`, `DB1`, `_internal`
- **Labels**: free text (can contain spaces). May be enclosed in double or single quotes.
- **Case sensitivity**: identifiers are case-sensitive (`API` ≠ `api`)
- **Comments**: lines starting with `//` or `#` are ignored

---

## 6. Statements

### 6.1 Theme Declaration

```text
theme: <theme-name>
```

**Supported theme names** (v0.0.1):

| Name            | Description                              |
|-----------------|------------------------------------------|
| `modern-dark`   | Dark background, indigo accents (default)|
| `modern-light`  | Clean light theme                        |
| `glass`         | Glassmorphism / translucent cards        |
| `neo`           | Neo-brutalist (bold borders, yellow)     |

- Optional.
- If omitted → `modern-dark` is used.
- Only the last `theme:` statement is taken into account.
- Theme can also be overridden in the UI of the prototype.

**Example:**
```text
theme: glass
```

---

### 6.2 Node Declaration

```text
NodeID: Label
NodeID: Label {style: stylename}
NodeID: "Label with spaces" {style: primary, type: service}
```

**Parts:**

| Part       | Required | Description |
|------------|----------|-------------|
| `NodeID`   | Yes      | Unique identifier used in edges |
| `:`        | Yes      | Separator |
| `Label`    | Yes      | Human-readable text shown on the node |
| `{...}`    | No       | Optional attribute block |

**Attribute block** (inside curly braces):

```text
{style: primary}
{style: database}
{style: success, type: db}     // type is currently treated as alias for style
```

Multiple attributes are separated by commas.

**Available styles** (v0.0.1):

| Style      | Typical use                  | Visual character          |
|------------|------------------------------|---------------------------|
| `primary`  | Main entry points            | Deep indigo               |
| `success`  | Positive / healthy services  | Green                     |
| `warning`  | Auth, caution                | Amber / yellow            |
| `danger`   | Queues, critical, errors     | Red                       |
| `muted`    | Secondary / cache            | Slate gray                |
| `glass`    | Highlighted translucent      | Semi-transparent indigo   |
| `database` | Databases                    | Cyan                      |
| `service`  | Backend services             | Purple                    |

If no style is specified, the node uses the default colors of the current theme.

---

### 6.3 Edge Declaration

```text
Source --> Target
Source --> Target : "label"
Source --> Target : label without quotes
Source -> Target                // single dash also accepted
Source → Target                 // unicode arrow also accepted
```

**Parts:**

| Part       | Required | Description |
|------------|----------|-------------|
| `Source`   | Yes      | Existing or new NodeID |
| `-->`      | Yes      | Arrow (or `->` / `→`) |
| `Target`   | Yes      | Existing or new NodeID |
| `: label`  | No       | Optional text shown on the edge |

- If a NodeID appears in an edge but was never declared, it is automatically created with `label = NodeID`.
- Multiple edges between the same pair of nodes are currently allowed (they will overlap).

---

## 7. Attributes & Styles

Attributes are written inside `{ }` after the label.

Currently supported keys:

- `style` — visual style of the node (see table above)
- `type` — treated as an alias of `style` (future versions may distinguish them)

Unknown attributes are currently ignored (forward-compatible).

---

## 8. Order of Declarations

The order of statements is **mostly free**, but the following conventions are recommended for readability:

```text
1. theme: ...                    (optional, at the top)
2. // Nodes section
3. All node declarations
4. // Edges section
5. All edge declarations
```

You may interleave nodes and edges freely. The parser does not enforce order.

**Recommended style** (used in all official examples):

```text
theme: modern-dark

// === Nodes ===
A: Alpha {style: primary}
B: Beta
C: Gamma {style: database}

// === Edges ===
A --> B : "calls"
B --> C
```

---

## 9. Required vs Optional

| Construct                  | Required for a valid diagram? | Notes |
|---------------------------|-------------------------------|-------|
| At least one node         | Yes                           | Otherwise empty diagram |
| Explicit node declarations| No                            | Nodes can be created via edges |
| Edges                     | No                            | You can have isolated nodes |
| Theme                     | No                            | Defaults to `modern-dark` |
| Styles / attributes       | No                            | Defaults used |
| Edge labels               | No                            | |
| Comments                  | No                            | |

**Minimal valid document:**
```text
Hello: World
```

**Another minimal valid document (implicit nodes):**
```text
A --> B
```

---

## 10. Comments

```text
// This is a comment
# This is also a comment (alternative style)
```

- Comments must be on their own line (or at the beginning of the line).
- Trailing comments on the same line as a statement are **not** supported in v0.0.1.

---

## 11. Examples

### 11.1 Minimal

```text
Start: Begin
End: Finish

Start --> End
```

### 11.2 Simple Architecture

```text
theme: modern-dark

Frontend: React SPA {style: primary}
Backend: Node.js API {style: service}
Database: PostgreSQL {style: database}

Frontend --> Backend : "REST"
Backend --> Database
```

### 11.3 Medium Complexity (Microservices)

```text
theme: glass

// Entry
Web: Web App {style: primary}
Mobile: Mobile App {style: primary}

// Edge
Gateway: API Gateway {style: service}

// Services
Auth: Auth Service {style: warning}
Users: User Service {style: success}
Orders: Order Service
Payments: Payment Service {style: danger}

// Data
DB: PostgreSQL {style: database}
Cache: Redis {style: muted}
Queue: Kafka {style: danger}

// Connections
Web --> Gateway
Mobile --> Gateway
Gateway --> Auth : "JWT"
Gateway --> Users
Gateway --> Orders
Orders --> Payments
Users --> DB
Orders --> DB
Payments --> DB
Users --> Cache
Orders --> Queue : "events"
```

### 11.4 Advanced Example (with many styles)

```text
theme: modern-light

// Presentation layer
UI: Next.js Frontend {style: primary}
Admin: Admin Panel {style: glass}

// API layer
GW: Kong Gateway {style: service}
BFF: Backend-for-Frontend {style: service}

// Domain services
Catalog: Catalog Service {style: success}
Cart: Cart Service
Checkout: Checkout Service {style: warning}
Notify: Notification Service {style: muted}

// Infrastructure
PG: PostgreSQL {style: database}
Mongo: MongoDB {style: database}
Redis: Redis Cache {style: muted}
Rabbit: RabbitMQ {style: danger}
S3: Object Storage {style: muted}

// Flow
UI --> GW
Admin --> GW
GW --> BFF
BFF --> Catalog
BFF --> Cart
BFF --> Checkout
Checkout --> Notify : "email/sms"
Catalog --> PG
Cart --> Redis
Checkout --> PG
Checkout --> Rabbit : "order.created"
Notify --> Rabbit
Catalog --> S3 : "images"
Cart --> Mongo
```

---

## 12. Rendering & Themes

The prototype renderer:

- Performs a simple hierarchical (layered) layout based on topological order.
- Draws nodes as rounded rectangles with soft shadows.
- Draws edges as smooth cubic Bézier curves with arrowheads.
- Places optional edge labels in small pills.

You can change the theme either:

1. Inside Vela (`theme: glass`)
2. Via the dropdown in the prototype UI (overrides Vela value)

---

## 13. Export Formats

From the prototype UI:

| Format | Description                              | Quality |
|--------|------------------------------------------|---------|
| SVG    | Vector, infinitely scalable, editable    | Perfect |
| PNG    | Raster, 2× retina resolution             | High    |

The SVG is self-contained and can be used directly in web pages, Notion, GitHub, Figma, etc.

---

## 14. Limitations (v0.0.1)

This is an early prototype. Current limitations:

- No groups / containers / subgraphs
- No manual positioning (`x`, `y`)
- No custom colors (only named styles)
- No icons
- No bidirectional edges (`<-->`)
- No edge styles (dashed, thick, colored)
- No notes / annotations
- Layout is simple hierarchical only (no force-directed, no orthogonal)
- No cycles handling beyond basic topological sort
- No multi-line labels
- No font-size / size control per node
- Parser is intentionally forgiving but not extremely strict

These will be addressed in future versions.

---

## 15. Future Roadmap (high level)

**v0.1**
- Groups / containers
- Manual positions and ranks
- More edge types
- Basic icons

**v0.2**
- Custom themes via JSON
- Orthogonal routing
- Notes and annotations
- Sequence-diagram inspired syntax

**Later**
- Interactive mode
- VS Code extension / language server
- CLI renderer
- Animation support

---

## 16. Best Practices

Drawn from established DSL design literature (Fowler, Mernik et al., and real-world examples such as Mermaid, D2, PlantUML):

1. **Prefer readability over terseness**  
   `UserService: User Service {style: success}` is better than ultra-short cryptic IDs.

2. **Use meaningful NodeIDs**  
   They appear both in the code and as secondary text on the node.

3. **Group related statements with comments**
   ```text
   // === Frontend ===
   // === Backend services ===
   // === Data stores ===
   ```

4. **Declare nodes before edges** when the diagram is non-trivial.  
   It makes the source easier to scan.

5. **Keep one statement per line**.

6. **Use styles intentionally** — they communicate meaning (database vs service vs entrypoint).

7. **Start simple**. Add styles and labels only when they improve understanding.

8. **Version your diagram files** together with the code they describe.

---

## 17. Grammar (Informal)

```ebnf
document        ::= { statement | comment | empty-line }

statement       ::= theme_stmt | node_stmt | edge_stmt

theme_stmt      ::= "theme" ":" theme_name
theme_name      ::= "modern-dark" | "modern-light" | "glass" | "neo"

node_stmt       ::= identifier ":" label [ attribute_block ]
label           ::= text | quoted_string
attribute_block ::= "{" { attribute } "}"
attribute       ::= key ":" value
key             ::= "style" | "type" | identifier
value           ::= identifier

edge_stmt       ::= identifier arrow identifier [ ":" label ]
arrow           ::= "-->" | "->" | "→"

comment         ::= ("//" | "#") { any-char }
identifier      ::= letter { letter | digit | "_" }
quoted_string   ::= '"' { any-char } '"' | "'" { any-char } "'"
```

---

## 18. Changelog

### v0.0.1 — 2026-07-28
- Initial public prototype language
- Nodes, edges, basic styles, four themes
- Hierarchical layout
- SVG + PNG export
- This documentation

---

**Happy diagramming!**

If you find ambiguities, missing features, or have ideas for the next version — feedback is very welcome.
