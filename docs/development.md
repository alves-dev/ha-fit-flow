# Development

Install dependencies with `uv sync`. Run `uv run pytest` and `uv run ruff check .`.
The SonarQube workflow runs the same tests with `--cov-report=xml` and sends
`coverage.xml` to the `ha-fit-flow` project at `https://sonar.alves-dev.com`.
Configure the repository secret `SONAR_TOKEN` in GitHub Actions; never store
the token in the repository.
Validate the integration structure with:

```sh
python3 /home/alves-dev/.codex/skills/home-assistant-integration-standards/scripts/validate_integration_structure.py .
```

For an end-to-end check, read [the shared local Home Assistant reference](local-home-assistant.md), then deploy with `sh dev/deploy-to-ha.sh` and use the shared Docker instance.
