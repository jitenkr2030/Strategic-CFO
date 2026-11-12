from django.contrib import admin
from .models import *
for model in [Organization,Membership,FinancialAccount,FinancialTransaction,Budget,Forecast,KPI,
              AdvisoryDecision,Fundraising,Risk,ReportRecord,IntegrationConfig,AuditLog]:
    admin.site.register(model)
