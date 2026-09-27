## Contributing

- With issues:
  - Use the search tool before opening a new issue.
  - Please provide source code and commit SHA if you found a bug.
  - Review existing issues and provide feedback or react to them.

- With pull requests:
  - Open your pull request against `main`.
  - Your pull request should have no more than two commits; if not, squash them.
  - It should pass CI (`uv run ruff check .`, `uv run pytest` — see `.github/workflows/ci.yml`).
  - You should add or modify tests to cover your proposed code changes.
  - If your pull request changes user-facing behavior, update `README.md`.
