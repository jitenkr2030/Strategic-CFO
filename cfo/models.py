from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class Organization(models.Model):
    name=models.CharField(max_length=180)
    legal_name=models.CharField(max_length=180,blank=True)
    gstin=models.CharField(max_length=15,blank=True)
    currency=models.CharField(max_length=3,default="INR")
    financial_year_start_month=models.PositiveSmallIntegerField(default=4)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Membership(models.Model):
    ROLE_CHOICES=[("owner","Owner"),("cfo","CFO"),("finance","Finance Manager"),("analyst","Analyst"),("viewer","Viewer")]
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="memberships")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="cfo_memberships")
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default="owner")
    is_active=models.BooleanField(default=True)
    class Meta: unique_together=("organization","user")

class FinancialAccount(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    name=models.CharField(max_length=120)
    code=models.CharField(max_length=30,blank=True)
    account_type=models.CharField(max_length=20,choices=[("revenue","Revenue"),("expense","Expense"),("asset","Asset"),("liability","Liability"),("equity","Equity")])
    is_active=models.BooleanField(default=True)
    def __str__(self): return self.name

class FinancialTransaction(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    account=models.ForeignKey(FinancialAccount,on_delete=models.PROTECT)
    date=models.DateField()
    description=models.CharField(max_length=240)
    reference=models.CharField(max_length=80,blank=True)
    amount=models.DecimalField(max_digits=16,decimal_places=2,validators=[MinValueValidator(Decimal("0.01"))])
    direction=models.CharField(max_length=10,choices=[("in","Inflow"),("out","Outflow")])
    counterparty=models.CharField(max_length=180,blank=True)
    department=models.CharField(max_length=100,blank=True)
    product_or_service=models.CharField(max_length=140,blank=True)
    is_reconciled=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-date","-id"]
    def __str__(self): return f"{self.date} {self.description}"

class Budget(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    period_start=models.DateField()
    period_end=models.DateField()
    category=models.CharField(max_length=100)
    department=models.CharField(max_length=100,blank=True)
    amount=models.DecimalField(max_digits=16,decimal_places=2)
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    approved=models.BooleanField(default=False)
    notes=models.TextField(blank=True)
    class Meta: ordering=["-period_start"]

class Forecast(models.Model):
    SCENARIOS=[("base","Base"),("optimistic","Optimistic"),("pessimistic","Pessimistic")]
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    scenario=models.CharField(max_length=20,choices=SCENARIOS,default="base")
    month=models.DateField()
    revenue=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    expenses=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    cash_balance=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    assumptions=models.TextField(blank=True)

class KPI(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    name=models.CharField(max_length=120)
    target=models.DecimalField(max_digits=16,decimal_places=2)
    actual=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    unit=models.CharField(max_length=30,default="%")
    owner=models.CharField(max_length=120,blank=True)
    period=models.CharField(max_length=30,blank=True)
    def achievement(self):
        return (self.actual/self.target*100) if self.target else Decimal("0")

class AdvisoryDecision(models.Model):
    STATUS=[("draft","Draft"),("review","Under review"),("approved","Approved"),("rejected","Rejected"),("implemented","Implemented")]
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    title=models.CharField(max_length=180)
    description=models.TextField()
    expected_benefit=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    estimated_cost=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    risk_level=models.CharField(max_length=20,choices=[("low","Low"),("medium","Medium"),("high","High")],default="medium")
    status=models.CharField(max_length=20,choices=STATUS,default="draft")
    decision_owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    due_date=models.DateField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class Fundraising(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    round_name=models.CharField(max_length=100)
    target_amount=models.DecimalField(max_digits=16,decimal_places=2)
    pre_money_valuation=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    amount_committed=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    expected_close=models.DateField(null=True,blank=True)
    notes=models.TextField(blank=True)
    @property
    def post_money_valuation(self): return self.pre_money_valuation+self.target_amount

class Risk(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    title=models.CharField(max_length=180)
    category=models.CharField(max_length=80)
    probability=models.PositiveSmallIntegerField(default=3)
    impact=models.PositiveSmallIntegerField(default=3)
    mitigation=models.TextField(blank=True)
    owner=models.CharField(max_length=120,blank=True)
    status=models.CharField(max_length=20,choices=[("open","Open"),("mitigating","Mitigating"),("closed","Closed")],default="open")
    @property
    def score(self): return self.probability*self.impact

class ReportRecord(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    title=models.CharField(max_length=180)
    report_type=models.CharField(max_length=80)
    generated_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    file=models.FileField(upload_to="reports/",blank=True)

class IntegrationConfig(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    provider=models.CharField(max_length=100)
    endpoint=models.URLField(blank=True)
    enabled=models.BooleanField(default=False)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    action=models.CharField(max_length=120)
    object_type=models.CharField(max_length=100,blank=True)
    object_id=models.CharField(max_length=80,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
