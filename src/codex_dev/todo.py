from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

TODO_FILE = Path(".todos.json")
PRIORITIES = ("Urgent", "High", "Medium", "Low")
DEFAULT_PRIORITY = "Medium"


@dataclass
class Todo:
    id: int
    title: str
    priority: str = DEFAULT_PRIORITY
    done: bool = False


def normalize_priority(priority: str | None) -> str:
    if not priority:
        return DEFAULT_PRIORITY

    for valid_priority in PRIORITIES:
        if priority.lower() == valid_priority.lower():
            return valid_priority
    return DEFAULT_PRIORITY


def load_todos(path: Path = TODO_FILE) -> list[Todo]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as todo_file:
        items = json.load(todo_file)

    return [
        Todo(
            id=item["id"],
            title=item["title"],
            priority=normalize_priority(item.get("priority")),
            done=item.get("done", False),
        )
        for item in items
    ]


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
    todo = Todo(id=next_id(todos), title=title, priority=normalize_priority(priority))
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

    subparsers.add_parser("list", help="List todos")

    done_parser = subparsers.add_parser("done", help="Mark a todo as done")
    done_parser.add_argument("id", type=int, help="Todo id")

    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="Todo id")

    subparsers.add_parser("clear-completed", help="Delete completed todos")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        todo = add_todo(" ".join(args.title), priority=args.priority)
        print(f"Added #{todo.id}: [{todo.priority}] {todo.title}")
    elif args.command == "list":
        print(format_todos(load_todos()))
    elif args.command == "done":
        todo = mark_done(args.id)
        print(f"Completed #{todo.id}: {todo.title}" if todo else "Todo not found.")
    elif args.command == "delete":
        todo = delete_todo(args.id)
        print(f"Deleted #{todo.id}: {todo.title}" if todo else "Todo not found.")
    elif args.command == "clear-completed":
        removed_count = clear_completed()
        print(f"Removed {removed_count} completed todo(s).")


if __name__ == "__main__":
    main()
