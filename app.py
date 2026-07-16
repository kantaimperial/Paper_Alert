"""Streamlit setup app: fill in the form once, get scheduled paper alerts."""

import subprocess
from datetime import date, time, timedelta

import streamlit as st
from dotenv import dotenv_values

from setup import DEFAULT_FLAGSHIP_JOURNALS
from src import scheduler
from src.config import GEMINI_MODEL_DEFAULT
from src.env_file import ENV_FILE, save_env
from src.profile import PROFILE_FILE, Profile, load_profile, save_profile
from src.scheduler import WEEKDAY_LABELS, WEEKDAY_ORDER

PRESET_FLAGSHIP_JOURNALS = DEFAULT_FLAGSHIP_JOURNALS

PRESET_PRIORITY_JOURNALS = [
    # ACS
    "Journal of the American Chemical Society",
    "ACS Nano",
    "Chemistry of Materials",
    "ACS Energy Letters",
    "ACS Applied Materials & Interfaces",
    "Inorganic Chemistry",
    # RSC
    "Chemical Science",
    "Chemical Communications",
    "Journal of Materials Chemistry A",
    "Journal of Materials Chemistry C",
    "Dalton Transactions",
    # Wiley
    "Angewandte Chemie International Edition",
    "Advanced Materials",
    "Advanced Functional Materials",
    "Advanced Energy Materials",
    "Small",
    # Cell Press
    "Cell",
    "Chem",
    "Joule",
    "Matter",
    # APS (physics)
    "Physical Review Letters",
    "Physical Review B",
    "Physical Review X",
    "Physical Review Materials",
    "Physical Review Applied",
]

LANGUAGE_OPTIONS = {"日本語": "ja", "English": "en"}
WEEKDAY_LABEL_TO_NUM = {v: k for k, v in WEEKDAY_LABELS.items()}


def _split(raw: str) -> list:
    return [item.strip() for item in raw.replace("\n", ",").split(",") if item.strip()]


def _describe_schedule(frequency: str, hour: int, minute: int, weekdays: list) -> str:
    time_str = f"{hour:02d}:{minute:02d}"
    if frequency == "daily":
        return f"毎日 {time_str}"
    days = "・".join(WEEKDAY_LABELS[wd] for wd in WEEKDAY_ORDER if wd in weekdays)
    return f"毎週{days}曜日 {time_str}"


st.set_page_config(page_title="paper-alert 設定", page_icon="📄")
st.title("📄 paper-alert 設定")
st.write("必要事項を入力して保存すると、選んだ頻度で新着論文のアラートメールが自動的に届くようになります。")

existing_profile = load_profile() if PROFILE_FILE.exists() else Profile(recipient_email="")
existing_env = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
existing_priority = existing_profile.priority_journals
existing_other_journals = [j for j in existing_priority if j not in PRESET_PRIORITY_JOURNALS]
existing_schedule = scheduler.current_schedule()

st.subheader("1. Gemini APIキー")
st.caption("無料枠あり・クレジットカード不要: https://aistudio.google.com/apikey")
gemini_api_key = st.text_input(
    "Gemini APIキー", value=existing_env.get("GEMINI_API_KEY", ""), type="password"
)

st.subheader("2. メールアドレス")
st.caption("論文アラートの送信元 兼 受信先として使うGmailアドレスです。")
gmail_address = st.text_input("Gmailアドレス", value=existing_env.get("GMAIL_ADDRESS", ""))
st.caption("アプリパスワードの発行 (2段階認証が必要): https://myaccount.google.com/apppasswords")
gmail_app_password = st.text_input(
    "Gmailアプリパスワード", value=existing_env.get("GMAIL_APP_PASSWORD", ""), type="password"
)

st.subheader("3. キーワード")
st.caption("英語で入力してください。カンマまたは改行区切りで複数指定できます。例: perovskite, charge transport")
keywords_raw = st.text_area("キーワード", value=", ".join(existing_profile.keywords))

st.subheader("4. 優先するジャーナル")

st.caption("Nature/Science系（広めの一致条件を適用）")
selected_flagship = st.multiselect(
    "Nature/Science系",
    options=PRESET_FLAGSHIP_JOURNALS,
    default=[
        j
        for j in (existing_profile.flagship_journals or PRESET_FLAGSHIP_JOURNALS)
        if j in PRESET_FLAGSHIP_JOURNALS
    ],
    label_visibility="collapsed",
)

st.caption("有名どころ（ACS・RSC・Cell・Wiley・物理系など）")
selected_priority = st.multiselect(
    "有名どころ",
    options=PRESET_PRIORITY_JOURNALS,
    default=[j for j in existing_priority if j in PRESET_PRIORITY_JOURNALS],
    label_visibility="collapsed",
)

st.caption("その他（カンマ区切りで追加）")
other_journals_raw = st.text_input(
    "その他", value=", ".join(existing_other_journals), label_visibility="collapsed"
)

st.caption("プレプリントサーバーも検索対象に含めるか（任意）。")
include_arxiv = st.checkbox("arXivも検索対象に含める", value=existing_profile.include_arxiv)
include_chemrxiv = st.checkbox("ChemRxivも検索対象に含める", value=existing_profile.include_chemrxiv)

st.caption(
    "論文は「掲載誌の格（Nature/Science系 > 分野トップ誌 > プレプリント）→ キーワード一致数」の"
    "順に並び、メールに載せる件数には上限を設定できます。arXiv/ChemRxivはジャーナルより件数が"
    "膨らみやすいので、個別にも上限をかけられます。"
)
max_total_papers = st.number_input(
    "メール1通に載せる論文数の上限（全体）", min_value=1, max_value=200,
    value=existing_profile.max_total_papers,
)
col_arxiv_cap, col_chemrxiv_cap = st.columns(2)
with col_arxiv_cap:
    max_arxiv_papers = st.number_input(
        "うちarXivの上限", min_value=1, max_value=200,
        value=existing_profile.max_arxiv_papers, disabled=not include_arxiv,
    )
with col_chemrxiv_cap:
    max_chemrxiv_papers = st.number_input(
        "うちChemRxivの上限", min_value=1, max_value=200,
        value=existing_profile.max_chemrxiv_papers, disabled=not include_chemrxiv,
    )

st.subheader("5. 配信頻度")
default_frequency = existing_schedule["frequency"] if existing_schedule else "daily"
default_hour = existing_schedule["hour"] if existing_schedule else 9
default_minute = existing_schedule["minute"] if existing_schedule else 0
default_weekdays = existing_schedule["weekdays"] if existing_schedule else [1]

frequency_mode_label = st.radio(
    "頻度",
    options=["毎日", "毎週"],
    index=0 if default_frequency == "daily" else 1,
    horizontal=True,
)
frequency = "daily" if frequency_mode_label == "毎日" else "weekly"

selected_weekday_labels = []
if frequency == "weekly":
    default_weekday_labels = [WEEKDAY_LABELS[wd] for wd in default_weekdays if wd in WEEKDAY_LABELS]
    selected_weekday_labels = st.multiselect(
        "曜日（複数選択可）",
        options=[WEEKDAY_LABELS[wd] for wd in WEEKDAY_ORDER],
        default=default_weekday_labels or ["月"],
    )

alert_time = st.time_input("配信時刻", value=time(default_hour, default_minute))

st.subheader("6. 要約の言語")
language_label = st.selectbox(
    "論文要約の言語",
    options=list(LANGUAGE_OPTIONS.keys()),
    index=list(LANGUAGE_OPTIONS.values()).index(existing_profile.summary_language)
    if existing_profile.summary_language in LANGUAGE_OPTIONS.values()
    else 0,
)

with st.expander("詳細設定（上級者向け）"):
    st.caption("Nature/Science系の雑誌だけに使う、より広い一致条件（任意）。")
    broad_terms_raw = st.text_area("広い一致条件", value=", ".join(existing_profile.broad_terms))

submitted = st.button("保存して自動実行を設定", type="primary")

if submitted:
    keywords = _split(keywords_raw)
    priority_journals = selected_priority + _split(other_journals_raw)
    language = LANGUAGE_OPTIONS[language_label]
    weekdays = [WEEKDAY_LABEL_TO_NUM[label] for label in selected_weekday_labels]

    errors = []
    if not gemini_api_key:
        errors.append("Gemini APIキーを入力してください。")
    if not gmail_address or "@" not in gmail_address:
        errors.append("Gmailアドレスを正しく入力してください。")
    if not gmail_app_password:
        errors.append("Gmailアプリパスワードを入力してください。")
    if not keywords:
        errors.append("キーワードを1つ以上入力してください。")
    if not selected_flagship and not priority_journals:
        errors.append("ジャーナルを1つ以上選択してください。")
    if frequency == "weekly" and not weekdays:
        errors.append("曜日を1つ以上選択してください。")

    if errors:
        for error in errors:
            st.error(error)
    else:
        save_env(
            gemini_api_key,
            gmail_address,
            gmail_app_password,
            existing_env.get("GEMINI_MODEL", GEMINI_MODEL_DEFAULT),
        )
        profile = Profile(
            recipient_email=gmail_address,
            keywords=keywords,
            broad_terms=_split(broad_terms_raw),
            flagship_journals=selected_flagship,
            priority_journals=priority_journals,
            summary_language=language,
            include_arxiv=include_arxiv,
            include_chemrxiv=include_chemrxiv,
            max_total_papers=int(max_total_papers),
            max_arxiv_papers=int(max_arxiv_papers),
            max_chemrxiv_papers=int(max_chemrxiv_papers),
        )
        save_profile(profile)
        try:
            scheduler.install_schedule(frequency, alert_time.hour, alert_time.minute, weekdays)
            schedule_desc = _describe_schedule(frequency, alert_time.hour, alert_time.minute, weekdays)
            st.success(
                f"設定を保存し、「{schedule_desc}」に自動実行するよう登録しました。"
                "以後は放っておいても論文アラートが届きます。"
            )
        except subprocess.CalledProcessError as exc:
            st.error(f"自動実行の登録に失敗しました: {exc}")

st.divider()

if existing_schedule:
    desc = _describe_schedule(
        existing_schedule["frequency"], existing_schedule["hour"], existing_schedule["minute"], existing_schedule["weekdays"]
    )
    st.success(f"✅ 自動実行が設定されています（{desc}）。")
    if st.button("自動実行を停止する"):
        scheduler.uninstall_schedule()
        st.rerun()
else:
    st.info("まだ自動実行は設定されていません。上のフォームから保存してください。")

st.subheader("テスト実行")
st.caption("現在保存されている設定で今すぐ1回実行し、動作を確認します(該当論文があれば実際にメールが送信されます)。")

override_period = st.checkbox("検索期間を指定してテストする（前回チェック日時は使わない）")
lookback_days = None
if override_period:
    lookback_days = st.number_input("何日前から検索するか", min_value=1, max_value=365, value=7)
    st.caption(
        "この場合、実行結果は次回の自動実行に影響しません（state/last_run.jsonは更新されません）。"
    )

if st.button("今すぐ実行してテスト"):
    if not PROFILE_FILE.exists() or not ENV_FILE.exists():
        st.error("先にフォームを保存してください。")
    else:
        cmd = [scheduler.python_executable(), "main.py"]
        if lookback_days is not None:
            since = (date.today() - timedelta(days=int(lookback_days))).isoformat()
            cmd += ["--since", since, "--no-save-state"]
        with st.spinner("実行中..."):
            result = subprocess.run(
                cmd,
                cwd=scheduler.ROOT_DIR,
                capture_output=True,
                text=True,
            )
        if result.returncode == 0:
            st.success("実行が完了しました。")
        else:
            st.error("実行中にエラーが発生しました。")
        st.code(result.stdout + result.stderr or "(出力なし)")
