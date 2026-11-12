from django import forms
from .models import *
class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class","form-control")
class OrganizationForm(StyledModelForm):
    class Meta: model=Organization; fields=["name","legal_name","gstin","currency","financial_year_start_month"]
class TransactionForm(StyledModelForm):
    class Meta: model=FinancialTransaction; fields=["account","date","description","reference","amount","direction","counterparty","department","product_or_service","is_reconciled"]
    date=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
class AccountForm(StyledModelForm):
    class Meta: model=FinancialAccount; fields=["name","code","account_type","is_active"]
class BudgetForm(StyledModelForm):
    class Meta: model=Budget; fields=["name","period_start","period_end","category","department","amount","notes"]
    period_start=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    period_end=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
class ForecastForm(StyledModelForm):
    class Meta: model=Forecast; fields=["name","scenario","month","revenue","expenses","cash_balance","assumptions"]
    month=forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
class KPIForm(StyledModelForm):
    class Meta: model=KPI; fields=["name","target","actual","unit","owner","period"]
class DecisionForm(StyledModelForm):
    class Meta: model=AdvisoryDecision; fields=["title","description","expected_benefit","estimated_cost","risk_level","status","due_date"]
    due_date=forms.DateField(required=False,widget=forms.DateInput(attrs={"type":"date"}))
class RiskForm(StyledModelForm):
    class Meta: model=Risk; fields=["title","category","probability","impact","mitigation","owner","status"]
class FundraisingForm(StyledModelForm):
    class Meta: model=Fundraising; fields=["round_name","target_amount","pre_money_valuation","amount_committed","expected_close","notes"]
    expected_close=forms.DateField(required=False,widget=forms.DateInput(attrs={"type":"date"}))
class IntegrationForm(StyledModelForm):
    class Meta: model=IntegrationConfig; fields=["provider","endpoint","enabled","notes"]
