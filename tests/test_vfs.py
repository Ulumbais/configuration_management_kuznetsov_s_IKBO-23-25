import tempfile
import unittest
from pathlib import Path

from src.vfs import load_vfs, reset_vfs


class VfsTests(unittest.TestCase):
    """Проверяет загрузку и сброс виртуальной файловой системы."""

    def test_files(self):
        """Пустой файл отличается от папки, Base64 декодируется."""
        nodes = load_vfs("examples/files.csv")
        self.assertIsNone(nodes["/"])
        self.assertEqual(nodes["/hello.txt"], b"Hello")
        self.assertEqual(nodes["/empty.txt"], b"")
        self.assertEqual(nodes["/binary.bin"], bytes([0, 1, 2]))

    def test_deep_tree(self):
        """Файл загружается из трёх вложенных папок."""
        nodes = load_vfs("examples/deep.csv")
        path = "/docs/course/python/readme.txt"
        self.assertEqual(nodes[path], b"Hello")

    def test_missing_parent(self):
        """Файл без родительской папки отклоняется."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.csv"
            path.write_text(
                "path,type,data\n"
                "/,dir,\n"
                "/missing/file.txt,file,\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_vfs(path)

    def test_reset(self):
        """Сброс очищает память и физическое представление."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vfs.csv"
            path.write_bytes(Path("examples/files.csv").read_bytes())
            self.assertEqual(reset_vfs(path), {"/": None})
            self.assertEqual(load_vfs(path), {"/": None})


if __name__ == "__main__":
    unittest.main()