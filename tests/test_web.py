from pathlib import Path

from codex_dev.todo import load_todos
from codex_dev.web import create_app


def test_web_adds_todo_with_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    app = create_app(todo_file)
    client = app.test_client()

    response = client.post(
        "/todos",
        data={"title": "Fix outage", "priority": "Urgent"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Urgent" in response.text
    assert load_todos(todo_file)[0].priority == "Urgent"


def test_web_sorts_todos_by_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    app = create_app(todo_file)
    client = app.test_client()

    client.post("/todos", data={"title": "Low task", "priority": "Low"})
    client.post("/todos", data={"title": "Urgent task", "priority": "Urgent"})
    response = client.get("/?sort=priority")

    assert response.status_code == 200
    assert response.text.index("Urgent task") < response.text.index("Low task")


def test_web_edits_todo_title_and_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    app = create_app(todo_file)
    client = app.test_client()

    client.post("/todos", data={"title": "Old task", "priority": "Low"})
    response = client.post(
        "/todos/1/edit",
        data={"title": "New task", "priority": "High"},
        follow_redirects=True,
    )

    todo = load_todos(todo_file)[0]
    assert response.status_code == 200
    assert "New task" in response.text
    assert todo.title == "New task"
    assert todo.priority == "High"
