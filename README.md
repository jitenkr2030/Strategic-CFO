# Strategic CFO — Django SaaS Starter

A runnable modular Django application for financial intelligence, planning, forecasting, profitability analysis, cash-flow visibility, working-capital planning, advisory decisions, fundraising records, risk registers, reporting and a deterministic CFO assistant.

## Included development phases

| Phase | Scope | Implemented in this starter |
|---|---|---|
| 1 | Authentication, organization and user management | Django auth, organization setup, membership roles, admin |
| 2 | Financial dashboard and data management | Dashboard, chart of accounts, transaction entry, XLSX import/export |
| 3 | FP&A, budgeting and forecasting | Budgets, variance, forecast records, scenarios |
| 4 | Profitability and cash flow | Revenue, expense, profit, margin and net transaction cash calculations |
| 5 | Working capital and financial modeling | Financial scenario simulator; working-capital base models can be extended |
| 6 | Business performance and cost optimization | KPI tracking and budget variance visibility |
| 7 | Strategic advisory and decision support | Decision register, owner, expected benefit/cost, status |
| 8 | Fundraising and business valuation | Funding round, committed amount, pre/post-money calculation |
| 9 | Risk management and board reporting | Risk register and export/report centre |
| 10 | AI CFO Copilot and predictive intelligence | Deterministic financial Q&A fallback; provider adapter point |
| 11 | Integrations and automated data collection | Integration registry; live provider connectors require credentials and provider-specific implementation |
| 12 | Enterprise security, testing and deployment | Organization-scoped querysets, Django auth, audit events, tests, PostgreSQL option, Gunicorn/WhiteNoise |

This is a functional starter/MVP, not a certified accounting package or a fully production-hardened enterprise system. An optional OpenAI-compatible chat-completions integration is available through `AI_API_KEY`, `AI_MODEL` and `AI_BASE_URL`; without a key, the deterministic local assistant is used. Live bank/GST/UPI integrations are not included.

## Requirements

- Python 3.10+
- pip
- Windows, Linux, macOS or WSL

## Run locally (Linux / WSL)

```bash
cd strategic_cfo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations cfo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in. The first login redirects to organization setup.

## Run on Windows PowerShell

```powershell
cd strategic_cfo
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations cfo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## First-use workflow

1. Create a superuser.
2. Sign in and create an organization.
3. Open Chart of Accounts and add any needed accounts.
4. Add transactions (inflows and outflows).
5. Create budgets, forecasts, KPIs, strategic decisions and risks.
6. Review dashboard and reports.
7. Import/export transactions using the documented XLSX column order.

## Excel import format

First worksheet; first row is a header. Required columns:
`Date | Account | Description | Reference | Amount | Direction | Counterparty | Department`

Date should be an Excel date or ISO date. Direction must be `in` or `out`.

## PostgreSQL

Set `DATABASE_URL` in `.env`, for example:
`postgresql://username:password@localhost:5432/strategic_cfo`
Then run migrations. SQLite is the default for quick local setup.

## Security and tenant isolation

The application associates business records with an organization and filters the normal user-facing views by the active membership. The Django admin is a privileged administrative interface; restrict admin accounts carefully. Before production, add invitation flows, enforce role permissions on every write, stronger tenant isolation tests, secrets management, TLS, backups, monitoring, rate limiting, and security review.

## Financial calculation notes

- Transaction cash is calculated as total inflows minus total outflows across entered records.
- Revenue and expenses are determined by account type plus transaction direction.
- The displayed cash figure is net movement, not a bank-verified closing balance; opening balances and bank reconciliation are not yet modeled.
- Runway is a rough estimate based on the current net cash movement and annualized entered expense total. Do not use it for funding or solvency decisions without a proper monthly cash-flow model.
- Budget variance currently matches budget category to account name and sums outflows inside the budget date range. Configure category/account names consistently.
- Valuation and scenario tools are simplified planning aids, not formal valuation opinions.

## Tests

```bash
python manage.py test
```

## Production checklist

- Set `DEBUG=0`, a strong random `SECRET_KEY`, and correct `ALLOWED_HOSTS`.
- Configure PostgreSQL and encrypted backups.
- Configure HTTPS, secure cookies, CSRF trusted origins and email delivery.
- Add role-based authorization policies and audit coverage.
- Add automated bank/GST/ERP connectors only after reviewing provider APIs and customer consent.
- Add a real AI provider integration with strict data minimization, tenant-scoped retrieval, output validation and human approval.
- Run migrations and tests in CI before deployment.
