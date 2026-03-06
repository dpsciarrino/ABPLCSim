# Architecture

See the project report PDF for full detail. This file is a quick reference.

## Component Map

```
Request → Auth Middleware → Session Manager → [User Engine Instance]
                                                  ├── TagDB
                                                  ├── TimeKeeper Thread
                                                  └── Scan Cycle Engine

TagDB depends on:
  ├── TypeRegistry   (schema — what types exist)
  ├── Tag            (data — instances with typed values)
  └── PathResolver   (access — dot/index path traversal)
```

## Key Design Rules

- Instructions are pure functions: `(tag_db, operands, scan_timestamp) → bool`
- No instruction calls `time.time()` directly — all use `scan_timestamp`
- Tags are created externally and registered with TagDB (not created by TagDB)
- The TypeRegistry must be populated before any Tags are created
- Built-in types (BOOL, SINT, INT, DINT, REAL, TIMER, COUNTER) are pre-loaded
- Single-dimension arrays only for MVP (multi-dim deferred)
