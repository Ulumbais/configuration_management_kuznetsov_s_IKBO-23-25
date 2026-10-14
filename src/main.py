import csv
import getpass
from datetime import datetime
"""Добавляем библиотеки для работы с файлами"""
from pathlib import Path
import argparse
from src.vfs import load_vfs, reset_vfs

from src.commands import (
    command_cd,
    command_du,
    command_history,
    command_ls,
)

COMMANDS = {
    "ls": command_ls,
    "cd": command_cd,
    "history": command_history,
    "du": command_du,
}

def parse_command(text):
    """Разделяет строчку на команду и список аргументов"""
    text = text.split()
    if len(text) == 0:
        return None, []
    else:
        return text[0], text[1:]

def parse_args():
    """Получает настройки эмулятора из командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки UNIX"
    )
    parser.add_argument(
        "--vfs",
        default="vfs.csv",
        help="Путь к CSV-файлу виртуальной файловой системы",
    )
    parser.add_argument(
        "--log",
        default="commands.csv",
        help="Путь к CSV-файлу журнала команд",
    )
    parser.add_argument(
        "--script",
        help="Путь к стартовому скрипту",
    )
    return parser.parse_args()


def log_command(log_path, line):
    """Добавляет событие вызова команды в CSV-файл."""
    path = Path(log_path)
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["user", "datetime", "command"])
        writer.writerow([
            getpass.getuser(),
            datetime.now().isoformat(timespec="seconds"),
            line,
        ])

def execute_command(line, log_path, state):
    """Выполняет команду и сообщает, нужно ли продолжать работу."""
    cmd, arg = parse_command(line)
    if cmd is None:
        return True

    state["history"].append(line)
    log_command(log_path, line)

    try:
        if cmd == "exit":
            if arg:
                raise ValueError("exit не принимает аргументы")
            return False

        if cmd == "vfs-init":
            if arg:
                raise ValueError("vfs-init не принимает аргументы")
            nodes = reset_vfs(state["vfs_path"])
            state["nodes"] = nodes
            state["cwd"] = "/"
            print("VFS сброшена: осталась корневая папка")
        elif cmd in COMMANDS:
            COMMANDS[cmd](arg, state)
        else:
            raise ValueError(f"Неизвестная команда: {cmd}")
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}")

    return True

def run_script(script_path, vfs_name, log_path, state):
    """Выполняет стартовый скрипт, отображая команды и результаты."""
    try:
        with Path(script_path).open(
            "r", encoding="utf-8-sig"
        ) as file:
            for line in file:
                line = line.strip()
                print(f"{vfs_name}:/> {line}")
                if not execute_command(line, log_path, state):
                    return False
    except OSError as error:
        print(f"Ошибка чтения скрипта: {error}")

    return True

def main():
    """Загружает VFS, запускает скрипт и интерактивный диалог."""
    args = parse_args()
    vfs_name = Path(args.vfs).stem

    print(f"VFS: {args.vfs}")
    print(f"Лог: {args.log}")
    print(f"Стартовый скрипт: {args.script}")

    try:
        nodes = load_vfs(args.vfs)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Ошибка загрузки VFS: {error}")
        return

    state = {
        "vfs_path": args.vfs,
        "nodes": nodes,
        "cwd": "/",
        "history": [],
    }
    print(f"Загружено элементов VFS: {len(nodes)}")

    if args.script:
        if not run_script(args.script, vfs_name, args.log, state):
            return

    while True:
        try:
            line = input(f"{vfs_name}:{state['cwd']}> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not execute_command(line, args.log, state):
            break

            
if __name__ == "__main__":
    main()