# Tavily Quota Monitor

A lightweight Streamlit dashboard for monitoring multiple Tavily accounts/keys and visualizing quota usage.

## Features

- Multi-account quota overview
- Daily and monthly usage cards
- Remaining quota indicators
- Trend charts for requests and cost
- Simple JSON/CSV-based data source for easy integration

## Quick Start

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Data Format

### `data/accounts.json`

Each account needs:

- `account_id`
- `name`
- `tier`
- `daily_limit`
- `monthly_limit`
- `used_today`
- `used_month`
- `last_updated`

### `data/usage_history.csv`

Columns:

- `timestamp`
- `account_id`
- `account_name`
- `requests`
- `cost`

## Next Steps

If you want real automatic monitoring, the next upgrade is to add a collector that syncs quotas from your Tavily billing or usage source on a schedule.
