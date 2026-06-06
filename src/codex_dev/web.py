from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from codex_dev.todo import (
    DEFAULT_PRIORITY,
    PRIORITIES,
    SORT_OPTIONS,
    TODO_FILE,
    add_todo,
    clear_completed,
    delete_todo,
    load_todos,
    normalize_sort,
    set_done,
    sort_todos,
)


def create_app(todo_file: Path = TODO_FILE) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        sort_by = normalize_sort(request.args.get("sort"))
        todos = sort_todos(load_todos(todo_file), sort_by)
        active_todos = [todo for todo in todos if not todo.done]
        completed_todos = [todo for todo in todos if todo.done]
        return render_template(
            "index.html",
            active_todos=active_todos,
            completed_todos=completed_todos,
            priorities=PRIORITIES,
            sort_options=SORT_OPTIONS,
            current_sort=sort_by,
            default_priority=DEFAULT_PRIORITY,
            total_count=len(todos),
            active_count=len(active_todos),
            completed_count=len(completed_todos),
        )

    @app.post("/todos")
    def create_todo():
        title = request.form.get("title", "").strip()
        priority = request.form.get("priority", DEFAULT_PRIORITY)
        if title:
            add_todo(title, todo_file, priority)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/toggle")
    def toggle_todo(todo_id: int):
        done = request.form.get("done") == "on"
        set_done(todo_id, done, todo_file)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/delete")
    def remove_todo(todo_id: int):
        delete_todo(todo_id, todo_file)
        return redirect(url_for("index"))

    @app.post("/todos/clear-completed")
    def remove_completed():
        clear_completed(todo_file)
        return redirect(url_for("index"))

    return app


def main() -> None:
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
