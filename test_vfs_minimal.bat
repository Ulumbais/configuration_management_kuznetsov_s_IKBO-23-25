@echo off
cd /d "%~dp0"
copy /Y examples\minimal.csv working_vfs.csv >nul
python -m src.main --vfs working_vfs.csv --log events.csv --script examples/stage3.txt