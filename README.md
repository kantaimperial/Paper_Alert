# paper-alert

指定したキーワード・雑誌に該当する新着論文を自動検索し、要約つきでメール通知するツールです。
要約はGemini API（無料枠あり）で行います。

## 配布された方へ（ターミナル操作不要）

このフォルダをGitHubの「Code → Download ZIP」で受け取った場合は、以下の手順だけで使えます。
**事前にPython 3が必要です。** 入っていない場合は起動時にダイアログで案内されるので、
https://www.python.org/downloads/ からインストールしてから、もう一度アプリを開いてください
（Windowsの場合、インストール時に「Add python.exe to PATH」へのチェックを忘れずに）。

### Macの場合

1. ダウンロードしたZIPを展開し、**「paper-alert」フォルダごと**、書類フォルダやデスクトップなど
   分かりやすい場所に移動する
   - ダウンロードフォルダに置きっぱなしにしない（あとで整理して消してしまいがちなため）
   - `paper-alertを起動.app`は同じフォルダ内の他のファイルに依存しているので、**アプリ単体だけを
     `Applications`などに移動しない**こと（壊れます）。`Applications`に置きたい場合も
     `~/Applications/paper-alert/`のようにフォルダごと移してください
2. フォルダの中にある **「paper-alertを起動.app」をダブルクリック** する
3. 初回は「"paper-alertを起動"は開いていません」という警告が出ます。これは署名なしアプリを
   初めて開くときに必ず出るもので、**最初の1回だけ**対応すれば十分です。
   1. 警告ダイアログの「完了」を押して閉じる
   2. **システム設定 →「プライバシーとセキュリティ」** を開く
   3. 下の方にある **「このまま開く」** を押す
   4. もう一度「paper-alertを起動.app」をダブルクリックし、確認ダイアログで「開く」を押す
4. 初回はセットアップに数分かかります。終わるとブラウザが自動で開きます
5. 開いた画面の案内に沿って、Gemini APIキーやメールアドレスなどを入力してください

2回目以降は「paper-alertを起動.app」をダブルクリックするだけで開きます（警告も出ません）。

### Windowsの場合

1. ダウンロードしたZIPを展開し、**「paper-alert」フォルダごと**分かりやすい場所に移動する
   - `paper-alertを起動.vbs`は同じフォルダ内の他のファイルに依存しているので、**ファイル単体だけを
     他の場所に移動・コピーしない**こと（壊れます）
2. フォルダの中にある **「paper-alertを起動.vbs」をダブルクリック** する
   - 初回はWindowsが「発行元を確認できません」といった警告を出すことがあります。「詳細情報」→
     「実行」を選べば起動できます
3. 初回はセットアップに数分かかります。終わるとブラウザが自動で開きます
4. 開いた画面の案内に沿って、Gemini APIキーやメールアドレスなどを入力してください

自動実行にはWindowsの「タスクスケジューラ」を使います。管理者権限は不要です。

## セットアップ（GUI・推奨、ターミナルを使う場合）

### 1. 依存関係のインストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. アプリを起動

```bash
streamlit run app.py
```

ブラウザが自動で開きます。以下を入力して「保存して自動実行を設定」を押すだけで設定完了です。

- Gemini APIキー（https://aistudio.google.com/apikey で無料発行）
- Gmailアドレス・アプリパスワード（送信元 兼 受信先。アプリパスワードは https://myaccount.google.com/apppasswords で発行、2段階認証が必要）
- キーワード（英語）
- 優先するジャーナル（プリセットから選択 + その他を自由入力）
- arXiv / ChemRxivを検索対象に含めるか、含める場合の件数上限
- 配信頻度（毎日、または毎週の曜日を複数選択）と時刻
- 論文要約の言語（日本語 / English）

保存すると `profile.yaml` と `.env` が生成され、選んだ頻度で自動実行が登録されます（Macは`launchd`、Windowsはタスクスケジューラ）。以後は放っておいても新着論文があればメールが届きます。画面下部の「今すぐ実行してテスト」で即座に動作確認もできます。設定をやめたい場合は「自動実行を停止する」で登録解除できます。

## セットアップ（CLI・上級者向け）

GUIを使わない場合は、従来通りCLIでも設定できます。

```bash
python setup.py           # 対話式ウィザード -> profile.yaml を生成
cp .env.example .env       # GEMINI_API_KEY / GMAIL_ADDRESS / GMAIL_APP_PASSWORD を記入
python main.py             # 実行
```

`profile.yaml` はあとから直接編集しても構いません（`profile.example.yaml` が書式の参考になります）。定期実行を自分で登録したい場合は `src/scheduler_macos.py`（launchd）・`src/scheduler_windows.py`（タスクスケジューラ）の `install_schedule()` を参考にしてください。`src/scheduler.py` がOSを見てどちらを使うか自動で切り替えます。

初回実行は7日分さかのぼって検索し、該当論文があればメール送信します。実行日時は `state/last_run.json` に記録され、次回はそこから検索します。

## 仕組み

- **検索対象**: `profile.yaml` の `flagship_journals`（Nature/Science系、広めのマッチ）と `priority_journals`（分野別トップ誌、キーワード一致）
- **検索元**: Crossref API
- **要約**: Gemini API（既定`gemini-3.1-flash-lite`、`.env`の`GEMINI_MODEL`で変更可）で要約を生成（言語は日本語/Englishから選択可）
- **通知**: Gmail経由でメール送信（DOIリンク付き）
