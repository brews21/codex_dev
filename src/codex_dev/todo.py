from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

TODO_FILE = Path(".todos.json")
PRIORITIES = ("Urgent", "High", "Medium", "Low")
DEFAULT_PRIORITY = "Medium"
SORT_OPTIONS = ("created", "updated", "priority", "title")
DEFAULT_SORT = "created"
PRIORITY_ORDER = {priority: index for index, priority in enumerate(PRIORITIES)}


@dataclass
class Todo:
    id: int
    title: str
    priority: str = DEFAULT_PRIORITY
    done: bool = False
    created_at: str = ""
    updated_at: str = ""


def current_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_priority(priority: str | None) -> str:
    if not priority:
        return DEFAULT_PRIORITY

    for valid_priority in PRIORITIES:
        if priority.lower() == valid_priority.lower():
            return valid_priority
    return DEFAULT_PRIORITY


def normalize_sort(sort_by: str | None) -> str:
    if sort_by in SORT_OPTIONS:
        return sort_by
    return DEFAULT_SORT


def load_todos(path: Path = TODO_FILE) -> list[Todo]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as todo_file:
        items = json.load(todo_file)

    todos = []
    for item in items:
        timestamp = current_timestamp()
        todos.append(
            Todo(
                id=item["id"],
                title=item["title"],
                priority=normalize_priority(item.get("priority")),
                done=item.get("done", False),
                created_at=item.get("created_at", timestamp),
                updated_at=item.get("updated_at", item.get("created_at", timestamp)),
            )
        )
    return todos


def save_todos(todos: list[Todo], path: Path = TODO_FILE) -> None:
    with path.open("w", encoding="utf-8") as todo_file:
        json.dump([asdict(todo) for todo in todos], todo_file, indent=2)
        todo_file.write("\n")


def next_id(todos: list[Todo]) -> int:
    return max((todo.id for todo in todos), default=0) + 1


def add_todo(
    title: str,
    path: Path = TODO_FILE,
    priority: str = DEFAULT_PRIORITY,
) -> Todo:
    todos = load_todos(path)
    timestamp = current_timestamp()
    todo = Todo(
        id=next_id(todos),
        title=title,
        priority=normalize_priority(priority),
        created_at=timestamp,
        updated_at=timestamp,
    )
    todos.append(todo)
    save_todos(todos, path)
    return todo


def mark_done(todo_id: int, path: Path = TODO_FILE) -> Todo | None:
    return set_done(todo_id, True, path)


def set_done(todo_id: int, done: bool, path: Path = TODO_FILE) -> Todo | None:
    todos = load_todos(path)
    for todo in todos:
        if todo.id == todo_id:
            todo.done = done
            todo.updated_at = current_timestamp()
            save_todos(todos, path)
            return todo
    return None


def edit_todo(
    todo_id: int,
    path: Path = TODO_FILE,
    title: str | None = None,
    priority: str | None = None,
) -> Todo | None:
    todos = load_todos(path)
    for todo in todos:
        if todo.id == todo_id:
            if title is not None:
                todo.title = title
            if priority is not None:
                todo.priority = normalize_priority(priority)
            todo.updated_at = current_timestamp()
            save_todos(todos, path)
            return todo
    return None


def delete_todo(todo_id: int, path: Path = TODO_FILE) -> Todo | None:
    todos = load_todos(path)
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            save_todos(todos, path)
            return todo
    return None


def clear_completed(path: Path = TODO_FILE) -> int:
    todos = load_todos(path)
    remaining = [todo for todo in todos if not todo.done]
    removed_count = len(todos) - len(remaining)
    save_todos(remaining, path)
    return removed_count


def sort_todos(todos: list[Todo], sort_by: str = DEFAULT_SORT) -> list[Todo]:
    sort_by = normalize_sort(sort_by)
    if sort_by == "priority":
        return sorted(todos, key=lambda todo: (PRIORITY_ORDER[todo.priority], todo.id))
    if sort_by == "updated":
        return sorted(todos, key=lambda todo: (todo.updated_at, todo.id), reverse=True)
    if sort_by == "title":
        return sorted(todos, key=lambda todo: (todo.title.lower(), todo.id))
    return sorted(todos, key=lambda todo: (todo.created_at, todo.id))


def format_todos(todos: list[Todo]) -> str:
    if not todos:
        return "No todos yet."

    lines = []
    for todo in todos:
        status = "x" if todo.done else " "
        lines.append(f"{todo.id:>3}. [{status}] [{todo.priority}] {todo.title}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a local todo list.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", nargs="+", help="Todo text")
    add_parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        default=DEFAULT_PRIORITY,
        help="Todo priority",
    )

    list_parser = subparsers.add_parser("list", help="List todos")
    list_parser.add_argument(
        "--sort",
        choices=SORT_OPTIONS,
        default=DEFAULT_SORT,
        help="Sort todos",
    )

    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="Todo id")

    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="Todo id")

    edit_parser = subparsers.add_parser("edit", help="Edit a todo")
    edit_parser.add_argument("id", type=int, help="Todo id")
    edit_parser.add_argument("--title", nargs="+", help="Updated todo text")
    edit_parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        help="Updated todo priority",
    )

    subparsers.add_parser("clear-completed", help="Delete completed todos")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        todo = add_todo(" ".join(args.title), priority=args.priority)
        print(f"Added #{todo.id}: [{todo.priority}] {todo.title}")
    elif args.command == "list":
        print(format_todos(sort_todos(load_todos(), args.sort)))
    elif args.command == "done":
        todo = mark_done(args.id)
        print(f"Completed #{todo.id}: {todo.title}" if todo else "Todo not found.")
    elif args.command == "delete":
        todo = delete_todo(args.id)
        print(f"Deleted #{todo.id}: {todo.title}" if todo else "Todo not found.")
    elif args.command == "edit":
        title = " ".join(args.title) if args.title else None
        todo = edit_todo(args.id, title=title, priority=args.priority)
        print(f"Updated #{todo.id}: [{todo.priority}] {todo.title}" if todo else "Todo not found.")
    elif args.command == "clear-completed":
        removed_count = clear_completed()
        print(f"Removed {removed_count} completed todo(s).")


if __name__ == "__main__":
    main()
