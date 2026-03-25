# Tavily Quota Monitor

A lightweight Streamlit dashboard for tracking multiple Tavily accounts or keys and visualizing quota usage.

## Table of Contents

- [English](#english)
- [中文](#中文)

## English

### Overview

This project provides a simple dashboard for:

- monitoring usage across multiple accounts
- comparing daily and monthly quota consumption
- spotting accounts that are close to their limits
- reviewing usage history with charts

### Features

- Multi-account quota overview
- Daily and monthly usage cards
- Remaining quota indicators
- Trend charts for requests and cost
- English/Chinese interface switcher
- JSON and CSV data sources for easy integration

### Project Structure

```text
.
├── app.py
├── data/
│   ├── accounts.json
│   └── usage_history.csv
├── requirements.txt
└── README.md
```

### Quick Start

#### 1. Create a virtual environment

```bash
python -m venv .venv
```

#### 2. Activate it

```bash
.venv\\Scripts\\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the app

```bash
streamlit run app.py
```

### Data Format

#### `data/accounts.json`

Example:

```json
[
  {
    "account_id": "acct-001",
    "name": "Main Account",
    "tier": "pro",
    "daily_limit": 1000,
    "monthly_limit": 30000,
    "used_today": 120,
    "used_month": 3800,
    "last_updated": "2026-03-25 09:00:00"
  }
]
```

Required fields:

- `account_id`
- `name`
- `tier`
- `daily_limit`
- `monthly_limit`
- `used_today`
- `used_month`
- `last_updated`

#### `data/usage_history.csv`

Example:

```csv
timestamp,account_id,account_name,requests,cost
2026-03-25 08:00:00,acct-001,Main Account,25,0.42
```

Columns:

- `timestamp`
- `account_id`
- `account_name`
- `requests`
- `cost`

### Deployment Notes

- Local development works with `streamlit run app.py`.
- For GitHub-based workflows, you can add a scheduled sync job later to refresh `data/accounts.json` and `data/usage_history.csv`.
- The app is designed to be simple to extend if you later connect it to Tavily billing, logs, or a custom collector.


## 中文

### 概览

这个项目提供一个简单的仪表盘，用于：

- 监控多个账号的使用情况
- 对比每日和每月额度消耗
- 发现接近上限的账号
- 通过图表查看历史使用趋势

### 功能

- 多账号额度总览
- 每日和每月使用卡片
- 剩余额度提示
- 请求数和成本趋势图
- 中英文界面切换
- 基于 JSON 和 CSV 的数据源，方便接入

### 项目结构

```text
.
├── app.py
├── data/
│   ├── accounts.json
│   └── usage_history.csv
├── requirements.txt
└── README.md
```

### 快速开始

#### 1. 创建虚拟环境

```bash
python -m venv .venv
```

#### 2. 激活虚拟环境

```bash
.venv\\Scripts\\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 启动应用

```bash
streamlit run app.py
```

### 数据格式

#### `data/accounts.json`

示例：

```json
[
  {
    "account_id": "acct-001",
    "name": "Main Account",
    "tier": "pro",
    "daily_limit": 1000,
    "monthly_limit": 30000,
    "used_today": 120,
    "used_month": 3800,
    "last_updated": "2026-03-25 09:00:00"
  }
]
```

必需字段：

- `account_id`
- `name`
- `tier`
- `daily_limit`
- `monthly_limit`
- `used_today`
- `used_month`
- `last_updated`

#### `data/usage_history.csv`

示例：

```csv
timestamp,account_id,account_name,requests,cost
2026-03-25 08:00:00,acct-001,Main Account,25,0.42
```

字段包括：

- `timestamp`
- `account_id`
- `account_name`
- `requests`
- `cost`

### 部署说明

- 本地开发可以直接使用 `streamlit run app.py`。
- 如果你后续要基于 GitHub 做自动同步，可以增加定时任务来刷新 `data/accounts.json` 和 `data/usage_history.csv`。
- 这个项目保持了较轻的结构，后续接入 Tavily 账单、日志或自定义采集器时会比较容易扩展。

- 增加 JSON / CSV 格式校验
