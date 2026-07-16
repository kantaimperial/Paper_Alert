@echo off
rem Sets up the venv/dependencies (first run only) and launches the Streamlit
rem app in the browser. Meant to be started via the launcher .vbs file next
rem to it, but can also be double-clicked or run from a command prompt.
rem (Kept ASCII-only: the legacy script/console codepage can mis-parse
rem non-ASCII text and break string literals depending on the system.)
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Please install Python 3 first, then open this app again.' + [Environment]::NewLine + [Environment]::NewLine + 'Download it from https://www.python.org/downloads/ - check Add python.exe to PATH during setup.','Python not found') | Out-Null"
    exit /b 1
)

rem Streamlit's own first-run prompt ("enter your email...") reads from
rem stdin and would otherwise hang forever when launched with no console.
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    (
        echo [general]
        echo email = ""
    ) > "%USERPROFILE%\.streamlit\credentials.toml"
)

if not exist venv (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

streamlit run app.py
