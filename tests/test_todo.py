from pathlib import Path

from codex_dev.todo import (
    DEFAULT_PRIORITY,
    PRIORITIES,
    SORT_OPTIONS,
    Todo,
    add_todo,
    clear_completed,
    delete_todo,
    edit_todo,
    format_todos,
    load_todos,
    mark_done,
    set_done,
    sort_todos,
)


def test_add_todo_saves_item(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"

    todo = add_todo("Buy milk", todo_file)

    assert todo.id == 1
    assert todo.title == "Buy milk"
    assert todo.priority == DEFAULT_PRIORITY
    assert todo.created_at
    assert todo.updated_at == todo.created_at
    assert load_todos(todo_file) == [todo]


def test_add_todo_accepts_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"

    todo = add_todo("Restart server", todo_file, priority="Urgent")

    assert todo.priority == "Urgent"
    assert load_todos(todo_file)[0].priority == "Urgent"


def test_load_todos_defaults_missing_metadata(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    todo_file.write_text('[{"id": 1, "title": "Old todo", "done": false}]')

    todo = load_todos(todo_file)[0]

    assert todo.priority == DEFAULT_PRIORITY
    assert todo.created_at
    assert todo.updated_at == todo.created_at


def test_mark_done_updates_matching_todo(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Write tests", todo_file)

    todo = mark_done(1, todo_file)

    assert todo is not None
    assert todo.done is True
    assert load_todos(todo_file)[0].done is True


def test_mark_done_updates_timestamp(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    todo = add_todo("Write tests", todo_file)

    done_todo = mark_done(1, todo_file)

    assert done_todo is not None
    assert done_todo.updated_at >= todo.updated_at


def test_set_done_can_reopen_todo(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    add_todo("Review web app", todo_file)
    mark_done(1, todo_file)

    todo = set_done(1, False, todo_file)

    assert todo is not None
    assert todo.done is False
    assert load_todos(todo_file)[0].done is False


def test_edit_todo_updates_title_and_priority(tmp_path: Path) -> None:
    todo_file = tmp_path / "todos.json"
    todo = add_todo("Old title", todo_file, priority="Low")

    edited = edit_todo(1, todo_file, title="New title", priority="Urgent")

    assert edited is not None
    assert edited.title == "New title"
    assert edited.priority == "Urgent"
    assert edited.updated_at >= todo.updated_at
    assert load_todos(todo_file)[0].title == "New title"


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
    rendered = format_todos(
        [
            Todo(id=1, title="Open", priority="High"),
        ]
    )

    assert "[ ] [High] Open" in rendered


def test_available_priorities_are_expected() -> None:
    assert PRIORITIES == ("Urgent", "High", "Medium", "Low")


def test_sort_todos_by_priority() -> None:
    todos = [
        Todo(id=1, title="Later", priority="Low"),
        Todo(id=2, title="Now", priority="Urgent"),
        Todo(id=3, title="Soon", priority="High"),
    ]

    sorted_todos = sort_todos(todos, "priority")

    assert [todo.title for todo in sorted_todos] == ["Now", "Soon", "Later"]


def test_sort_todos_by_updated_newest_first() -> None:
    todos = [
        Todo(id=1, title="Older", updated_at="2026-01-01T09:00:00+00:00"),
        Todo(id=2, title="Newer", updated_at="2026-01-02T09:00:00+00:00"),
    ]

    sorted_todos = sort_todos(todos, "updated")

    assert [todo.title for todo in sorted_todos] == ["Newer", "Older"]


def test_sort_options_are_expected() -> None:
    assert SORT_OPTIONS == ("created", "updated", "priority", "title")
