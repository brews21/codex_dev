from pathlib import Path

from codex_dev.todo import (
    DEFAULT_PRIORITY,
    PRIORITIES,
    Todo,
    add_todo,
    clear_completed,
    delete_todo,
    format_todos,
    load_todos,
    mark_done,
    set_done,
)


def test_add_todo_saves_item(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"

    todo = add_todo("Buy milk", todo_file)

    assert todo.id == 1
    assert todo.title == "Buy milk"
    assert todo.priority == DEFAULT_PRIORITY
    assert load_todos(todo_file) == [todo]


def test_add_todo_accepts_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"

    todo = add_todo("Restart server", todo_file, priority="Urgent")

    assert todo.priority == "Urgent"
    assert load_todos(todo_file)[0].priority == "Urgent"


def test_load_todos_defaults_missing_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    todo_file.write_text('[{"id": 1, "title": "Old todo", "done": false}]')

    todo = load_todos(todo_file)[0]

    assert todo.priority == DEFAULT_PRIORITY


def test_mark_done_updates_matching_todo(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Write tests", todo_file)

    todo = mark_done(1, todo_file)

    assert todo is not None
    assert todo.done is True
    assert load_todos(todo_file)[0].done is True


def test_set_done_can_reopen_todo(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Review web app", todo_file)
    mark_done(1, todo_file)

    todo = set_done(1, False, todo_file)

    assert todo is not None
    assert todo.done is False
    assert load_todos(todo_file)[0].done is False


def test_delete_todo_removes_matching_todo(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Keep", todo_file)
    add_todo("Remove", todo_file)

    deleted = delete_todo(2, todo_file)

    assert deleted is not None
    assert [todo.title for todo in load_todos(todo_file)] == ["Keep"]


def test_clear_completed_removes_only_done_todos(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Done", todo_file)
    add_todo("Still open", todo_file)
    mark_done(1, todo_file)

    removed_count = clear_completed(todo_file)

    assert removed_count == 1
    assert [todo.title for todo in load_todos(todo_file)] == ["Still open"]


def test_format_todos_shows_statuses() -> None:
    rendered = format_todos([
        Todo(id=1, title="Open", priority="High"),
    ])

    assert "[ ] [High] Open" in rendered


def test_available_priorities_are_expected() -> None:
    assert PRIORITIES == ("Urgent", "High", "Medium", "Low")
