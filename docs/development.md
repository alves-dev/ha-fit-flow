# Development

Install dependencies with `uv sync`. Run `uv run pytest` and `uv run ruff check .`.
Validate the integration structure with:

```sh
python3 /home/alves-dev/.codex/skills/home-assistant-integration-standards/scripts/validate_integration_structure.py .
```

For an end-to-end check, deploy with `sh dev/copy-to-core.sh` and use the local Home Assistant instance.
