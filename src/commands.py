from pathlib import PurePosixPath

def require_directory(nodes, path):
    """Проверяет, что путь существует и является папкой."""
    if path not in nodes or nodes[path] is not None:
        raise ValueError(f"Не является папкой: {path}")

def resolve_path(state, text):
    """Находит виртуальный путь, проверяя папки по пути."""
    nodes = state["nodes"]
    parts = []
    if not text.startswith("/"):
        parts = state["cwd"].strip("/").split("/")
        parts = [part for part in parts if part]

    for part in text.split("/"):
        current = "/" + "/".join(parts)
        require_directory(nodes, current)

        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)

    path = "/" + "/".join(parts)
    if path not in nodes:
        raise ValueError(f"Путь не найден: {path}")
    return path


def command_ls(args, state):
    """Выводит файл или непосредственное содержимое папки."""
    if len(args) > 1:
        raise ValueError("ls принимает не более одного пути")

    path = resolve_path(state, args[0] if args else ".")
    nodes = state["nodes"]
    if nodes[path] is not None:
        print(PurePosixPath(path).name)
        return

    for child in sorted(nodes):
        if child == "/":
            continue
        if str(PurePosixPath(child).parent) == path:
            suffix = "/" if nodes[child] is None else ""
            print(PurePosixPath(child).name + suffix)


def command_cd(args, state):
    """Меняет текущую виртуальную папку."""
    if len(args) > 1:
        raise ValueError("cd принимает не более одного пути")

    path = resolve_path(state, args[0] if args else "/")
    if state["nodes"][path] is not None:
        raise ValueError(f"Не является папкой: {path}")
    state["cwd"] = path


def command_history(args, state):
    """Выводит непустые команды текущего сеанса."""
    if args:
        raise ValueError("history не принимает аргументы")

    for number, line in enumerate(state["history"], start=1):
        print(f"{number}  {line}")


def subtree_size(nodes, path):
    """Считает объём содержимого файлов в байтах."""
    if nodes[path] is not None:
        return len(nodes[path])

    prefix = path.rstrip("/") + "/"
    total = 0
    for child, data in nodes.items():
        if child.startswith(prefix) and data is not None:
            total += len(data)
    return total


def command_du(args, state):
    """Выводит объём каждой вложенной папки и выбранного пути."""
    if len(args) > 1:
        raise ValueError("du принимает не более одного пути")

    path = resolve_path(state, args[0] if args else ".")
    nodes = state["nodes"]
    prefix = path.rstrip("/") + "/"
    for child in sorted(nodes):
        if child != path and child.startswith(prefix):
            if nodes[child] is None:
                print(f"{subtree_size(nodes, child)}\t{child}")

    print(f"{subtree_size(nodes, path)}\t{path}")