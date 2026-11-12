from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns=[
 path("login/",auth_views.LoginView.as_view(template_name="registration/login.html"),name="login"),
 path("setup/",views.setup,name="setup"),
 path("",views.dashboard,name="dashboard"),
 path("transactions/",views.transactions,name="transactions"),
 path("transactions/add/",views.transaction_create,name="transaction_create"),
 path("transactions/import/",views.import_transactions,name="import_transactions"),
 path("transactions/export.xlsx",views.export_transactions,name="export_transactions"),
 path("accounts/",views.accounts,name="accounts"),
 path("budgets/",views.budgets,name="budgets"),
 path("forecasts/",views.forecasts,name="forecasts"),
 path("scenarios/",views.scenario_tool,name="scenario_tool"),
 path("kpis/",views.kpis,name="kpis"),
 path("decisions/",views.decisions,name="decisions"),
 path("risks/",views.risks,name="risks"),
 path("fundraising/",views.fundraising,name="fundraising"),
 path("copilot/",views.copilot,name="copilot"),
 path("integrations/",views.integrations,name="integrations"),
 path("reports/",views.reports,name="reports"),
 path("reports/summary.csv",views.report_csv,name="report_csv"),
]
