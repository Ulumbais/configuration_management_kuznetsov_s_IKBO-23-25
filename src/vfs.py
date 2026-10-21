import base64
import csv
from pathlib import Path, PurePosixPath


def validate_tree(nodes):
    """Проверяет наличие корня и родительских папок."""
    if "/" not in nodes or nodes["/"] is not None:
        raise ValueError("Корень VFS должен быть папкой")

    for path in nodes:
        if path == "/":
            continue

        parent = str(PurePosixPath(path).parent)
        if parent not in nodes or nodes[parent] is not None:
            raise ValueError(f"Нет родительской папки: {parent}")


def validate_path(path, nodes):
    """Проверяет формат и уникальность виртуального пути."""
    if not path or not path.startswith("/"):
        raise ValueError("Путь должен начинаться с /")

    parts = path.split("/")
    if ".." in parts or "." in parts:
        raise ValueError("В CSV запрещены части . и ..")

    if str(PurePosixPath(path)) != path:
        raise ValueError(f"Некорректный путь: {path}")

    if path in nodes:
        raise ValueError(f"Повтор пути: {path}")


def decode_node(row):
    """Возвращает None для папки или байты для файла."""
    if row["type"] == "dir":
        if row["data"]:
            raise ValueError("У папки не должно быть данных")
        return None

    if row["type"] == "file":
        return base64.b64decode(row["data"], validate=True)

    raise ValueError(f"Неизвестный тип: {row['type']}")


def load_vfs(vfs_path):
    """Загружает папки и файлы из CSV в память."""
    nodes = {}

    with Path(vfs_path).open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["path", "type", "data"]:
            raise ValueError("Ожидаются столбцы path,type,data")

        for row in reader:
            if None in row or None in row.values():
                raise ValueError(
                    "Каждая строка CSV должна содержать три поля"
                )

            path = row["path"]
            validate_path(path, nodes)
            nodes[path] = decode_node(row)

    validate_tree(nodes)
    return nodes


def reset_vfs(vfs_path):
    """Записывает пустую VFS на диск и возвращает её в памяти."""
    with Path(vfs_path).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["path", "type", "data"])
        writer.writerow(["/", "dir", ""])

    return {"/": None}