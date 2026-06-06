# AGENTS.md

## Python Environment

- All Python tasks must be completed inside a virtual environment.
- For the `codex_dev` app, use the existing project virtual environment at `.venv`.
- Run Python commands through `.venv/bin/python` unless the virtual environment is already activated.
- Install dependencies into `.venv`, not the system Python environment.
- Do not install Python modules into the root/system Python environment.
- Do not use `sudo pip`, global `pip install`, or `python -m pip install` against system Python.
- If `.venv` is missing, create it with `python3 -m venv .venv` before installing dependencies.
- Prefer `.venv/bin/python -m pip ...` so package installs always target the repo virtual environment.

Examples:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m pip install -r requirements.txt
```
