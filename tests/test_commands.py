import io
import unittest
from contextlib import redirect_stdout

from src.commands import (
    command_cd,
    command_history,
    command_ls,
    resolve_path,
    subtree_size,
)
from src.vfs import load_vfs


class CommandTests(unittest.TestCase):
    """Проверяет пути, команды и подсчёт объёма VFS."""

    def setUp(self):
        """Создаёт независимое состояние перед каждым тестом."""
        self.state = {
            "nodes": load_vfs("examples/deep.csv"),
            "cwd": "/",
            "history": [],
        }

    def test_relative_paths(self):
        """Переходы учитывают текущую папку и родителя."""
        command_cd(["docs/course/python"], self.state)
        self.assertEqual(self.state["cwd"], "/docs/course/python")
        self.assertEqual(resolve_path(self.state, ".."), "/docs/course")
        command_cd([], self.state)
        self.assertEqual(self.state["cwd"], "/")
        self.assertEqual(resolve_path(self.state, ".."), "/")

    def test_cd_file_keeps_directory(self):
        """Ошибка перехода в файл не меняет текущую папку."""
        with self.assertRaises(ValueError):
            command_cd(["/docs/course/python/readme.txt"], self.state)
        self.assertEqual(self.state["cwd"], "/")

    def test_file_cannot_be_parent(self):
        """Нельзя пройти через файл даже с последующим .. ."""
        path = "/docs/course/python/readme.txt/.."
        with self.assertRaises(ValueError):
            resolve_path(self.state, path)

    def test_ls_direct_children(self):
        """ls выводит только непосредственное содержимое."""
        output = io.StringIO()
        with redirect_stdout(output):
            command_ls([], self.state)
        self.assertEqual(output.getvalue(), "docs/\nempty/\n")

    def test_sizes(self):
        """Размер папки включает файлы всех уровней."""
        nodes = self.state["nodes"]
        self.assertEqual(subtree_size(nodes, "/"), 5)
        self.assertEqual(subtree_size(nodes, "/docs"), 5)
        self.assertEqual(subtree_size(nodes, "/empty"), 0)
        path = "/docs/course/python/readme.txt"
        self.assertEqual(subtree_size(nodes, path), 5)

    def test_history(self):
        """История выводится с номерами."""
        self.state["history"] = ["ls", "unknown", "history"]
        output = io.StringIO()
        with redirect_stdout(output):
            command_history([], self.state)
        expected = "1  ls\n2  unknown\n3  history\n"
        self.assertEqual(output.getvalue(), expected)


if __name__ == "__main__":
    unittest.main()