# codex_dev
Testing VS Code and Codex AI. Creating Python Apps

## Todo List

This repo includes a small todo list app with both command-line and web interfaces.

### Install for local development

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/pre-commit install
```

### Run the web app

With the wrapper script:

```bash
./run_todo_web.sh
```

Or manually:

```bash
PYTHONPATH=src flask --app codex_dev.web:create_app run --debug
```

Open http://127.0.0.1:5000 in your browser.

After installing locally, you can also run:

```bash
todo-web
```

### Run checks

```bash
.venv/bin/python -m pytest
.venv/bin/pre-commit run --all-files
```

### Run the CLI

```bash
PYTHONPATH=src python -m codex_dev.todo add Buy milk --priority High
PYTHONPATH=src python -m codex_dev.todo list --sort priority
PYTHONPATH=src python -m codex_dev.todo done 1
PYTHONPATH=src python -m codex_dev.todo edit 1 --title Buy oat milk --priority Urgent
PYTHONPATH=src python -m codex_dev.todo delete 1
PYTHONPATH=src python -m codex_dev.todo clear-completed
```

Priorities are `Urgent`, `High`, `Medium`, and `Low`. New todos default to `Medium`.
Sort options are `created`, `updated`, `priority`, and `title`.

Todo data is saved in `.todos.json`, which is ignored by git.

After installing locally, you can also run the CLI with:

```bash
todo add Buy milk --priority High
todo list --sort priority
todo edit 1 --title Buy oat milk --priority Urgent
```
