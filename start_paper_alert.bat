@echo off
rem Sets up the venv/dependencies (first run only) and launches the Streamlit
rem app in the browser. Meant to be started via "paper-alertを起動.vbs",
rem but can also be double-clicked or run directly from a command prompt.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('先にPython 3をインストールしてから、もう一度このアプリを開いてください。' + [Environment]::NewLine + [Environment]::NewLine + 'https://www.python.org/downloads/ からダウンロードできます。インストール時は「Add python.exe to PATH」にチェックを入れてください。','Pythonが見つかりません') | Out-Null"
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
