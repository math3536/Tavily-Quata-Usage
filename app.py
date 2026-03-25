from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
USAGE_FILE = DATA_DIR / "usage_history.csv"


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
        return pd.DataFrame(
            columns=["timestamp", "account_id", "account_name", "requests", "cost"]
        )

    df = pd.read_csv(USAGE_FILE)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def render_summary_cards(accounts: list[AccountSnapshot]) -> None:
    total_daily_limit = sum(a.daily_limit for a in accounts)
    total_used_today = sum(a.used_today for a in accounts)
    total_monthly_limit = sum(a.monthly_limit for a in accounts)
    total_used_month = sum(a.used_month for a in accounts)

    cols = st.columns(4)
    metrics = [
        ("Accounts", len(accounts)),
        ("Daily used", f"{total_used_today}/{total_daily_limit}"),
        ("Monthly used", f"{total_used_month}/{total_monthly_limit}"),
        ("At risk", sum(1 for a in accounts if a.daily_ratio >= 0.8 or a.monthly_ratio >= 0.8)),
    ]

    for col, (label, value) in zip(cols, metrics, strict=True):
        col.metric(label, value)


def render_account_table(accounts: list[AccountSnapshot]) -> pd.DataFrame:
    rows = []
    for account in accounts:
        rows.append(
            {
                "Account": account.name,
                "Tier": account.tier,
                "Used Today": account.used_today,
                "Daily Limit": account.daily_limit,
                "Remaining Today": account.remaining_today,
                "Used Month": account.used_month,
                "Monthly Limit": account.monthly_limit,
                "Remaining Month": account.remaining_month,
                "Daily %": round(account.daily_ratio * 100, 1),
                "Monthly %": round(account.monthly_ratio * 100, 1),
                "Last Updated": account.last_updated,
            }
        )

    table = pd.DataFrame(rows)
    st.dataframe(table, use_container_width=True, hide_index=True)
    return table


def render_account_details(account: AccountSnapshot, history: pd.DataFrame) -> None:
    st.subheader(f"{account.name} details")

    cols = st.columns(4)
    cols[0].metric("Used today", f"{account.used_today}/{account.daily_limit}")
    cols[1].metric("Remaining today", account.remaining_today)
    cols[2].metric("Used month", f"{account.used_month}/{account.monthly_limit}")
    cols[3].metric("Remaining month", account.remaining_month)

    progress_cols = st.columns(2)
    progress_cols[0].progress(min(account.daily_ratio, 1.0), text=f"Daily usage {account.daily_ratio:.0%}")
    progress_cols[1].progress(min(account.monthly_ratio, 1.0), text=f"Monthly usage {account.monthly_ratio:.0%}")

    account_history = history[history["account_id"] == account.account_id].copy()
    if account_history.empty:
        st.info("No history available for this account yet.")
        return

    account_history["date"] = account_history["timestamp"].dt.date
    by_day = (
        account_history.groupby("date", as_index=False)
        .agg(requests=("requests", "sum"), cost=("cost", "sum"))
        .sort_values("date")
    )

    chart_left, chart_right = st.columns(2)
    with chart_left:
        fig = px.line(by_day, x="date", y="requests", markers=True, title="Requests over time")
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        fig = px.bar(by_day, x="date", y="cost", title="Cost over time")
        st.plotly_chart(fig, use_container_width=True)


def render_overview_chart(accounts: list[AccountSnapshot]) -> None:
    df = pd.DataFrame(
        [
            {
                "Account": account.name,
                "Used Today": account.used_today,
                "Remaining Today": account.remaining_today,
            }
            for account in accounts
        ]
    )

    if df.empty:
        return

    fig = px.bar(
        df,
        x="Account",
        y=["Used Today", "Remaining Today"],
        barmode="stack",
        title="Today quota split by account",
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Tavily Quota Monitor", page_icon="📊", layout="wide")
    st.title("Tavily 多账号额度监控")
    st.caption("用于汇总多个 Tavily 账号/Key 的剩余额度、消耗趋势和风险告警。")

    accounts = load_accounts()
    history = load_usage_history()

    if not accounts:
        st.warning("没有找到 accounts.json。先放入示例数据或接入你的真实数据源。")
        st.stop()

    render_summary_cards(accounts)
    st.divider()

    render_overview_chart(accounts)
    st.divider()

    st.subheader("Account overview")
    render_account_table(accounts)

    st.divider()
    account_names = [f"{a.name} ({a.account_id})" for a in accounts]
    selected = st.selectbox("Choose an account", account_names, index=0)
    selected_account_id = selected.rsplit("(", 1)[-1].rstrip(")")
    selected_account = next(a for a in accounts if a.account_id == selected_account_id)
    render_account_details(selected_account, history)

    st.divider()
    st.subheader("How to use")
    st.markdown(
        """
        1. 把你的账号快照写进 `data/accounts.json`
        2. 把历史请求/成本写进 `data/usage_history.csv`
        3. 启动 `streamlit run app.py`

        如果你想自动采集，我可以继续帮你加：
        - 定时拉取脚本
        - GitHub Actions 定时同步
        - Webhook/告警推送到 Telegram、飞书或企业微信
        """
    )


if __name__ == "__main__":
    main()
