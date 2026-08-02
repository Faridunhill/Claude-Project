@echo off
REM Windows launcher — run the Monster from any folder, no PYTHONPATH needed.
REM   C:\path\to\marketing_monster\monster.cmd locate C:\Users\hadid
REM Ledgers are created in the folder you are standing in, so cd to your
REM marketing folder first (e.g. %USERPROFILE%\FARIDOS\marketing).
setlocal
set "MONSTER_HOME=%~dp0"
if defined PYTHONPATH (
  set "PYTHONPATH=%MONSTER_HOME%;%PYTHONPATH%"
) else (
  set "PYTHONPATH=%MONSTER_HOME%"
)
python -m monster %*
exit /b %ERRORLEVEL%
