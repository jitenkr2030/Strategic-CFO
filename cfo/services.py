from decimal import Decimal
from django.db.models import Sum, Q
from .models import FinancialTransaction, FinancialAccount, Budget, Forecast, Risk

def money(value):
    return Decimal(value or 0).quantize(Decimal("0.01"))

def financial_summary(org):
    tx=FinancialTransaction.objects.filter(organization=org)
    incoming=tx.filter(direction="in").aggregate(v=Sum("amount"))["v"] or Decimal("0")
    outgoing=tx.filter(direction="out").aggregate(v=Sum("amount"))["v"] or Decimal("0")
    revenue=tx.filter(account__account_type="revenue",direction="in").aggregate(v=Sum("amount"))["v"] or Decimal("0")
    expenses=tx.filter(account__account_type="expense",direction="out").aggregate(v=Sum("amount"))["v"] or Decimal("0")
    cash=incoming-outgoing
    profit=revenue-expenses
    margin=(profit/revenue*100) if revenue else Decimal("0")
    monthly_burn=expenses/12 if expenses else Decimal("0")
    runway=(cash/monthly_burn) if monthly_burn>0 and cash>0 else None
    return {"revenue":money(revenue),"expenses":money(expenses),"profit":money(profit),
      "cash":money(cash),"margin":money(margin),"runway":runway,"transactions":tx.count()}

def budget_variance(org):
    rows=[]
    for b in Budget.objects.filter(organization=org):
        actual=FinancialTransaction.objects.filter(organization=org,date__gte=b.period_start,date__lte=b.period_end,
            account__name__iexact=b.category,direction="out").aggregate(v=Sum("amount"))["v"] or Decimal("0")
        rows.append({"budget":b,"actual":actual,"variance":b.amount-actual})
    return rows

def forecast_projection(org):
    return Forecast.objects.filter(organization=org).order_by("month")

def risk_score(probability,impact):
    return int(probability)*int(impact)

def scenario(revenue,expense,revenue_change=0,expense_change=0):
    r=Decimal(str(revenue))*(1+Decimal(str(revenue_change))/100)
    e=Decimal(str(expense))*(1+Decimal(str(expense_change))/100)
    return {"revenue":r,"expenses":e,"profit":r-e,"margin":(r-e)/r*100 if r else Decimal("0")}

def business_health(summary, open_risks=0):
    score=70
    if summary["margin"]<0: score-=25
    elif summary["margin"]<10: score-=10
    if summary["cash"]<0: score-=25
    if open_risks>5: score-=10
    return max(0,min(100,score))
