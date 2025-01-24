from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from loan_app.models import Borrower, Lender, Loan
from rest_framework_simplejwt.tokens import RefreshToken

class LoanTests(TestCase):
    def setUp(self):
        self.borrower_user = User.objects.create_user(username='borrower', password='password')
        self.lender_user = User.objects.create_user(username='lender', password='password')

        self.borrower = Borrower.objects.create(user=self.borrower_user, balance=1000)
        self.lender = Lender.objects.create(user=self.lender_user, balance=5000)

        self.client = APIClient()

        self.borrower_token = str(RefreshToken.for_user(self.borrower_user).access_token)
        self.lender_token = str(RefreshToken.for_user(self.lender_user).access_token)

    def authenticate_borrower(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.borrower_token}')

    def authenticate_lender(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.lender_token}')


def test_borrower_loan_request(self):
    """Test borrower can request a loan."""
    self.authenticate_borrower()  
    data = {
        'amount': 500,
        'term_in_months': 6
    }

    response = self.client.post('/LoanRequestView/', data)

    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(Loan.objects.count(), 1)
    loan = Loan.objects.first()
    self.assertEqual(loan.borrower, self.borrower)
    self.assertEqual(loan.amount, 500)
    self.assertEqual(loan.term_in_months, 6)

def test_lender_offer_loan(self):
    """Test lender can fund a loan."""
    loan = Loan.objects.create(borrower=self.borrower, amount=500, term_in_months=6)

    self.authenticate_lender()
    response = self.client.post(f'/OfferLoanView/{loan.id}/')

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    loan.refresh_from_db()

    self.assertEqual(loan.lender, self.lender)
    self.assertEqual(loan.status, 'funded')
    self.assertEqual(self.lender.balance, 5000 - loan.total_amount_due() - 3.75)
