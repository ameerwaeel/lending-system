from rest_framework import serializers
from .models import Borrower, Lender, Loan, Payment

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'borrower', 'amount', 'term_in_months', 'annual_interest_rate', 'status', 'lender', 'funded_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'loan', 'amount', 'due_date', 'is_paid']