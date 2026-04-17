# mcp-mayo

[![PyPI version](https://img.shields.io/pypi/v/mcp-mayo)](https://pypi.org/project/mcp-mayo/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-mayo)](https://pypi.org/project/mcp-mayo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io/)
[![GitHub stars](https://img.shields.io/github/stars/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/asgard-ai-platform/mcp-mayo)](https://github.com/asgard-ai-platform/mcp-mayo/commits/main)

[MAYO Apollo](https://www.mayohr.com/) 的 MCP Server — 把 HRM 平台的人事 (Foundation)、差勤 (Attendance)、薪資勞健保 (Payroll) API 透過 [Model Context Protocol](https://modelcontextprotocol.io/) 包成 AI 可呼叫的工具。

[English](README.md) · 屬於 [Asgard AI Platform](https://github.com/asgard-ai-platform) 開源生態系。

## 特色

- **33 個工具** — 28 個一對一的 endpoint 包裝 + 5 個語意化組合工具
- **三個後端網域** — Foundation / Attendance / Payroll 用同一把 `hrmlicense` API key 就能存取
- **日期格式自動轉換** — 呼叫端用 ISO `YYYY-MM-DD` / `YYYY-MM`，內部轉成各 endpoint 要求的格式
- **語意化聚合** — 例如 `get_employee_profile`、`get_organization_snapshot_as_of`、`get_attendance_summary` 一次回應完整資訊
- **Pydantic 型別** — 每個參數都有 AI 可讀的描述
- **E2E 測試** — 對著 PRE 環境跑完所有工具

## 前置條件

- Python 3.10+
- `uv` (建議) 或 `pip`
- MAYO 核發的 `hrmlicense` API key，且具備 FD / PT / PY 所需的讀取權限

## 安裝

### 從原始碼 (目前狀態)

```bash
git clone https://github.com/asgard-ai-platform/mcp-mayo.git
cd mcp-mayo
uv sync
cp .env.example .env
# 編輯 .env，填入 MAYO_API_KEY
```

### 從 PyPI (發佈後)

```bash
uv add mcp-mayo
# 或
pip install mcp-mayo
```

## 設定

| 環境變數 | 必要 | 用途 |
|---|---|---|
| `MAYO_API_KEY` | 是 | 放在 `hrmlicense` header 的金鑰；單一憑證即可存取 FD / PT / PY |

## 使用方式

### 本機執行

```bash
uv run --env-file .env python mcp_server.py
```

### Claude Desktop

```json
{
  "mcpServers": {
    "mayo": {
      "command": "uvx",
      "args": ["mcp-mayo"],
      "env": {
        "MAYO_API_KEY": "your_hrmlicense_token"
      }
    }
  }
}
```

### Claude Code (`.mcp.json`)

```json
{
  "mcpServers": {
    "mayo": {
      "command": "uv",
      "args": ["run", "mcp-mayo"],
      "cwd": "${PWD}",
      "env": {
        "PYTHONPATH": "${PWD}",
        "MAYO_API_KEY": "${MAYO_API_KEY}"
      }
    }
  }
}
```

### Cursor / 其他 IDE

讓 MCP client 以 `uvx mcp-mayo` 啟動，並在環境中提供 `MAYO_API_KEY`。

## 工具清單

### 語意化工具 (AI 優先使用)

| 工具 | 功能 |
|---|---|
| `get_employee_profile` | 一次拿到一位員工的 PA + 工作經歷 + 學歷 |
| `get_organization_snapshot_as_of` | 指定日期的組織樹 + 在職名單 |
| `get_attendance_summary` | 一次取回區間的出勤/異常/加班/請假 |
| `search_active_employees` | 預設以今天為基準的在職名單 |
| `get_monthly_payroll_report` | 以 ISO `YYYY-MM` 取單月薪資發放清冊 |

### 人事 Foundation (FD) — 15

`list_active_employees` ¹、`list_resigned_employees` ¹、`get_organization_tree` ¹、`export_organization_with_employees`、`export_employees`、`export_departments`、`export_organization_full`、`export_employees_full`、`export_expatriations`、`export_working_history`、`export_education_history`、`export_employee_changes`、`export_organization_changes`、`export_pa_options`、`export_company_custom_fields`

### 差勤 Attendance (PT) — 8

`get_attendance_rules`、`get_attendance_history`、`get_attendance_abnormal`、`get_forgot_checkin_records`、`get_leave_history`、`get_employee_calendar`、`get_overtime_records`、`get_trip_history` ²

### 薪資勞健保 Payroll (PY) — 5

`get_monthly_labor_insurance` ²、`get_monthly_nhi` ²、`get_monthly_labor_pension` ²、`get_salary_insurance_detail`、`get_salary_bonus_list`

¹ 三支 `/ClientOut/ReportCenter/*` (加上依賴它們的語意化工具 `search_active_employees` / `get_organization_snapshot_as_of`) 目前在 PRE Foundation 後端會回 404，工具仍保留以便 MAYO 補上該環境路由後立即生效。

² 在 MAYO 官方 Postman collection 中被標註為伺服器端已報錯的 endpoint。本專案仍保留包裝，當 MAYO 修復後立即可用；docstring 內會看到 `KNOWN ISSUE` 標示。

## 使用範例

### 「C030010 部門還在職的人」

> **You:** 昨天 C030010 部門還在職的人列一下

**AI 呼叫：**

```
search_active_employees(
  dept_code = "C030010",
)
```

**結果：** `SUCCESS` — 以今天為生效日期呼叫 Foundation 的 ActiveEmployeeData，回傳在職名單。

### 「員工完整資料」

> **You:** 給我員編 A00384 的完整資料

**AI 呼叫：**

```
get_employee_profile(
  employee_number = "A00384",
)
```

**結果：** `SUCCESS` — 組合 `/PA` + `/Working` + `/Education`，後兩者在本地 filter 到 A00384。

### 「9/1 到 9/7 的出勤統計」

> **You:** 9/1 到 9/7 的出勤統計，含異常跟加班

**AI 呼叫：**

```
get_attendance_summary(
  start_date = "2025-09-01",
  end_date   = "2025-09-07",
)
```

**結果：** `SUCCESS` — 回傳該區間的出勤/異常/加班/請假各區塊。

### 「單月薪資清冊」

> **You:** 2025-01 的薪資發放清冊

**AI 呼叫：**

```
get_monthly_payroll_report(
  year_month = "2025-01",
)
```

**結果：** `SUCCESS` — 內部轉成 `2025/01` 呼叫 SalaryBonusList。

## 架構

```
stdio (JSON-RPC 2.0)
  → mcp_server.py                 程式入口；匯入所有工具模組
    → app.py                      FastMCP("mcp-mayo") 單例
      → tools/                    @mcp.tool() 註冊的函式
          foundation_tools.py       15 個 FD 包裝
          attendance_tools.py       8 個 PT 包裝
          payroll_tools.py          5 個 PY 包裝
          semantic_tools.py         5 個語意化組合
        → connectors/rest_client.py   重試 + 多網域 URL 解析
          → auth/api_key.py           產生 {"hrmlicense": <MAYO_API_KEY>}
            → config/settings.py      BASE_URLS + ENDPOINTS (依網域分類)
```

## 測試

```bash
uv run --env-file .env python scripts/auth/test_connection.py   # 探測 FD / PT / PY
uv run --env-file .env python tests/test_all_tools.py           # 跑全部工具
```

## 貢獻

請見 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 授權

MIT — 詳見 [LICENSE](LICENSE)。
