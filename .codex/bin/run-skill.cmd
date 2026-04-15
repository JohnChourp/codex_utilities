@echo off
setlocal
if "%CODEX_HOME%"=="" for %%I in ("%~dp0..") do set "CODEX_HOME=%%~fI"
if "%PYTHON_BIN%"=="" set "PYTHON_BIN=py -3"
%PYTHON_BIN% "%CODEX_HOME%\skills\.system\skill-runtime-lib\scripts\run_skill.py" %*
