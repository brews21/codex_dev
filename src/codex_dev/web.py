from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from codex_dev.todo import (
    add_todo,
    clear_completed,
    delete_todo,
    load_todos,
    set_done,
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        todos = load_todos()
        active_todos = [todo for todo in todos if not todo.done]
        completed_todos = [todo for todo in todos if todo.done]
        return render_template(
            "index.html",
            active_todos=active_todos,
            completed_todos=completed_todos,
            total_count=len(todos),
            active_count=len(active_todos),
            completed_count=len(completed_todos),
        )

    @app.post("/todos")
    def create_todo():
        title = request.form.get("title", "").strip()
        if title:
            add_todo(title)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/toggle")
    def toggle_todo(todo_id: int):
        done = request.form.get("done") == "on"
        set_done(todo_id, done)
        return redirect(url_for("index"))

    @app.post("/todos/<int:todo_id>/delete")
    def remove_todo(todo_id: int):
        delete_todo(todo_id)
        return redirect(url_for("index"))

    @app.post("/todos/clear-completed")
    def remove_completed():
        clear_completed()
        return redirect(url_for("index"))

    return app


def main() -> None:
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
