# Strategic CFO implementation map

1. **Identity & tenant foundation:** Django authentication, organization onboarding, memberships, roles and organization-linked models.
2. **Financial data:** chart of accounts, transactions, dashboard, audit trail, XLSX import/export.
3. **Planning:** budget records, budget-vs-actual calculation, monthly forecast scenarios.
4. **Profitability/cash:** revenue, expense, profit, margin and net transaction movement summaries.
5. **Working capital/modeling:** scenario calculation engine. Extend with AR/AP/inventory subledgers, DSO/DPO/DIO and cash conversion cycle.
6. **Performance/cost:** KPI targets, achievement and budget variance monitoring.
7. **Advisory:** decision register, expected benefits/costs, risk level, owner and status.
8. **Fundraising/valuation:** funding rounds, commitments and pre-/post-money valuation arithmetic.
9. **Risk/board:** probability-impact register, risk scoring, CSV and XLSX exports.
10. **AI:** CFO question interface with deterministic fallback. Add a provider behind `cfo/ai.py`; never let an LLM be the source of truth for calculations.
11. **Integrations:** provider configuration registry. Add individual connector modules, OAuth/token vault, sync jobs, idempotency and reconciliation for each provider.
12. **Enterprise readiness:** tests, PostgreSQL support, deployment notes. Complete authorization, monitoring, backup restore drills, penetration testing and compliance review before production.
