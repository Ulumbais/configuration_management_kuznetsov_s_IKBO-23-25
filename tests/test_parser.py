from src.main import parse_command
assert parse_command('cd docs') == ('cd', ['docs']); print('OK')
assert parse_command('ls docs') == ('ls', ['docs']); print('OK')
assert parse_command('') == (None, []); print('OK')
print("Все проверки пройдены")