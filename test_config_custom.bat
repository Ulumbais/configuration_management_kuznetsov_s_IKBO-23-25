@echo off
cd /d "%~dp0"
python -m src.main --vfs examples/deep.csv --log events.csv --script startup.txt