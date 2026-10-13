@echo off
cd /d "%~dp0"
python src/main.py --vfs demo.csv --log events.csv --script startup.txt