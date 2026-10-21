MAX_COMMANDS_ARGS = 1

def parse_command(text):
    """Разделяет строчку на команду и список аргументов"""
    text = text.split()
    if len(text) == 0:
        return None, []
    else:
        return text[0], text[1:]


def main():
    """Запускает интерактивный диалог с пользователем"""
    vfs_name = "demo"
    while True:
        line = input(f"{vfs_name}:/> ")
        cmd, arg = parse_command(line)
        if cmd is None:
            continue
        if cmd == "exit": 
            if len(arg) > 0:
                print("Ошибка: exit не принимает аргументы")
            else:
                break
        elif cmd in ['ls', 'cd']:
            if len(arg) <= MAX_COMMANDS_ARGS:
                print(cmd, arg)
            else:
                print("Ошибка: слишком много аргументов")
        else:
            print("Ошибка: неизвестная команда")

            
if __name__ == "__main__":
    main()