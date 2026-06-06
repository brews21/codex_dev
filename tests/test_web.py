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
