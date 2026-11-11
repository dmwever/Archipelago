# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

This repo is a fork of Archipelago; the domain worked on here is the age2de world, so its docs live
in the world folder rather than at the repo root.

- **`worlds/age2de/CONTEXT.md`**: the glossary.
- **`worlds/age2de/docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context, inside the world:

```
worlds/age2de/
├── CONTEXT.md
├── docs/
│   ├── adr/
│   │   └── 0001-defeat-rules-live-in-per-player-logic.md
│   └── spec-<feature>.md
└── ...
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Speak in scenario terms, not file terms

What reaches the maintainer is what a trigger needs, which item pays for it, and which units move. Grid coordinates, object reference ids and trigger indices belong in an audit table, not in a question put to them: a question they have to decode is a round spent.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
