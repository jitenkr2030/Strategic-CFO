import csv
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from .models import *
from .forms import *
from .services import financial_summary, budget_variance, forecast_projection, scenario, business_health
from .ai import copilot_answer, ai_provider_status

def current_org(user):
    membership=Membership.objects.filter(user=user,is_active=True).select_related("organization").first()
    return membership.organization if membership else None

def require_org(view):
    def wrapped(request,*args,**kwargs):
        org=current_org(request.user)
        if not org:
            return redirect("setup")
        request.organization=org
        return view(request,*args,**kwargs)
    return wrapped

@login_required
def setup(request):
    if current_org(request.user): return redirect("dashboard")
    form=OrganizationForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        with transaction.atomic():
            org=form.save()
            Membership.objects.create(organization=org,user=request.user,role="owner")
            defaults=[
              ("Sales Revenue","4000","revenue"),("Service Revenue","4100","revenue"),
              ("Cost of Goods Sold","5000","expense"),("Salaries","5100","expense"),
              ("Rent","5200","expense"),("Marketing","5300","expense"),
              ("Bank","1000","asset"),("Accounts Receivable","1100","asset"),
              ("Accounts Payable","2000","liability"),("Owner Equity","3000","equity")]
            for name,code,typ in defaults: FinancialAccount.objects.create(organization=org,name=name,code=code,account_type=typ)
        messages.success(request,"Organization created. Your finance workspace is ready.")
        return redirect("dashboard")
    return render(request,"cfo/form.html",{"form":form,"title":"Create your organization"})

@login_required
@require_org
def dashboard(request):
    org=request.organization
    summary=financial_summary(org)
    risks=Risk.objects.filter(organization=org,status="open")
    context={"org":org,"summary":summary,"health":business_health(summary,risks.count()),
      "risks":risks[:5],"budgets":budget_variance(org)[:5],
      "forecasts":forecast_projection(org)[:6],"recent":FinancialTransaction.objects.filter(organization=org)[:8],
      "decision_count":AdvisoryDecision.objects.filter(organization=org).count()}
    return render(request,"cfo/dashboard.html",context)

@login_required
@require_org
def transactions(request):
    org=request.organization
    qs=FinancialTransaction.objects.filter(organization=org).select_related("account")
    return render(request,"cfo/transactions.html",{"transactions":qs[:250],"accounts":FinancialAccount.objects.filter(organization=org)})

@login_required
@require_org
def transaction_create(request):
    org=request.organization
    form=TransactionForm(request.POST or None)
    form.fields["account"].queryset=FinancialAccount.objects.filter(organization=org)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save()
        AuditLog.objects.create(organization=org,user=request.user,action="Created transaction",object_type="FinancialTransaction",object_id=obj.pk)
        messages.success(request,"Transaction saved.")
        return redirect("transactions")
    return render(request,"cfo/form.html",{"form":form,"title":"Add financial transaction"})

@login_required
@require_org
def accounts(request):
    org=request.organization
    form=AccountForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("accounts")
    return render(request,"cfo/accounts.html",{"accounts":FinancialAccount.objects.filter(organization=org),"form":form})

@login_required
@require_org
def budgets(request):
    org=request.organization; form=BudgetForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.owner=request.user; obj.save()
        messages.success(request,"Budget created."); return redirect("budgets")
    return render(request,"cfo/budgets.html",{"form":form,"rows":budget_variance(org)})

@login_required
@require_org
def forecasts(request):
    org=request.organization; form=ForecastForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("forecasts")
    return render(request,"cfo/forecasts.html",{"form":form,"forecasts":forecast_projection(org)})

@login_required
@require_org
def scenario_tool(request):
    result=None
    if request.method=="POST":
        try:
            result=scenario(request.POST.get("revenue","0"),request.POST.get("expenses","0"),
                request.POST.get("revenue_change","0"),request.POST.get("expense_change","0"))
        except (InvalidOperation,ValueError): messages.error(request,"Enter valid numeric values.")
    return render(request,"cfo/scenario.html",{"result":result})

@login_required
@require_org
def kpis(request):
    org=request.organization; form=KPIForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("kpis")
    return render(request,"cfo/kpis.html",{"form":form,"items":KPI.objects.filter(organization=org)})

@login_required
@require_org
def decisions(request):
    org=request.organization; form=DecisionForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.decision_owner=request.user; obj.save()
        return redirect("decisions")
    return render(request,"cfo/decisions.html",{"form":form,"items":AdvisoryDecision.objects.filter(organization=org)})

@login_required
@require_org
def risks(request):
    org=request.organization; form=RiskForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("risks")
    return render(request,"cfo/risks.html",{"form":form,"items":Risk.objects.filter(organization=org)})

@login_required
@require_org
def fundraising(request):
    org=request.organization; form=FundraisingForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("fundraising")
    return render(request,"cfo/fundraising.html",{"form":form,"items":Fundraising.objects.filter(organization=org)})

@login_required
@require_org
def copilot(request):
    org=request.organization; answer=None; question=""
    if request.method=="POST":
        question=request.POST.get("question","").strip()
        if question: answer=copilot_answer(question,financial_summary(org))
    return render(request,"cfo/copilot.html",{"answer":answer,"question":question,"ai_status":ai_provider_status()})

@login_required
@require_org
def integrations(request):
    org=request.organization; form=IntegrationForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        obj=form.save(commit=False); obj.organization=org; obj.save(); return redirect("integrations")
    return render(request,"cfo/integrations.html",{"form":form,"items":IntegrationConfig.objects.filter(organization=org)})

@login_required
@require_org
def reports(request):
    org=request.organization; s=financial_summary(org)
    return render(request,"cfo/reports.html",{"summary":s,"org":org})

@login_required
@require_org
def export_transactions(request):
    org=request.organization
    wb=Workbook(); ws=wb.active; ws.title="Transactions"
    ws.append(["Date","Account","Description","Reference","Amount","Direction","Counterparty","Department"])
    for t in FinancialTransaction.objects.filter(organization=org).select_related("account"):
        ws.append([t.date.isoformat(),t.account.name,t.description,t.reference,float(t.amount),t.direction,t.counterparty,t.department])
    response=HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"]='attachment; filename="strategic_cfo_transactions.xlsx"'
    wb.save(response); return response

@login_required
@require_org
def import_transactions(request):
    org=request.organization
    if request.method=="POST" and request.FILES.get("file"):
        try:
            wb=load_workbook(request.FILES["file"],data_only=True); ws=wb.active
            count=0
            for row in ws.iter_rows(min_row=2,values_only=True):
                if not row or not row[0]: continue
                date,account_name,description,reference,amount,direction,*rest=row
                account=FinancialAccount.objects.filter(organization=org,name=str(account_name)).first()
                if not account: continue
                FinancialTransaction.objects.create(organization=org,account=account,date=date,description=str(description or ""),
                    reference=str(reference or ""),amount=Decimal(str(amount)),direction=str(direction or "out").lower(),
                    counterparty=str(rest[0] or "") if len(rest)>0 else "",department=str(rest[1] or "") if len(rest)>1 else "")
                count+=1
            messages.success(request,f"Imported {count} transaction(s).")
        except Exception as exc: messages.error(request,f"Import failed: {exc}")
        return redirect("transactions")
    return render(request,"cfo/import.html")

@login_required
@require_org
def report_csv(request):
    org=request.organization
    response=HttpResponse(content_type="text/csv")
    response["Content-Disposition"]='attachment; filename="strategic_cfo_summary.csv"'
    writer=csv.writer(response); writer.writerow(["Metric","Value"])
    for k,v in financial_summary(org).items(): writer.writerow([k,str(v)])
    return response
