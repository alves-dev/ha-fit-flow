# AGENTS.md

Use `sh dev/start-ha.sh` and `sh dev/stop-ha.sh` to manage the shared local Home Assistant instance. Use `sh dev/copy-to-core.sh` to deploy the `fit_flow` integration to that instance; it stops, copies, and starts the shared instance.

Run `uv run pytest` and `uv run ruff check .` for validation.
