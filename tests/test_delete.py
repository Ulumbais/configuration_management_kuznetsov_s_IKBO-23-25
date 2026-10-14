import tempfile
import unittest
from pathlib import Path

from src.commands import command_rm, command_rmdir
from src.vfs import load_vfs


class DeleteTests(unittest.TestCase):
    """Проверяет удаление и сохранность исходного CSV."""

    def setUp(self):
        """Загружает независимую VFS перед каждым тестом."""
        self.state = {
            "nodes": load_vfs("examples/deep.csv"),
            "cwd": "/",
            "history": [],
        }

    def test_rm_file(self):
        """Файл удаляется из словаря."""
        path = "/docs/course/python/readme.txt"
        command_rm([path], self.state)
        self.assertNotIn(path, self.state["nodes"])

    def test_rm_directory_rejected(self):
        """rm не удаляет папки."""
        with self.assertRaises(ValueError):
            command_rm(["/docs"], self.state)
        self.assertIn("/docs", self.state["nodes"])

    def test_rmdir_empty(self):
        """Пустая папка удаляется."""
        command_rmdir(["/empty"], self.state)
        self.assertNotIn("/empty", self.state["nodes"])

    def test_rmdir_nonempty_rejected(self):
        """Непустая папка сохраняется."""
        with self.assertRaises(ValueError):
            command_rmdir(["/docs"], self.state)
        self.assertIn("/docs", self.state["nodes"])

    def test_root_and_current_rejected(self):
        """Корень и текущая папка защищены от удаления."""
        with self.assertRaises(ValueError):
            command_rmdir(["/"], self.state)
        self.state["cwd"] = "/empty"
        with self.assertRaises(ValueError):
            command_rmdir(["."], self.state)

    def test_csv_unchanged(self):
        """Удаления в памяти не изменяют физический CSV."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vfs.csv"
            original = Path("examples/deep.csv").read_bytes()
            path.write_bytes(original)
            self.state["nodes"] = load_vfs(path)
            command_rm(
                ["/docs/course/python/readme.txt"], self.state
            )
            command_rmdir(["/empty"], self.state)
            self.assertEqual(path.read_bytes(), original)
            restored = load_vfs(path)
            self.assertIn("/empty", restored)
            self.assertIn("/docs/course/python/readme.txt", restored)


if __name__ == "__main__":
    unittest.main()