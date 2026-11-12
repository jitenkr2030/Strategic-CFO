from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import *
from .services import financial_summary, scenario, business_health

class FinancialServiceTests(TestCase):
    def setUp(self):
        self.org=Organization.objects.create(name="Test Co")
        self.rev=FinancialAccount.objects.create(organization=self.org,name="Sales",account_type="revenue")
        self.exp=FinancialAccount.objects.create(organization=self.org,name="Rent",account_type="expense")
        FinancialTransaction.objects.create(organization=self.org,account=self.rev,date="2026-04-01",description="Sale",amount=1000,direction="in")
        FinancialTransaction.objects.create(organization=self.org,account=self.exp,date="2026-04-02",description="Rent",amount=300,direction="out")
    def test_summary(self):
        s=financial_summary(self.org)
        self.assertEqual(s["revenue"],Decimal("1000.00"))
        self.assertEqual(s["profit"],Decimal("700.00"))
    def test_scenario(self):
        s=scenario(1000,500,10,0)
        self.assertEqual(s["profit"],Decimal("600.0"))
    def test_health_bounded(self):
        self.assertLessEqual(business_health(financial_summary(self.org)),100)

class DashboardAccessTests(TestCase):
    def test_login_required(self):
        response=self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code,302)
