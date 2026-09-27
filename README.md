## Ferir

Ferir runs coding agents on real codebases: clone any git repository (public or private), execute [Pi](https://pi.dev/) headless in Docker, and return a unified diff - so you can review, apply, or open a PR from automated tasks.


### Prerequisites

- Python 3.11+.
- Docker.
- Git.
- LLM Provider.


### Install

```bash
uv add ferir
```

### Usage

```python
import ferir

result = ferir.run(
    ferir.RunRequest(
        work_dir="/tmp/basement",
        id="550e8400-e29b-41d4-a716-446655440000",
        repo_url="https://github.com/Clivern/Diffsay.git",
        prompt="Add Gemfile.lock to LOW_PRIORITY_FILES",
        pi_model="openrouter/anthropic/claude-sonnet-4.5",
        proxy_url="http://host.docker.internal:8080/api",
        docker_image="clivern/ferir:v0.2.0",
        container=ferir.Container(
            memory="2g",
            cpus="1",
            init_script=".ferir/init.sh",
            init_bash="apt-get update && apt-get install -y jq",
        ),
        cleanup=True,
    ),
    timeout=90 * 60,
)

# result.patch, result.summary, result.total_tokens, result.changed_files, result.repo_dir, result.out_dir
```


### Private repositories

HTTPS:

```python
git_clone_auth=ferir.GitCloneAuth(token=os.environ["GITHUB_TOKEN"]),
repo_url="https://github.com/org/private.git",
```

SSH:

```python
git_clone_auth=ferir.GitCloneAuth(
    ssh_private_key_path=os.path.expanduser("~/.ssh/id_ed25519"),
),
repo_url="git@github.com:org/private.git",
```


### Examples

```bash
uv run python examples/example1.py
```

| Example | What it shows |
|---|---|
| `examples/example1.py` | Five concurrent runs against one repository |
| `examples/example2.py` | Read-only codebase question |
| `examples/example3.py` | Init installs Python, then Pi edits and runs tests |
| `examples/example4.py` | The timeout kills a long init script |


### Develop

```bash
uv sync
uv run ruff check .
uv run pytest -m "not network"
```
