# quant-ai-1k

A reproducible, auditable template for building a small-capital (CAD 1,000) quantitative trading stack that combines rule-based filters with an AI layer. The project is intentionally opinionated around survivability, discipline, and gradual scaling while respecting strict risk boundaries.

## Project goals
- Operate at daily/weekly frequency on USD ETFs (extendable to CAD-hedged ETFs).
- Enforce disciplined risk limits with soft (-25%) and hard (-50%) drawdown triggers.
- Provide modular components for data, feature engineering, modelling, execution, monitoring, and risk control.
- Enable paper-trading rehearsal before live deployment.

## Repository layout
```
quant-ai-1k/
├─ README.md
├─ pyproject.toml
├─ .env.example
├─ config/
├─ data/
├─ notebooks/
├─ src/
├─ scripts/
└─ models/
```

Refer to the comments within each configuration and source module for guidance on extending the template.

## Getting started
1. Clone the repository and create a Python 3.11 environment (conda or venv recommended).
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Copy `.env.example` to `.env` and fill in broker/API credentials.
4. Update the ETF universe in `config/universe.yml` and adjust risk settings in `config/risk.yml`.
5. Run the example data fetch and backtest scripts:
   ```bash
   python scripts/fetch_data.py
   python scripts/backtest.py
   ```

## Safety checklist
- Always validate new models with walk-forward analysis (`scripts/backtest.py`).
- Enforce risk limits through `src/core/risk.py` before placing any order.
- Maintain paper trading logs for at least one shadow week prior to going live.
- Back up configurations, models, and logs daily.

## Next steps
- Implement real data fetching pipelines in `src/core/data_loader.py`.
- Connect to your chosen broker via `src/exec/broker_ibkr.py` or an alternative adapter.
- Expand monitoring hooks (alerts, metrics) before enabling unattended execution.

## Disclaimer
This repository is a template. Ensure compliance with local regulations and broker policies before trading live capital.
