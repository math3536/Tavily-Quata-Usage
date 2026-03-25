from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
USAGE_FILE = DATA_DIR / "usage_history.csv"


TEXT = {
    "en": {
        "page_title": "Tavily Quota Monitor",
        "title": "Tavily Quota Monitor",
        "caption": "Track usage, remaining quota, and risk across multiple Tavily accounts or keys.",
        "language_label": "Language",
        "language_help": "Choose the interface language.",
        "no_accounts": "No `accounts.json` found. Add sample data or connect your real data source first.",
        "overview": "Account overview",
        "choose_account": "Choose an account",
        "details": "{name} details",
        "how_to_use": "How to use",
        "usage_step_1": "Put your account snapshot into `data/accounts.json`",
        "usage_step_2": "Write historical requests and cost into `data/usage_history.csv`",
        "usage_step_3": "Run `streamlit run app.py`",
        "usage_more": "If you want automatic collection, I can help add:",
        "usage_bullets": [
            "A scheduled pull script",
            "GitHub Actions sync",
            "Webhook alerts to Telegram, Feishu, or WeCom",
        ],
        "summary_accounts": "Accounts",
        "summary_daily_used": "Daily used",
        "summary_monthly_used": "Monthly used",
        "summary_at_risk": "At risk",
        "table_account": "Account",
        "table_tier": "Tier",
        "table_used_today": "Used Today",
        "table_daily_limit": "Daily Limit",
        "table_remaining_today": "Remaining Today",
        "table_used_month": "Used Month",
        "table_monthly_limit": "Monthly Limit",
        "table_remaining_month": "Remaining Month",
        "table_daily_pct": "Daily %",
        "table_monthly_pct": "Monthly %",
        "table_last_updated": "Last Updated",
        "metric_used_today": "Used today",
        "metric_remaining_today": "Remaining today",
        "metric_used_month": "Used month",
        "metric_remaining_month": "Remaining month",
        "daily_usage": "Daily usage {ratio:.0%}",
        "monthly_usage": "Monthly usage {ratio:.0%}",
        "no_history": "No history available for this account yet.",
        "requests_over_time": "Requests over time",
        "cost_over_time": "Cost over time",
        "quota_split": "Today quota split by account",
        "chart_date": "Date",
        "chart_requests": "Requests",
        "chart_cost": "Cost",
        "chart_used_today": "Used Today",
        "chart_remaining_today": "Remaining Today",
        "metrics_suffix": "Overview",
    },
    "zh": {
        "page_title": "Tavily 配额监控",
        "title": "Tavily 配额监控",
        "caption": "用于查看多个 Tavily 账号或密钥的使用情况、剩余额度和风险状态。",
        "language_label": "语言",
        "language_help": "选择界面语言。",
        "no_accounts": "没有找到 `accounts.json`。请先放入示例数据或接入你的真实数据源。",
        "overview": "账号总览",
        "choose_account": "选择账号",
        "details": "{name} 详情",
        "how_to_use": "使用说明",
        "usage_step_1": "把账号快照写入 `data/accounts.json`",
        "usage_step_2": "把历史请求和成本写入 `data/usage_history.csv`",
        "usage_step_3": "运行 `streamlit run app.py`",
        "usage_more": "如果你想自动采集，我可以继续帮你加：",
        "usage_bullets": [
            "定时拉取脚本",
            "GitHub Actions 定时同步",
            "推送告警到 Telegram、飞书或企业微信",
        ],
        "summary_accounts": "账号数",
        "summary_daily_used": "今日已用",
        "summary_monthly_used": "本月已用",
        "summary_at_risk": "风险账号",
        "table_account": "账号",
        "table_tier": "套餐",
        "table_used_today": "今日已用",
        "table_daily_limit": "日额度",
        "table_remaining_today": "今日剩余",
        "table_used_month": "本月已用",
        "table_monthly_limit": "月额度",
        "table_remaining_month": "本月剩余",
        "table_daily_pct": "今日占比",
        "table_monthly_pct": "本月占比",
        "table_last_updated": "更新时间",
        "metric_used_today": "今日已用",
        "metric_remaining_today": "今日剩余",
        "metric_used_month": "本月已用",
        "metric_remaining_month": "本月剩余",
        "daily_usage": "今日使用率 {ratio:.0%}",
        "monthly_usage": "本月使用率 {ratio:.0%}",
        "no_history": "当前账号还没有历史记录。",
        "requests_over_time": "请求趋势",
        "cost_over_time": "成本趋势",
        "quota_split": "按账号拆分的今日额度",
        "chart_date": "日期",
        "chart_requests": "请求数",
        "chart_cost": "成本",
        "chart_used_today": "今日已用",
        "chart_remaining_today": "今日剩余",
        "metrics_suffix": "概览",
    },
}


@dataclass
class AccountSnapshot:
    account_id: str
    name: str
    tier: str
    daily_limit: int
    monthly_limit: int
    used_today: int
    used_month: int
    last_updated: str

    @property
    def remaining_today(self) -> int:
        return max(self.daily_limit - self.used_today, 0)

    @property
    def remaining_month(self) -> int:
        return max(self.monthly_limit - self.used_month, 0)

    @property
    def daily_ratio(self) -> float:
        return self.used_today / self.daily_limit if self.daily_limit else 0.0

    @property
    def monthly_ratio(self) -> float:
        return self.used_month / self.monthly_limit if self.monthly_limit else 0.0


def t(lang: str, key: str, **kwargs: object) -> str:
    value = TEXT[lang][key]
    return value.format(**kwargs) if kwargs else value


def load_accounts() -> list[AccountSnapshot]:
    if not ACCOUNTS_FILE.exists():
        return []

    raw = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    accounts: list[AccountSnapshot] = []

    for item in raw:
        accounts.append(
            AccountSnapshot(
                account_id=str(item["account_id"]),
                name=str(item["name"]),
                tier=str(item.get("tier", "unknown")),
                daily_limit=int(item["daily_limit"]),
                monthly_limit=int(item["monthly_limit"]),
                used_today=int(item["used_today"]),
                used_month=int(item["used_month"]),
                last_updated=str(item.get("last_updated", "")),
            )
        )

    return accounts


def load_usage_history() -> pd.DataFrame:
    if not USAGE_FILE.exists():
        return pd.DataFrame(columns=["timestamp", "account_id", "account_name", "requests", "cost"])

    df = pd.read_csv(USAGE_FILE)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def render_summary_cards(accounts: list[AccountSnapshot], lang: str) -> None:
    total_daily_limit = sum(a.daily_limit for a in accounts)
    total_used_today = sum(a.used_today for a in accounts)
    total_monthly_limit = sum(a.monthly_limit for a in accounts)
    total_used_month = sum(a.used_month for a in accounts)

    cols = st.columns(4)
    metrics = [
        (t(lang, "summary_accounts"), len(accounts)),
        (t(lang, "summary_daily_used"), f"{total_used_today}/{total_daily_limit}"),
        (t(lang, "summary_monthly_used"), f"{total_used_month}/{total_monthly_limit}"),
        (t(lang, "summary_at_risk"), sum(1 for a in accounts if a.daily_ratio >= 0.8 or a.monthly_ratio >= 0.8)),
    ]

    for col, (label, value) in zip(cols, metrics, strict=True):
        col.metric(label, value)


def render_account_table(accounts: list[AccountSnapshot], lang: str) -> pd.DataFrame:
    rows = []
    for account in accounts:
        rows.append(
            {
                t(lang, "table_account"): account.name,
                t(lang, "table_tier"): account.tier,
                t(lang, "table_used_today"): account.used_today,
                t(lang, "table_daily_limit"): account.daily_limit,
                t(lang, "table_remaining_today"): account.remaining_today,
                t(lang, "table_used_month"): account.used_month,
                t(lang, "table_monthly_limit"): account.monthly_limit,
                t(lang, "table_remaining_month"): account.remaining_month,
                t(lang, "table_daily_pct"): round(account.daily_ratio * 100, 1),
                t(lang, "table_monthly_pct"): round(account.monthly_ratio * 100, 1),
                t(lang, "table_last_updated"): account.last_updated,
            }
        )

    table = pd.DataFrame(rows)
    st.dataframe(table, use_container_width=True, hide_index=True)
    return table


def render_account_details(account: AccountSnapshot, history: pd.DataFrame, lang: str) -> None:
    st.subheader(t(lang, "details", name=account.name))

    cols = st.columns(4)
    cols[0].metric(t(lang, "metric_used_today"), f"{account.used_today}/{account.daily_limit}")
    cols[1].metric(t(lang, "metric_remaining_today"), account.remaining_today)
    cols[2].metric(t(lang, "metric_used_month"), f"{account.used_month}/{account.monthly_limit}")
    cols[3].metric(t(lang, "metric_remaining_month"), account.remaining_month)

    progress_cols = st.columns(2)
    progress_cols[0].progress(min(account.daily_ratio, 1.0), text=t(lang, "daily_usage", ratio=account.daily_ratio))
    progress_cols[1].progress(min(account.monthly_ratio, 1.0), text=t(lang, "monthly_usage", ratio=account.monthly_ratio))

    account_history = history[history["account_id"] == account.account_id].copy()
    if account_history.empty:
        st.info(t(lang, "no_history"))
        return

    account_history["date"] = account_history["timestamp"].dt.date
    by_day = (
        account_history.groupby("date", as_index=False)
        .agg(requests=("requests", "sum"), cost=("cost", "sum"))
        .sort_values("date")
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        fig = px.line(
            by_day,
            x="date",
            y="requests",
            markers=True,
            title=t(lang, "requests_over_time"),
            labels={"date": t(lang, "chart_date"), "requests": t(lang, "chart_requests")},
        )
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        fig = px.bar(
            by_day,
            x="date",
            y="cost",
            title=t(lang, "cost_over_time"),
            labels={"date": t(lang, "chart_date"), "cost": t(lang, "chart_cost")},
        )
        st.plotly_chart(fig, use_container_width=True)


def render_overview_chart(accounts: list[AccountSnapshot], lang: str) -> None:
    df = pd.DataFrame(
        [
            {
                t(lang, "table_account"): account.name,
                t(lang, "chart_used_today"): account.used_today,
                t(lang, "chart_remaining_today"): account.remaining_today,
            }
            for account in accounts
        ]
    )

    if df.empty:
        return

    account_column = t(lang, "table_account")
    fig = px.bar(
        df,
        x=account_column,
        y=[t(lang, "chart_used_today"), t(lang, "chart_remaining_today")],
        barmode="stack",
        title=t(lang, "quota_split"),
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title=t("en", "page_title"), page_icon="📊", layout="wide")

    lang_choice = st.sidebar.radio(
        t("en", "language_label"),
        options=["English", "中文"],
        index=0,
        help=t("en", "language_help"),
    )
    lang = "en" if lang_choice == "English" else "zh"

    st.title(t(lang, "title"))
    st.caption(t(lang, "caption"))

    accounts = load_accounts()
    history = load_usage_history()

    if not accounts:
        st.warning(t(lang, "no_accounts"))
        st.stop()

    render_summary_cards(accounts, lang)
    st.divider()

    render_overview_chart(accounts, lang)
    st.divider()

    st.subheader(t(lang, "overview"))
    render_account_table(accounts, lang)

    st.divider()
    account_names = [f"{a.name} ({a.account_id})" for a in accounts]
    selected = st.selectbox(t(lang, "choose_account"), account_names, index=0)
    selected_account_id = selected.rsplit("(", 1)[-1].rstrip(")")
    selected_account = next(a for a in accounts if a.account_id == selected_account_id)
    render_account_details(selected_account, history, lang)

    st.divider()
    st.subheader(t(lang, "how_to_use"))
    st.markdown(
        "\n".join(
            [
                f"1. {t(lang, 'usage_step_1')}",
                f"2. {t(lang, 'usage_step_2')}",
                f"3. {t(lang, 'usage_step_3')}",
                "",
                t(lang, "usage_more"),
                f"- {t(lang, 'usage_bullets')[0]}",
                f"- {t(lang, 'usage_bullets')[1]}",
                f"- {t(lang, 'usage_bullets')[2]}",
            ]
        )
    )


if __name__ == "__main__":
    main()
