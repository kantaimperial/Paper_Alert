#!/bin/bash
# Sets up the venv/dependencies (first run only) and launches the Streamlit
# app in the browser. Meant to be double-clicked via "paper-alertを起動.app",
# but can also be run directly from a terminal.
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    osascript -e 'display alert "Pythonが見つかりません" message "先にPython 3をインストールしてから、もう一度このアプリをダブルクリックしてください。\n\nhttps://www.python.org/downloads/ からダウンロードできます。" buttons {"OK"} default button "OK"'
    exit 1
fi

# Streamlit's own first-run prompt ("enter your email...") reads from stdin
# and would otherwise hang forever when launched with no terminal attached.
mkdir -p "$HOME/.streamlit"
if [ ! -f "$HOME/.streamlit/credentials.toml" ]; then
    printf '[general]\nemail = ""\n' > "$HOME/.streamlit/credentials.toml"
fi

FIRST_RUN=0
if [ ! -d venv ]; then
    FIRST_RUN=1
    osascript -e 'display notification "初回セットアップ中です。数分かかることがあります…" with title "paper-alert"'
    python3 -m venv venv
fi

source venv/bin/activate

if [ "$FIRST_RUN" = "1" ]; then
    pip install -q -r requirements.txt
fi

osascript -e 'display notification "ブラウザで設定画面を開きます…" with title "paper-alert"'
streamlit run app.py
