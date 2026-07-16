# paper-alert

指定したキーワード・雑誌に該当する新着論文を自動検索し、日本語要約つきでメール通知するツールです。
要約はGemini API（無料枠あり）で行います。

## セットアップ

### 1. 依存関係のインストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Gemini APIキーの取得

https://aistudio.google.com/apikey でAPIキーを発行してください（無料枠あり、クレジットカード不要）。

### 3. プロファイルの作成

対話式ウィザードで、キーワード・重視する雑誌・メールアドレスを設定します。

```bash
python setup.py
```

`profile.yaml` が生成されます。あとから直接編集しても構いません（`profile.example.yaml` が書式の参考になります）。

### 4. `.env` の設定

`.env.example` を `.env` にコピーし、`GEMINI_API_KEY` と `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` を設定してください。

- `GMAIL_APP_PASSWORD` は https://myaccount.google.com/apppasswords で発行（2段階認証が必要）

```bash
cp .env.example .env
```

### 5. 実行

```bash
python main.py
```

初回は7日分さかのぼって検索し、該当論文があればメール送信します。実行日時は `state/last_run.json` に記録され、次回はそこから検索します。

## 定期実行（任意）

macOSの `launchd` で定期実行できます。設定例やスリープ対策（`pmset repeat wake`）については個別に相談してください。

## 仕組み

- **検索対象**: `profile.yaml` の `flagship_journals`（Nature/Science系、広めのマッチ）と `priority_journals`（分野別トップ誌、キーワード一致）
- **検索元**: Crossref API
- **要約**: Gemini API（`gemini-3.5-flash`）で日本語要約を生成
- **通知**: Gmail経由でメール送信（DOIリンク付き）
