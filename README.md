# PLC Emulator

A Python-based software emulator for Allen-Bradley ControlLogix Programmable Logic Controllers.
Replicates the deterministic scan-cycle behavior of a real PLC, supporting Ladder Logic instruction
execution, L5X project import/export, and a web-based tag monitoring dashboard.

---

## Project Status

| Milestone | Status |
|---|---|
| v0.1.0 — Core engine, TagDB, bit logic | 🔧 In Progress |
| v0.2.0 — Timers and counters | ⏳ Pending |
| v0.3.0 — L5X import | ⏳ Pending |
| v0.4.0 — REST API + Session Manager | ⏳ Pending |
| v0.5.0 — Authentication + Database | ⏳ Pending |
| v0.6.0 — Web UI | ⏳ Pending |
| v1.0.0 — MVP public release | ⏳ Pending |

---

## Architecture Overview

```
Request → Auth Middleware → Session Manager → [User Engine Instance]
                                                  ├── TagDB
                                                  ├── TimeKeeper Thread
                                                  └── Scan Cycle Engine
```

Each authenticated user receives their own isolated engine instance.
See `docs/architecture.md` for full detail.

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/yourusername/plc-emulator.git
cd plc-emulator
pip install -r requirements.txt
```

### Running Tests

```bash
pytest tests/ -v
```

### Running the API (localhost only — no auth during early development)

```bash
uvicorn api.main:app --reload
```

---

## Environment Configuration

Copy `.env.example` to `.env.development` and adjust values as needed.
Never commit `.env.*` files (except `.env.example`) to source control.

```bash
cp .env.example .env.development
```

---

## Project Structure

```
plc-emulator/
├── engine/
│   ├── type_registry.py       # Type definitions and UDT registry
│   ├── tag.py                 # Tag and value dataclasses
│   ├── tag_db.py              # TagDB — stores and retrieves Tag instances
│   ├── path_resolver.py       # Parses and traverses dot/index access paths
│   ├── session_manager.py     # Per-user engine lifecycle management
│   ├── scan_cycle.py          # Main scan loop
│   ├── time_keeper.py         # High-resolution time thread
│   └── instructions/
│       ├── bit_logic.py       # XIC, XIO, OTE, OTL, OTU, ONS
│       ├── timers.py          # TON, TOF, RTO
│       └── counters.py        # CTU, CTD, RES
├── parser/
│   ├── l5x_parser.py          # .L5X XML → internal representation
│   └── l5x_exporter.py        # Internal representation → .L5X XML
├── db/
│   ├── database.py            # SQLAlchemy engine and session factory
│   ├── models.py              # ORM models: User, Program, SessionMeta
│   └── crud.py                # DB helper functions
├── middleware/
│   └── auth.py                # JWT validation middleware
├── api/
│   ├── main.py                # FastAPI app entry point
│   ├── routes/
│   │   ├── auth.py            # /auth/register, /auth/token, /auth/me
│   │   ├── tags.py            # /tags GET/POST
│   │   ├── program.py         # /program upload/download
│   │   └── scan.py            # /scan start/stop/step
│   └── websockets/
│       └── tag_feed.py        # Live tag push to frontend
├── frontend/                  # React + Vite SPA (added at v0.6.0)
├── tests/
│   ├── test_type_registry.py
│   ├── test_tag.py
│   ├── test_tag_db.py
│   ├── test_path_resolver.py
│   ├── test_instructions.py
│   ├── test_scan_cycle.py
│   ├── test_session_manager.py
│   ├── test_auth.py
│   └── test_l5x_parser.py
├── docs/
│   ├── architecture.md
│   └── known_limitations.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Known Limitations

See `docs/known_limitations.md` for documented behavioral differences
between this emulator and a physical ControlLogix controller.

---

## License

All rights reserved. Public use is permitted. Contributions are not accepted.
