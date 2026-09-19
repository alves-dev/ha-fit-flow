# AGENTS.md

## Setup Commands

- Install: `uv sync`
- Dev/runtime validation: `sh dev/copy-to-core.sh` (deploys to the shared Home Assistant instance)
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Integration structure validation: `python3 /home/alves-dev/.codex/skills/home-assistant-integration-standards/scripts/validate_integration_structure.py .`

Use `sh dev/start-ha.sh` and `sh dev/stop-ha.sh` to manage the shared local Home Assistant instance.

## Code Style

- Python 3.14-compatible code with Ruff rules from `pyproject.toml`.
- Keep Home Assistant integration lifecycle functions asynchronous.
- Keep domain calculations testable and isolated from Home Assistant where practical.
- Preserve the existing coordinator, storage, dispatcher, WebSocket, and sensor patterns documented in `context/knowledge/patterns/`.
- Follow decisions from `context/decisions/`.

## Context Files to Load

Before starting work, load relevant context:

- `@context/.context-mesh-framework.md`
- `@context/intent/project-intent.md` (always)
- `@context/intent/feature-*.md` (for the feature being changed)
- `@context/decisions/*.md` (relevant technical decisions)
- `@context/knowledge/patterns/*.md` (patterns to follow)

## Project Structure

```text
root/
├── AGENTS.md
├── context/
│   ├── .context-mesh-framework.md
│   ├── intent/
│   ├── decisions/
│   ├── knowledge/{patterns,anti-patterns}/
│   ├── agents/
│   └── evolution/
├── custom_components/fit_flow/
├── tests/
├── docs/
├── dev/
├── pyproject.toml
└── uv.lock
```

## AI Agent Rules

### Always

- Load context before implementing.
- Follow documented decisions and use documented patterns.
- Keep feature intent, technical decisions, and implementation knowledge separate.
- Update Context Mesh after any implementation or behavior change.

### Never

- Put library names, file paths, or code examples in feature intent files.
- Ignore documented decisions or use entries in `context/knowledge/anti-patterns/`.
- Leave context stale after changing behavior.

### After Any Changes

- Update the affected feature intent when user-visible behavior changes.
- Add outcomes to affected decision files when an approach changes or gains evidence.
- Update `context/evolution/changelog.md`.
- Add a learning note when a significant new insight is discovered.

## Definition of Done

- [ ] Relevant decision is documented before a new implementation approach is introduced.
- [ ] Code follows the documented patterns.
- [ ] `uv run pytest` passes.
- [ ] `uv run ruff check .` passes.
- [ ] Context reflects the resulting behavior and decisions.
- [ ] Changelog is updated.
