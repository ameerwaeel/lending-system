from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal  


class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Lender(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Loan(models.Model):
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    term_in_months =models.IntegerField() 
    annual_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('funded', 'Funded'),
        ('completed', 'Completed')
    ], default='pending')
    lender = models.ForeignKey(Lender, null=True, blank=True, on_delete=models.SET_NULL)
    funded_at = models.DateTimeField(null=True, blank=True)

    def total_amount_due(self):
        # """Calculate total amount due including interest."""
        # return self.amount + (self.amount * (self.annual_interest_rate / 100) * (self.term_in_months / 12))
        interest_rate = Decimal(self.annual_interest_rate) / Decimal(100)
        term_in_years = Decimal(self.term_in_months) / Decimal(12)
        return self.amount + (self.amount * interest_rate * term_in_years)
    
class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)